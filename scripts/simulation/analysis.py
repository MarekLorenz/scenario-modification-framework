import csv
import json
from pathlib import Path

def compare_results():
    # Get the script directory and navigate to project root
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent.parent  # Go up two levels to reach project root
    
    print(f"Working from base directory: {base_dir}")
    
    # Load CSV data
    csv_path = base_dir / 'data/simulation_results/summary.csv'
    csv_dict = {}
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return
    
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
    json_path = base_dir / 'data/simulation_results/FINAL_all_scenarios_4o.json'
    
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return
    
    with open(json_path, 'r') as f:
        json_dict = json.load(f)
    
    print(f"Loaded JSON data from: {json_path}")
    print(json_dict)
    print(csv_dict)
    
    # Count matches
    matches = sum(1 for scenario in csv_dict if scenario in json_dict and json_dict[scenario]["critical_obstacle_id"] in csv_dict[scenario])
    # total = len(set(csv_dict.keys()) | set(json_dict.keys()))
    total = len(csv_dict)
    
    if total > 0:
        accuracy = (matches / total) * 100
        print(f"Accuracy: {accuracy:.2f}% ({matches}/{total} scenarios match)")
    else:
        print("No scenarios found to compare")

if __name__ == "__main__":
    compare_results()
