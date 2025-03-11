import argparse
from llm_templates.critical_interval import find_critical_interval
from llm_templates.critical_obstacles import find_critical_obstacles
from mtl_converter.L1_converter import convert_l1_to_mtl
from mtl_converter.L4_converter import convert_l4_to_mtl_simplified, convert_l4_to_mtl
from mtl_converter.L7_converter import convert_l7_to_mtl_simplified, convert_l7_to_mtl, extract_ego_positions
from preprocessing.extract_trajectories import extract_ego_trajectory
from preprocessing.plot import lanelets_to_polygons
from preprocessing.layermodel import extract_important_information, assign_layers
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
    convert_single_xml_to_json(file, 'data/json_scenarios')
    information_dict = extract_important_information(f'data/json_scenarios/{scenario_name}.json')

    layers = assign_layers(information_dict)

    # Extract individual layers
    L1 = layers["L1_RoadLevel"]
    L2 = layers["L2_TrafficInfrastructure"]
    L3 = layers["L3_TemporalModifications"]
    L4 = layers["L4_MovableObjects"]
    L5 = layers["L5_EnvironmentalConditions"]
    L6 = layers["L6_DigitalInformation"]

    # Convert lanelets to polygons
    polygons = lanelets_to_polygons(L1)

    # ego layer
    L7 = extract_ego_trajectory(ego_trajectory_file)

    # convert layers to mtl
    L4_mtl = convert_l4_to_mtl_simplified(L4, L1)
    L7_mtl = convert_l7_to_mtl_simplified(L7, L1)

    # LLM Step 1
    critical_obstacles = find_critical_obstacles(L4_mtl, L7_mtl)
    critical_obstacles_list = [
        obstacle.strip().replace('"', '').replace("'", '')
        for obstacle in critical_obstacles.replace("[", "").replace("]", "").split(",")
    ]
    print(f"Critical obstacles: {critical_obstacles_list}")

    # LLM Step 2
    ego_positions = extract_ego_positions(L7)
    L4_mtl, L4_lanelets_mentioned = convert_l4_to_mtl(L4, L1, critical_obstacles_list, ego_positions)
    L7_mtl, L7_lanelets_mentioned = convert_l7_to_mtl(L7, L1)
    L1_mtl = convert_l1_to_mtl(L1, list(L4_lanelets_mentioned) + list(L7_lanelets_mentioned))

    critical_interval = find_critical_interval(L7_mtl, L4_mtl, L1_mtl)
    critical_interval_list = critical_interval.replace("(", "").replace(")", "").replace("[", "").replace("]", "").split(",")
    critical_interval_list = [x.strip() for x in critical_interval_list]
    print(f"Critical interval: {critical_interval_list}")

    # LLM Step 3: Modify the scenario
    altered_obstacle_data = modify_scenario(critical_interval_list[0], (critical_interval_list[1], critical_interval_list[2]), critical_interval_list[3], L4, L7)
    parsed_obstacle_data = parse_obstacle_data(altered_obstacle_data)
    print(f"Parsed obstacle data: {parsed_obstacle_data}")
    update_xml_scenario(f'data/scenarios/{scenario_name}.xml', critical_interval_list[0], parsed_obstacle_data, "updated_scenario.xml")
    
    # Visualize original scenario
    visualize_dynamic_obstacles_with_time(L4, show_plot=True)

    # Visualize updated scenario
    scenario_name = "updated_scenario"
    file = f'updated_scenario.xml'
    convert_single_xml_to_json(file, 'data/json_scenarios')
    information_dict = extract_important_information(f'data/json_scenarios/{scenario_name}.json')
    layers = assign_layers(information_dict)
    L4 = layers["L4_MovableObjects"]

    visualize_dynamic_obstacles_with_time(L4, show_plot=True)


if __name__ == "__main__":
    main()