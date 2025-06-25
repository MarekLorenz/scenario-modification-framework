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
    # Get the script directory and navigate to project root
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent.parent  # Go up two levels to reach project root
    
    print(f"Working from base directory: {base_dir}")
    
    # Load CSV data
    csv_path = base_dir / 'data/simulation_results/summary.csv'
    csv_dict = {}
    
    if not csv_path.exists():
        print(f"Warning: CSV file not found at {csv_path}")
        csv_dict = {}
    else:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                scenario_name = row['Scenario_Name']
                collision_id = row['CollisionObstacleID']
                extreme_risk_id = row['ExtremeRiskObstacleID']
                obstacle_id = [collision_id, extreme_risk_id]
                csv_dict[scenario_name] = obstacle_id
        print(f"Loaded CSV data from: {csv_path}")
    
    # Load JSON data
    json_path = base_dir / 'data/simulation_results/all_scenarios_4_5_revalidation.json'
    
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return
    
    with open(json_path, 'r') as f:
        json_dict = json.load(f)
    
    print(f"Loaded JSON data from: {json_path}")
    print(json_dict)

    # Use relative paths for dataset directories
    success_scenarios_dir = base_dir / 'Dataset/success_scenarios'
    collision_scenarios_dir = base_dir / 'Dataset/collision_scenarios'
    
    if not success_scenarios_dir.exists():
        print(f"Warning: Success scenarios directory not found at {success_scenarios_dir}")
        non_collision = []
    else:
        non_collision = get_scenario_names(success_scenarios_dir)
    
    if not collision_scenarios_dir.exists():
        print(f"Warning: Collision scenarios directory not found at {collision_scenarios_dir}")
        collision = []
    else:
        collision = get_scenario_names(collision_scenarios_dir)

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
    
    # Print summary
    total_scenarios = len(non_collision) + len(collision)
    total_correct = len(collision_correct) + len(non_collision_correct)
    if total_scenarios > 0:
        accuracy = (total_correct / total_scenarios) * 100
        print(f"\nOverall accuracy: {accuracy:.2f}% ({total_correct}/{total_scenarios})")

if __name__ == "__main__":
    compare_results()
