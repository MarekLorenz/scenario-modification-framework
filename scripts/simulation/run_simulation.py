from pathlib import Path
import subprocess

def run_simulations():
    """
    Run generate_ego_trajectory and main.py for each scenario in data/scenarios
    """
    base_dir = Path('/Users/mareklorenz/Development/scenario-modification-framework')
    scenarios_dir = base_dir / 'data/scenarios'
    
    # Get all XML files in scenarios directory
    scenario_files = list(scenarios_dir.glob('*.xml'))
    total_scenarios = len(scenario_files)
    
    print(f"Found {total_scenarios} scenarios to process")
    
    # Process each scenario
    for i, scenario_file in enumerate(scenario_files, 1):
        scenario_name = scenario_file.stem  # Get filename without extension
        print(f"\nProcessing scenario {i}/{total_scenarios}: {scenario_name}")
        
        try:
            # First generate ego trajectory
            print(f"Generating ego trajectory for {scenario_name}")
            subprocess.run(['python', 'generate_ego_trajectory.py', '-s', scenario_name], check=True)
            
            # Then run main simulation
            print(f"Running main simulation for {scenario_name}")
            subprocess.run(['python', 'main.py', '-s', scenario_name], check=True)
            
            print(f"Successfully processed {scenario_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing scenario {scenario_name}: {e}")
            continue

if __name__ == "__main__":
    run_simulations()
