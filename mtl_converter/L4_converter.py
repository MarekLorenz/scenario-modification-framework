# requires L1 for lanelet information
from mtl_converter.utils import is_within_lanelet

def convert_l4_to_mtl(L4: dict, L1: dict) -> list[str]:
    """
    Convert Layer 4 (dynamic obstacles) scenario to MTL scenario
    """
    movable_objects_mtl = []

    for dynamic_obstacle in [x for x in L4['dynamicObstacle']]:
        current_lanelet = None
        start_time = None
        for timestamp in dynamic_obstacle['trajectory']:
            position = timestamp['position']
            time = timestamp['time']
            found_lanelet = None
            for lanelet in L1['lanelet']:
                if is_within_lanelet(position, lanelet):
                    found_lanelet = lanelet['id']
                    break
            if found_lanelet != current_lanelet:
                if current_lanelet is not None:
                    # Add the interval for the previous lanelet to the list
                    movable_objects_mtl.append(f"G_[{start_time}, {time}]: occupy({dynamic_obstacle['id']}, {current_lanelet})")
                # Update the current lanelet, start time, and entry orientation
                current_lanelet = found_lanelet
                start_time = time

        # Add the last interval if the obstacle was on a lanelet
        if current_lanelet is not None:
            movable_objects_mtl.append(f"G_[{start_time}, {time}]: occupy({dynamic_obstacle['id']}, {current_lanelet})")

    return movable_objects_mtl

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
            found_lanelet = next((l['id'] for l in L1['lanelet'] 
                                if is_within_lanelet(position, l)), None)
            
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