import argparse
import os

from preprocessing.extract_trajectories import extract_ego_every_nth_timestep
from preprocessing.layermodel import extract_important_information, assign_layers
from preprocessing.plot import lanelets_to_polygons, visualize_and_save_ego_trajectory_with_lanelets
from preprocessing.xml2json import convert_single_xml_to_json


def main():
    parser = argparse.ArgumentParser(description='Process scenario name')
    parser.add_argument('-s', '--scenario', type=str, required=True,
                       help='Scenario name (e.g. BEL_Antwerp-1_14_T-1)')
    
    args = parser.parse_args()
    scenario_name = args.scenario
    scenario_filepath = f'data/scenarios/{scenario_name}.xml'
    input_csv_path = f'data/logs/{scenario_name}/logs.csv'

    # Ensure the output directory exists
    scenario_output_dir = f'data/ego_trajectories/{scenario_name}'
    convert_single_xml_to_json(scenario_filepath, 'data/json_scenarios')
    information_dict = extract_important_information(f'data/json_scenarios/{scenario_name}.json')

    layers = assign_layers(information_dict)

    L1 = layers["L1_RoadLevel"]
    L7 = layers["L7_PlanningProblem"]
    polygons = lanelets_to_polygons(L1)

    os.makedirs(scenario_output_dir, exist_ok=True)
    output_csv_path = f'data/ego_trajectories/ego_trajectory_positions_with_lanelets_{scenario_name}.csv'

    visualize_and_save_ego_trajectory_with_lanelets(input_csv_path, output_csv_path, polygons, L7, show_plot=False)

    # file that will be used for simulation

    ego_path = f'data/ego_trajectories/ego_trajectory_{scenario_name}.csv'
    extract_ego_every_nth_timestep(output_csv_path, ego_path,n=1)

if __name__ == "__main__":
    main()