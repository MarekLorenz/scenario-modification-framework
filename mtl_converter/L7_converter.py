from mtl_converter.utils import is_within_lanelet

def convert_l7_to_mtl(L7: dict, L1: dict) -> tuple[list[str], set[str]]:
    """
    Convert Layer 7 (Ego Layer) scenario to MTL scenario
    Returns tuple containing:
    - List of MTL formulas
    - Set of all mentioned lanelet IDs
    """
    ego_mtl = []
    lanelets_mentioned = set()
    current_lanelet = None
    start_time = None

    for timestamp in L7:
        position = {'x': timestamp['x'], 'y': timestamp['y']}
        time = timestamp['timestep']
        found_lanelet = None

        for lanelet in L1['lanelet']:
            if is_within_lanelet(position, lanelet):
                found_lanelet = lanelet['id']
                break

        if found_lanelet != current_lanelet:
            if current_lanelet is not None:
                ego_mtl.append(f"G_[{start_time}, {time}]: occupy(EGO, {current_lanelet})")
                lanelets_mentioned.add(current_lanelet)
                # ego_mtl.append(f"Position on lanelet entry: G_[{start_time}, {start_time}]: {position}")
            current_lanelet = found_lanelet
            start_time = time

    if current_lanelet is not None:
        ego_mtl.append(f"G_[{start_time}, {time}]: occupy(EGO, {current_lanelet})")
        lanelets_mentioned.add(current_lanelet)
        # ego_mtl.append(f"Position on lanelet exit: G_[{start_time}, {start_time}]: {position}")

    return ego_mtl, lanelets_mentioned

def convert_l7_to_mtl_simplified(L7: dict, L1: dict) -> list[str]:
    """
    Convert Layer 7 (Ego Layer) scenario to MTL scenario
    """
    ego_mtl = []
    current_lanelet = None
    start_time = None

    for timestamp in L7:
        position = {'x': timestamp['x'], 'y': timestamp['y']}
        time = timestamp['timestep']
        found_lanelet = None

        for lanelet in L1['lanelet']:
            if is_within_lanelet(position, lanelet):
                found_lanelet = lanelet['id']
                break

        if found_lanelet != current_lanelet:
            if current_lanelet is not None:
                # Add the interval for the previous lanelet to the list
                ego_mtl.append(f"G_[{start_time}, {time}]: occupy(EGO, {current_lanelet})")
                # Add the position of the dynamic obstacle to the list
            # Update the current lanelet, start time, and entry orientation
            current_lanelet = found_lanelet
            start_time = time

    # Add the last interval if the obstacle was on a lanelet
    if current_lanelet is not None:
        ego_mtl.append(f"G_[{start_time}, {time}]: occupy(EGO, {current_lanelet})")
    return ego_mtl

def extract_ego_positions(L7: dict) -> list[dict]:
    """
    Extract ego vehicle positions from Layer 7 data
    Returns list of position dictionaries with x/y coordinates
    """
    return [
        {'x': timestamp['x'], 'y': timestamp['y']}
        for timestamp in L7
    ]