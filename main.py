import argparse
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
from scenario_modification.update_xml import parse_obstacle_data
from output_analysis import visualize_dynamic_obstacles_with_time
from scenario_modification.update_xml import update_xml_scenario

def main():
    parser = argparse.ArgumentParser(description='Process scenario name')
    parser.add_argument('-s', '--scenario', type=str, required=True,
                       help='Scenario name (e.g. BEL_Antwerp-1_14_T-1)')
    
    args = parser.parse_args()
    scenario_name = args.scenario
    file = f'data/scenarios/{scenario_name}.xml'
    ego_trajectory_file = f"data/ego_trajectories/ego_trajectory_{scenario_name}.csv"
    modified_scenario = helper(file, scenario_name, ego_trajectory_file)
    print(f"Modified scenario: {modified_scenario}")

    # Visualize the dynamic obstacles before and after modification
    visualize_dynamic_obstacles(file, scenario_name)
    visualize_dynamic_obstacles(modified_scenario, "updated_scenario")

def helper(scenario_filepath: str, scenario_name: str, ego_trajectory_filepath: str, n=1, previous_failed_reason: str = None):
    # Termination condition: maximum recursion depth = 3
    if n > 3:
        return scenario_filepath
    
    print(f"Running modification for the {n}th time")
    interrupt = False
    try:
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
        # Additional llm-based termination condition
        if "interrupt" in critical_interval.lower():
            print("Interrupt signal received. Returning current scenario.")
            interrupt = True
            return scenario_filepath
        step_two_result = parse_critical_interval_output(critical_interval)
        print(f"Step 2 result: {step_two_result}")

        # LLM Step 3: Modify the scenario
        start_time = step_two_result.critical_interval.start_time
        end_time = step_two_result.critical_interval.end_time
        dynamic_obstacle_lanelets = get_lanelets_for_obstacle(L4, L1, step_two_result.critical_obstacle_id, start_time, end_time)
        ego_lanelets = get_ego_lanelets_in_interval(L7, L1, start_time, end_time)
        altered_obstacle_data = modify_scenario(step_two_result, L1,  L4, L7, ego_lanelets, dynamic_obstacle_lanelets, previous_failed_reason)
        parsed_obstacle_data = parse_obstacle_data(altered_obstacle_data)
        print(f"Parsed obstacle data: {parsed_obstacle_data}")
        update_xml_scenario(scenario_filepath, step_two_result.critical_obstacle_id, parsed_obstacle_data, "updated_scenario.xml", L1)

        scenario_name = "updated_scenario"
        output_file = f'updated_scenario.xml'

    except Exception as e:
        print(f"Error occurred - Retrying: {e}")
        output_file = scenario_filepath
        # flow prompting loop with meta knowledge
        previous_failed_reason = e

    finally:
        if interrupt:
            return scenario_filepath
        updated_n = n + 1
        return helper(
            scenario_filepath=output_file,
            scenario_name=scenario_name, 
            ego_trajectory_filepath=ego_trajectory_filepath,
            n=updated_n,
            previous_failed_reason=previous_failed_reason)

def visualize_dynamic_obstacles(scenario_filepath: str, scenario_name: str):
    convert_single_xml_to_json(scenario_filepath, 'data/json_scenarios')
    information_dict = extract_important_information(f'data/json_scenarios/{scenario_name}.json')
    layers = assign_layers(information_dict)
    L4 = layers["L4_MovableObjects"]
    visualize_dynamic_obstacles_with_time(L4, show_plot=True)

if __name__ == "__main__":
    main()