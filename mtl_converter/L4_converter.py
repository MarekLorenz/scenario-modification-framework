# requires L1 for lanelet information
import math
from mtl_converter.L4_safety_metrics import TTC_Evaluation, time_to_collision
from mtl_converter.utils import is_within_lanelet

def convert_l4_to_mtl(L4: dict, L1: dict, critical_obstacles: list[str], ego_positions: list[dict], relative_metrics_csv_file_path: str) -> tuple[list[str], set[str]]:

    """
    Convert Layer 4 (dynamic obstacles) scenario to MTL scenario
    Returns tuple containing:
    - List of MTL formulas
    - Set of all mentioned lanelet IDs
    """
    movable_objects_mtl = []
    lanelets_mentioned = set()

    for dynamic_obstacle in [x for x in L4['dynamicObstacle'] if x['id'] in critical_obstacles]:
        current_lanelet = None
        start_time = 0
        
        # Find first lanelet before starting the loop
        first_position = dynamic_obstacle['trajectory'][0]['position']
        for lanelet in L1['lanelet']:
            if is_within_lanelet(first_position, lanelet):
                current_lanelet = lanelet['id']
                break
        
        for idx, timestamp in enumerate(dynamic_obstacle['trajectory']):
            position = timestamp['position']
            
            time = timestamp['time']
            found_lanelet = None
            
            # Find current lanelet
            for lanelet in L1['lanelet']:
                if is_within_lanelet(position, lanelet):
                    found_lanelet = lanelet['id']
                    break

            if found_lanelet != current_lanelet:
                if current_lanelet is not None:  # Only output if we had a valid lanelet
                    movable_objects_mtl.append(f"G_[{start_time}, {time}]: occupy({dynamic_obstacle['id']}, {current_lanelet})")
                    lanelets_mentioned.add(current_lanelet)

                    # Calculate minimum TTC for the entire duration in the lanelet
                    min_ttc = math.inf, math.inf # long, lat
                    min_ttc_timestamp = start_time
                    min_distance = math.inf

                    for t in range(int(start_time), int(time) + 1):
                        ttc_evaluation: TTC_Evaluation = time_to_collision(timestamp=float(t),
                                                      obstacle_id=float(dynamic_obstacle['id']), 
                                                      csv_file_path=relative_metrics_csv_file_path)
                        current_ttc_long, current_ttc_lat = ttc_evaluation.ttc_long, ttc_evaluation.ttc_lat
                        current_distance = euclidean_distance(position, ego_positions[int(t)]) if not int(t) >= len(ego_positions) else math.inf

                        if (current_ttc_long < 10 and current_ttc_lat < 10):
                            min_ttc = current_ttc_long, current_ttc_lat
                            min_ttc_timestamp = t
                            min_distance = current_distance
                    distance = euclidean_distance(position, ego_positions[int(min_ttc_timestamp)]) if not int(min_ttc_timestamp) >= len(ego_positions) else math.inf
                    if min_ttc[0] != math.inf:
                        movable_objects_mtl.append(f"F[{start_time}, {time}]: min_TTC_longitudinal = {min_ttc[0]}s AND min_TTC_lateral = {min_ttc[1]}s AND DTC = {distance}m")
                
                current_lanelet = found_lanelet
                start_time = time

        # Add the final lanelet occupation
        if current_lanelet is not None:
            movable_objects_mtl.append(f"G_[{start_time}, {time}]: occupy({dynamic_obstacle['id']}, {current_lanelet})")
            lanelets_mentioned.add(current_lanelet)
            
            # Calculate minimum TTC for the final lanelet
            min_ttc = math.inf, math.inf # long, lat
            min_ttc_timestamp = start_time
            min_distance = math.inf

            for t in range(int(start_time), int(time) + 1):
                ttc_evaluation: TTC_Evaluation = time_to_collision(timestamp=float(t),
                                                obstacle_id=float(dynamic_obstacle['id']), 
                                                csv_file_path=relative_metrics_csv_file_path)
                direction_type = ttc_evaluation.direction_type
                current_ttc_long, current_ttc_lat = ttc_evaluation.ttc_long, ttc_evaluation.ttc_lat
                current_distance = euclidean_distance(position, ego_positions[int(t)]) if not int(t) >= len(ego_positions) else math.inf

                if (current_ttc_long < 1 and current_ttc_lat < 1) and (current_ttc_long + current_ttc_lat < min_ttc[0] + min_ttc[1] 
                                                or (current_ttc_long + current_ttc_lat == min_ttc[0] + min_ttc[1] and current_distance < min_distance)):
                    min_ttc = current_ttc_long, current_ttc_lat
                    min_ttc_timestamp = t
                    min_distance = current_distance
                
            distance = euclidean_distance(position, ego_positions[int(min_ttc_timestamp)]) if not int(min_ttc_timestamp) >= len(ego_positions) else math.inf
            if min_ttc[0] != math.inf:
                movable_objects_mtl.append(f"F[{start_time}, {time}]: min_TTC_longitudinal = {min_ttc[0]}s AND min_TTC_lateral = {min_ttc[1]}s AND DTC = {distance}m")
        
    return movable_objects_mtl, lanelets_mentioned

def euclidean_distance(pos1: dict, pos2: dict) -> float:
    """Calculate Euclidean distance between two positions"""
    return ((float(pos1['x']) - float(pos2['x']))**2 + (float(pos1['y']) - float(pos2['y']))**2)**0.5

def convert_l4_to_mtl_simplified(L4: dict, L1: dict) -> list[str]:
    """
    Convert Layer 4 (dynamic obstacles) scenario to simplified MTL summary
    """
    obstacle_summaries = []
    
    for obstacle in L4.get('dynamicObstacle', []):
        current_lanelet = None
        intervals = []
        start_time = None
        
        for state in obstacle['trajectory']:
            time = state['time']
            position = state['position']
            
            # Find current lanelet
            found_lanelet = next((l['id'] for l in L1['lanelet'] if is_within_lanelet(position, l)), None)

            # Track lanelet changes
            if found_lanelet != current_lanelet:
                if current_lanelet is not None:  # Record previous interval
                    intervals.append(f"G[{start_time}, {time}]: {current_lanelet}")
                current_lanelet = found_lanelet
                start_time = time
        
        # Add final interval if lanelet occupied at end
        if current_lanelet is not None:
            intervals.append(f"G[{start_time}, {time}]: {current_lanelet}")
        
        # Format obstacle summary
        if intervals:
            obstacle_summaries.append(
                f"{obstacle['id']}: " + ", ".join(intervals)
            )
    
    return "\n".join(obstacle_summaries)

def get_lanelets_for_obstacle(
    L4: dict,
    L1: dict,
    obstacle_id: str,
    start_time: float,
    end_time: float
) -> list[int]:
    """
    Get all lanelets occupied by a specific obstacle during time interval.
    
    Args:
        L4: Layer 4 data with dynamic obstacles
        L1: Layer 1 lanelet data
        obstacle_id: Target obstacle ID to analyze
        start_time: Interval start (inclusive)
        end_time: Interval end (inclusive)
    
    Returns:
        Sorted list of unique lanelet IDs occupied during interval
    """
    occupied = set()
    
    # Find target obstacle
    obstacle = next(
        (obs for obs in L4.get('dynamicObstacle', []) 
         if obs['id'] == obstacle_id),
        None
    )
    
    if not obstacle:
        return []
    
    # Check trajectory points in time window
    for state in obstacle['trajectory']:
        if start_time <= int(state['time']) <= end_time:
            lanelet_id = next(
                (l['id'] for l in L1['lanelet'] 
                 if is_within_lanelet(state['position'], l)),
                None
            )
            if lanelet_id:
                occupied.add(lanelet_id)
    
    return occupied

def calculate_ttb(obstacle_velocity: float, max_deceleration: float = 7.0) -> float:
    """
    Calculate Time To Brake (TTB) for an obstacle
    
    Args:
        obstacle_velocity: Current velocity of the obstacle in m/s
        max_deceleration: Maximum deceleration capability in m/s^2 (default 7.0 m/s^2)
    
    Returns:
        Time to brake in seconds
    """
    if obstacle_velocity <= 0:
        return 0
    return obstacle_velocity / max_deceleration

def _get_safety_zone(dynamic_obstacle_timestamp: dict, ego_position) -> list[dict]:
    # on a scale from 1 to 5 - how risky is the obstacle for the ego vehicle 
    obstacle_position = dynamic_obstacle_timestamp['position']
    obstacle_velocity = float(dynamic_obstacle_timestamp['velocity'])
    
    # Calculate distance between ego and obstacle
    distance = euclidean_distance(ego_position, obstacle_position)
    # calculate time to brake
    ttb = calculate_ttb(obstacle_velocity)
    
    # Define distance thresholds (in meters)
    CRITICAL_DISTANCE = 10  # Very close
    SAFE_DISTANCE = 50     # Reasonably safe distance
    
    # Normalize distance factor (1 when very close, 0 when far)
    distance_factor = max(0, min(1, (SAFE_DISTANCE - distance) / (SAFE_DISTANCE - CRITICAL_DISTANCE)))
    
    if ttb > 0:
        # Combine TTB and distance into risk factor
        # Both factors contribute equally to the risk
        ttb_factor = 1 - math.exp(-ttb/2)
        combined_risk = (ttb_factor + distance_factor) / 2
        
        # Higher weight to distance when very close
        if distance < CRITICAL_DISTANCE:
            combined_risk = 0.7 * distance_factor + 0.3 * ttb_factor
            
        risk_level = max(1, min(5, math.ceil(combined_risk * 5)))
    else:
        # Even for stationary obstacles, consider distance
        risk_level = max(1, min(3, math.ceil(distance_factor * 3)))
    
    return risk_level