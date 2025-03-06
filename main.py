import argparse
from llm_templates.critical_obstacles import find_critical_obstacles
from mtl_converter.L4_converter import convert_l4_to_mtl_simplified
from mtl_converter.L7_converter import convert_l7_to_mtl
from preprocessing.extract_trajectories import extract_ego_trajectory
from preprocessing.plot import lanelets_to_polygons
from preprocessing.layermodel import extract_important_information, assign_layers
from preprocessing.xml2json import convert_single_xml_to_json

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
    L7_mtl = convert_l7_to_mtl(L7, L1)

    critical_obstacles = find_critical_obstacles(L4_mtl, L7_mtl)
    print(f"Critical obstacles: {critical_obstacles}")

if __name__ == "__main__":
    main()