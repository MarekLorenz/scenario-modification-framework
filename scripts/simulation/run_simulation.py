from pathlib import Path
import shutil
import subprocess

def run_simulations():
    """
    Run generate_ego_trajectory and main.py for each scenario in data/scenarios
    """
    base_dir = Path('/Users/mareklorenz/Development/scenario-modification-framework')
    scenarios_dir = base_dir / 'data/scenarios'
    
    # Get all XML files in scenarios directory
    scenario_files = sorted(list(scenarios_dir.glob('*.xml')))[8:]
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

            # Check if updated_scenario.xml exists before copying
            updated_src = Path('updated_scenario.xml')
            if not updated_src.exists():
                print(f"Error: {updated_src} does not exist after simulation for {scenario_name}")
            else:
                dest_dir = base_dir / 'updated_files_4o'
                dest_dir.mkdir(parents=True, exist_ok=True)
                updated_dest = dest_dir / f"updated_{scenario_name}.xml"
                # Overwrite the existing file if it exists
                if updated_dest.exists():
                    updated_dest.unlink()
                shutil.copy(updated_src, updated_dest)
                print(f"Copied updated_scenario.xml to {updated_dest}")

            print(f"Successfully processed {scenario_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing scenario {scenario_name}: {e}")
            continue

if __name__ == "__main__":
    run_simulations()
