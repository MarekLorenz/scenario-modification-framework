import argparse
import json
import time
from llm_templates.critical_interval import find_critical_interval, parse_critical_interval_output
from llm_templates.critical_obstacles import find_critical_obstacles, parse_critical_obstacles_output
from mtl_converter.L1_converter import convert_l1_to_mtl
from mtl_converter.L4_converter import convert_l4_to_mtl_simplified, convert_l4_to_mtl, get_lanelets_for_obstacle
from mtl_converter.L7_converter import convert_l7_to_mtl_simplified, convert_l7_to_mtl, extract_ego_positions, get_ego_lanelets_in_interval
from mtl_converter.safety_metrics import process_single_scenario
from preprocessing.extract_trajectories import dynamic_obstacles_with_lanelets, extract_ego_trajectory, extract_every_nth_timestep
from preprocessing.layermodel import extract_important_information, assign_layers
from preprocessing.plot import lanelets_to_polygons
from preprocessing.xml2json import convert_single_xml_to_json
from scenario_modification.modify_scenario import modify_scenario
from scenario_modification.update_xml import parse_obstacle_data, update_xml_scenario
from output_analysis import visualize_dynamic_obstacles_with_time
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Process scenario name')
    parser.add_argument('-s', '--scenario', type=str, required=True,
                       help='REQUIRED: Scenario name (e.g. BEL_Antwerp-1_14_T-1)')
    parser.add_argument('-n', '--num_iterations', type=int, required=False, default=1,
                       help='OPTIONAL: Maximum number of iterations (default: 3)')
    parser.add_argument('-v', '--visualize', type=bool, required=False, default=False,
                       help='OPTIONAL: Visualize the dynamic obstacle trajectories before and after modification (default: False)')
    
    args = parser.parse_args()
    scenario_name = args.scenario
    num_iterations = args.num_iterations
    file = f'data/scenarios/{scenario_name}.xml'
    ego_trajectory_file = f"data/ego_trajectories/ego_trajectory_{scenario_name}.csv"
    modified_scenario = helper(file, scenario_name, ego_trajectory_file, num_iterations=num_iterations)
    print(f"Modified scenario: {modified_scenario}")

    if args.visualize:
        # Visualize the dynamic obstacles before and after modification
        visualize_dynamic_obstacles(file, scenario_name)
        visualize_dynamic_obstacles(modified_scenario, "updated_scenario")

def helper(scenario_filepath: str, scenario_name: str, ego_trajectory_filepath: str, previous_failed_reason: str = None, num_iterations: int = 1, n: int = 1):
    # Termination condition: maximum recursion depth = 3
    print(f"num_iterations: {num_iterations}")
    if n > num_iterations:
        return scenario_filepath
    
    print(f"Running modification for the {n}th time")
    interrupt = False
    convert_single_xml_to_json(scenario_filepath, 'data/json_scenarios')
    information_dict = extract_important_information(f'data/json_scenarios/{scenario_name}.json')

    layers = assign_layers(information_dict)

    # Extract individual layers
    L1 = layers["L1_RoadLevel"]
    L4 = layers["L4_MovableObjects"]
    # ego layer
    L7 = extract_ego_trajectory(ego_trajectory_filepath)

    # convert layers to mtl
    L4_mtl = convert_l4_to_mtl_simplified(L4, L1)
    L7_mtl = convert_l7_to_mtl_simplified(L7, L1)

    #  ==== generate the relative metrics CSV file ====
    # generate the dynamic obstacles csv file
    obstacle_csv_path = f'data/obstacles/{scenario_name}_dynamic_obstacles_with_lanelets.csv'
    polygons = lanelets_to_polygons(L1)
    dynamic_obstacles_with_lanelets(L4, polygons, obstacle_csv_path)
    obstacles_path = f'data/obstacles/{scenario_name}_dynamic_obstacles.csv'
    extract_every_nth_timestep(obstacle_csv_path, obstacles_path, n=1)

    relative_metrics_csv_file_path = f'data/scenarios/{scenario_name}_relative_metrics.csv'
    process_single_scenario(ego_trajectory_filepath, obstacles_path, scenario_name)
    
    # LLM Step 1: find the critical obstacles
    print(f"L4_mtl: {L4_mtl}")
    print(f"L7_mtl: {L7_mtl}")
    critical_obstacles = find_critical_obstacles(L4_mtl, L7_mtl)
    step_one_result = parse_critical_obstacles_output(critical_obstacles)
    print(f"Critical obstacles: {step_one_result.critical_obstacle_ids}")
    
    # LLM Step 2: find the critical interval
    ego_positions = extract_ego_positions(L7)
    L4_mtl, L4_lanelets_mentioned = convert_l4_to_mtl(L4, L1, step_one_result.critical_obstacle_ids, ego_positions, relative_metrics_csv_file_path)
    L7_mtl, L7_lanelets_mentioned = convert_l7_to_mtl(L7, L1)
    L1_mtl = convert_l1_to_mtl(L1, list(L4_lanelets_mentioned) + list(L7_lanelets_mentioned))

    print(f"L4_mtl: {L4_mtl}")
    critical_interval = find_critical_interval(L7_mtl, L4_mtl, L1_mtl)
    # Additional llm-based termination condition when a scenario is already very critical
    step_two_result = parse_critical_interval_output(critical_interval)
    # if step_two_result.has_collision:
    #     print("Interrupt signal received. Returning current scenario.")
    #     interrupt = True
    #     return scenario_filepath
    print(f"Step 2 result: {step_two_result}")
    #save simulation result for accuracy analysis
    save_simulation_result(scenario_name, step_two_result.critical_obstacle_id, step_two_result.has_collision)

        # LLM Step 3: Modify the scenario
        # start_time = step_two_result.critical_interval.start_time
        # end_time = step_two_result.critical_interval.end_time
        # dynamic_obstacle_lanelets = get_lanelets_for_obstacle(L4, L1, step_two_result.critical_obstacle_id, start_time, end_time)
        # ego_lanelets = get_ego_lanelets_in_interval(L7, L1, start_time, end_time)
        # altered_obstacle_data = modify_scenario(step_two_result, L1,  L4, L7, ego_lanelets, dynamic_obstacle_lanelets, previous_failed_reason)
        # parsed_obstacle_data = parse_obstacle_data(altered_obstacle_data)
        # print(f"Parsed obstacle data: {parsed_obstacle_data}")
        # update_xml_scenario(scenario_filepath, step_two_result.critical_obstacle_id, parsed_obstacle_data, "updated_scenario.xml", L1)

        # scenario_name = "updated_scenario"
        # output_file = f'updated_scenario.xml'

    # except Exception as e:
    #     print(f"Error occurred - Retrying: {e}")
    #     output_file = scenario_filepath
    #     # flow prompting loop with meta knowledge
    #     previous_failed_reason = e

    # finally:
    return scenario_filepath
        # if interrupt:
        #     return scenario_filepath
        # updated_n = n + 1
        # return helper(
        #     scenario_filepath=output_file,
        #     scenario_name=scenario_name, 
        #     ego_trajectory_filepath=ego_trajectory_filepath,
        #     n=updated_n,
        #     previous_failed_reason=previous_failed_reason,
        #     num_iterations=num_iterations)

def visualize_dynamic_obstacles(scenario_filepath: str, scenario_name: str):
    convert_single_xml_to_json(scenario_filepath, 'data/json_scenarios')
    information_dict = extract_important_information(f'data/json_scenarios/{scenario_name}.json')
    layers = assign_layers(information_dict)
    L4 = layers["L4_MovableObjects"]
    visualize_dynamic_obstacles_with_time(L4, show_plot=True)

def save_simulation_result(scenario_name: str, critical_obstacle_id: str, has_collision: bool):
    result_file = Path("data/simulation_results/all_scenarios_openai_slightly_modified.json")
    
    # Create directory if it doesn't exist
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing results or create new dict if file doesn't exist
    if result_file.exists():
        with open(result_file, "r") as f:
            result_dict = json.load(f)
    else:
        result_dict = {}
    
    result_dict[scenario_name] = {
        "critical_obstacle_id": critical_obstacle_id,
        "has_collision": has_collision
    }
    
    # Save back to file
    with open(result_file, "w") as f:
        json.dump(result_dict, f, indent=4)

if __name__ == "__main__":
     start_time = time.time()
     main()
     end_time = time.time()
     execution_time = end_time - start_time
     print(f"Time taken: {execution_time} seconds")
     
     # Write time to file
     with open('times', 'a') as f:
         f.write(f"{execution_time}\n")