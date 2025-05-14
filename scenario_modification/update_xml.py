import json
import xml.etree.ElementTree as ET
from typing import List, Dict
from pathlib import Path

from mtl_converter.utils import is_within_lanelet


def parse_obstacle_data(json_str: str) -> list[dict]:
    """
    Parses a JSON string containing obstacle trajectory data
    
    Args:
        json_str: String containing JSON array of trajectory points
        
    Returns:
        List of trajectory point dictionaries
    """
    json_str = json_str.replace("```", "")
    start_index = json_str.find('[')
    if start_index == -1:
        json_str = "[\n" + json_str + "\n]"
        start_index = 0
    json_str = json_str[start_index:]
    print(f"JSON str: {json_str}")
    try:
        # Attempt to parse the JSON
        data = json.loads(json_str)
        if not isinstance(data, list):
            raise ValueError("Expected JSON array at root level")
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def update_xml_scenario(original_path: str,
                       obstacle_id: str,
                       updated_data: List[Dict],
                       output_path: str = None,
                       L1: dict = None) -> None:
    """
    Updates XML scenario with proper type handling for numeric values
    """
    tree = ET.parse(original_path)
    root = tree.getroot()

    updated_times = [str(point_data.get('time', '')) for point_data in updated_data]
    print(f"Updated times: {updated_times}")

    # Find obstacle
    for obstacle in root.findall('.//dynamicObstacle'):
        if obstacle.get('id') == obstacle_id:
            trajectory = obstacle.find('trajectory')
            if trajectory is None:
                trajectory = ET.SubElement(obstacle, 'trajectory')
            else:
                # Remove existing states with matching timestamps
                for state in trajectory.findall('state'):
                    time_elem = state.find('time/exact')
                    if time_elem is not None and time_elem.text in updated_times:
                        trajectory.remove(state)
            
            # Add new state elements with string conversion
            for point_data in updated_data:
                state = ET.SubElement(trajectory, 'state')
                
                # Convert all values to strings
                time_str = str(point_data.get('time', ''))
                x_str = f"{point_data['position']['x']:.4f}" if isinstance(point_data['position']['x'], float) else str(point_data['position']['x'])
                x_float = float(x_str)
                y_str = f"{point_data['position']['y']:.4f}" if isinstance(point_data['position']['y'], float) else str(point_data['position']['y'])
                y_float = float(y_str)
                orient_str = f"{point_data['orientation']:.4f}" if isinstance(point_data['orientation'], float) else str(point_data['orientation'])
                velocity_str = f"{point_data['velocity']:.4f}" if isinstance(point_data['velocity'], float) else str(point_data['velocity'])
                accel_str = f"{point_data['acceleration']:.4f}" if isinstance(point_data['acceleration'], float) else str(point_data['acceleration'])

                # ====== possibilities for unfeasible trajectories ======
                # - returning to a previously visited lanelet
                # - driving off the road
                # - driving in the wrong direction @TODO
                point_is_within_lanelet = False
                lanelets_visited = []  # Change to list to maintain order

                for lanelet in L1['lanelet']:
                    position = {"x": x_float,
                               "y": y_float}
                    if is_within_lanelet(position, lanelet):
                        point_is_within_lanelet = True
                        current_lanelet = lanelet['id']
                        
                        # Check if we're trying to return to a previously visited lanelet
                        if current_lanelet in lanelets_visited[:-1]:  # Allow last lanelet in sequence
                            raise RuntimeError(f"Dynamic obstacle {obstacle_id} returned to a previously visited lanelet: {current_lanelet}")
                            
                        # Only add if it's different from the last visited lanelet
                        if not lanelets_visited or lanelets_visited[-1] != current_lanelet:
                            lanelets_visited.append(current_lanelet)
                        break
                
                if not point_is_within_lanelet:
                    raise RuntimeError(f"Modified position not inside lanelet: {position}")
                # Time
                time_elem = ET.SubElement(state, 'time')
                ET.SubElement(time_elem, 'exact').text = time_str
                
                # Position
                pos_elem = ET.SubElement(state, 'position')
                pos_point = ET.SubElement(pos_elem, 'point')
                ET.SubElement(pos_point, 'x').text = x_str
                ET.SubElement(pos_point, 'y').text = y_str
                
                # Orientation
                orient_elem = ET.SubElement(state, 'orientation')
                ET.SubElement(orient_elem, 'exact').text = orient_str
                
                # Velocity
                velocity_elem = ET.SubElement(state, 'velocity')
                ET.SubElement(velocity_elem, 'exact').text = velocity_str
                
                # Acceleration
                accel_elem = ET.SubElement(state, 'acceleration')
                ET.SubElement(accel_elem, 'exact').text = accel_str
            
            # Sort all states by time
            states = trajectory.findall('state')
            states.sort(key=lambda s: float(s.findtext('time/exact', '0')))
            
            # Clear and re-add sorted states
            for state in list(trajectory.findall('state')):
                trajectory.remove(state)
            for state in states:
                trajectory.append(state)

            # Handle output path
            if not output_path:
                orig_path = Path(original_path)
                output_path = orig_path.parent / f"{orig_path.stem}_modified.xml"
            
            # Write with proper encoding
            tree.write(output_path, 
                      encoding='utf-8', 
                      xml_declaration=True,
                      method='xml')
            print(f"Scenario successfully updated: {output_path}")
            return
    
    raise ValueError(f"Obstacle {obstacle_id} not found in scenario")