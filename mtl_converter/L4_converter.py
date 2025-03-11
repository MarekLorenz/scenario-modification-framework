# requires L1 for lanelet information
from mtl_converter.utils import is_within_lanelet

def convert_l4_to_mtl(L4: dict, L1: dict, critical_obstacles: list[str], ego_positions: list[dict]) -> tuple[list[str], set[str]]:
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
        start_time = None
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
                if current_lanelet is not None:
                    movable_objects_mtl.append(f"G_[{start_time}, {time}]: occupy({dynamic_obstacle['id']}, {current_lanelet})")
                    lanelets_mentioned.add(current_lanelet)

                # Calculate distance only on entry to new lanelet
                if idx < len(ego_positions):
                    ego_pos = ego_positions[idx]
                    distance = _euclidean_distance(position, ego_pos)
                    movable_objects_mtl.append(f"G[{start_time}, {start_time}] Distance ego to {dynamic_obstacle['id']}: {distance:.2f}m")

                current_lanelet = found_lanelet
                start_time = time

        if current_lanelet is not None:
            movable_objects_mtl.append(f"G_[{start_time}, {time}]: occupy({dynamic_obstacle['id']}, {current_lanelet})")
            lanelets_mentioned.add(current_lanelet)

    return movable_objects_mtl, lanelets_mentioned

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

def _euclidean_distance(pos1: dict, pos2: dict) -> float:
    """Calculate Euclidean distance between two positions"""
    return ((float(pos1['x']) - float(pos2['x']))**2 + (float(pos1['y']) - float(pos2['y']))**2)**0.5