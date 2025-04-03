import csv
import json
from pathlib import Path

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
            obstacle_id = collision_id if collision_id and collision_id.lower() != 'none' else extreme_risk_id
            if obstacle_id and obstacle_id.lower() != 'none':
                csv_dict[scenario_name] = obstacle_id
    
    # Load JSON data
    json_path = Path('/Users/mareklorenz/Development/scenario-modification-framework/data/simulation_results/result.json')
    with open(json_path, 'r') as f:
        json_dict = json.load(f)
    
    # Count matches
    matches = sum(1 for scenario in csv_dict if scenario in json_dict and csv_dict[scenario] == json_dict[scenario])
    total = len(set(csv_dict.keys()) | set(json_dict.keys()))
    
    accuracy = (matches / total) * 100
    print(f"Accuracy: {accuracy:.2f}% ({matches}/{total} scenarios match)")

if __name__ == "__main__":
    compare_results()
