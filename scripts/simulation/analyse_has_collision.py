import csv
import json
import os
from pathlib import Path


def get_scenario_names(directory):
    # Get all files in directory
    files = os.listdir(directory)
    # Filter for .xml files and remove the .xml extension
    return [os.path.splitext(f)[0] for f in files if f.endswith('.xml')]


def compare_results():
    # Load CSV data
    csv_path = Path('/Users/mareklorenz/Development/scenario-modification-framework/data/simulation_results/summary.csv')
    csv_dict = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario_name = row['Scenario_Name']
            collision_id = row['CollisionObstacleID']
            extreme_risk_id = row['ExtremeRiskObstacleID']
            obstacle_id = [collision_id, extreme_risk_id]
            csv_dict[scenario_name] = obstacle_id
    
    # Load JSON data
    json_path = Path('/Users/mareklorenz/Development/scenario-modification-framework/data/simulation_results/all_scenarios_4_5_revalidation.json')
    with open(json_path, 'r') as f:
        json_dict = json.load(f)
    
    print(json_dict)

    non_collision = get_scenario_names('Dataset/success_scenarios')
    collision = get_scenario_names('Dataset/collision_scenarios')

    print("Non-collision scenarios:", len(non_collision))
    print("Collision scenarios:", len(collision))

    collision_correct = []
    collision_incorrect = []
    non_collision_correct = []
    non_collision_incorrect = []
    error_scenarios = []

    for scenario in non_collision:
        if scenario in json_dict and json_dict[scenario]["has_collision"] == False:
            non_collision_correct.append(scenario)
        elif scenario not in json_dict:
            non_collision_incorrect.append(scenario)
            error_scenarios.append(scenario)
        else:
            non_collision_incorrect.append(scenario)

    for scenario in collision:
        if scenario in json_dict and json_dict[scenario]["has_collision"] == True:
            collision_correct.append(scenario)
        elif scenario not in json_dict:
            collision_incorrect.append(scenario)
            error_scenarios.append(scenario)
        else:
            collision_incorrect.append(scenario)
    print("Collision correct:", len(collision_correct))
    print("Collision incorrect:", len(collision_incorrect))
    print("Non-collision correct:", len(non_collision_correct))
    print("Non-collision incorrect:", len(non_collision_incorrect))
    print("Error scenarios:", len(error_scenarios))

if __name__ == "__main__":
    compare_results()
