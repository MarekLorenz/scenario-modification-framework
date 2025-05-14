from pathlib import Path
import shutil

def process_scenarios():
    """
    Process scenario files from collision scenarios and simulation logs.
    - Copies XML files from Dataset/collision_scenarios to data/scenarios
    - Copies logs.csv files to data/logs/scenario_name
    """
    # Base directory
    base_dir = Path('/Users/mareklorenz/Development/scenario-modification-framework')
    
    # Create output directories if they don't exist
    scenarios_dir = base_dir / 'data/scenarios'
    logs_dir = base_dir / 'data/logs'
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Process collision scenarios
    collision_dir = base_dir / 'Dataset/all_scenarios_combined'
    if not collision_dir.exists():
        print(f"Warning: All scenarios directory not found at {collision_dir}")
    else:
        # Recursively find all XML files
        for xml_file in collision_dir.rglob('*.xml'):
            # Create destination path
            dest_path = scenarios_dir / xml_file.name
            
            # Copy file, overwrite if exists
            shutil.copy2(xml_file, dest_path)
            print(f"Copied: {xml_file.name}")

    # Process simulation logs
    simulation_dir = base_dir / 'Dataset/Simulation_scenarios_with_FrenetixMotionPlanner'
    if not simulation_dir.exists():
        print(f"Warning: Simulation logs directory not found at {simulation_dir}")
    else:
        # Go through each scenario folder
        for scenario_folder in simulation_dir.iterdir():
            if scenario_folder.is_dir():
                logs_file = scenario_folder / 'logs.csv'
                if logs_file.exists():
                    # Create scenario-specific logs directory
                    scenario_logs_dir = logs_dir / scenario_folder.name
                    scenario_logs_dir.mkdir(exist_ok=True)
                    
                    # Copy logs file
                    dest_path = scenario_logs_dir / 'logs.csv'
                    shutil.copy2(logs_file, dest_path)
                    print(f"Copied logs for scenario: {scenario_folder.name}")

if __name__ == "__main__":
    process_scenarios()