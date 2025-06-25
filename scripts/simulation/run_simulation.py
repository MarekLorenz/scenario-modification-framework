from pathlib import Path
import shutil
import subprocess

def run_simulations(output_dir, n_iterations=5):
    """
    Run generate_ego_trajectory and main.py for each scenario in data/scenarios
    Run each scenario n_iterations times and save separately
    """
    # Get the script directory and navigate to project root
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent.parent  # Go up two levels to reach project root
    scenarios_dir = base_dir / 'data/scenarios'
    
    # Get all XML files in scenarios directory
    scenario_files = sorted(list(scenarios_dir.glob('*.xml')))[8:]
    total_scenarios = len(scenario_files)

    print(f"Found {total_scenarios} scenarios to process")
    print(f"Each scenario will be run {n_iterations} times")
    print(f"Working from base directory: {base_dir}")
    
    # Create output directory for multiple iterations
    dest_dir = base_dir / f'{output_dir}'
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"Results will be saved to: {dest_dir}")
    
    # Process each scenario
    for i, scenario_file in enumerate(scenario_files, 1):
        scenario_name = scenario_file.stem  # Get filename without extension
        print(f"\nProcessing scenario {i}/{total_scenarios}: {scenario_name}")
        
        # Run each scenario n_iterations times
        for iteration in range(1, n_iterations + 1):
            print(f"  Iteration {iteration}/{n_iterations}")
            
            try:
                # Change to base directory to run scripts
                original_cwd = Path.cwd()
                subprocess.run(['python', str(base_dir / 'generate_ego_trajectory.py'), '-s', scenario_name], 
                             check=True, cwd=base_dir)
                
                # Then run main simulation
                print(f"    Running main simulation for {scenario_name} (iteration {iteration})")
                subprocess.run(['python', str(base_dir / 'main.py'), '-s', scenario_name], 
                             check=True, cwd=base_dir)

                # Check if updated_scenario.xml exists before copying
                updated_src = base_dir / 'updated_scenario.xml'
                if not updated_src.exists():
                    print(f"    Error: {updated_src} does not exist after simulation for {scenario_name} iteration {iteration}")
                else:
                    # Create filename with iteration number
                    updated_dest = dest_dir / f"updated_{scenario_name}_iter_{iteration}.xml"
                    
                    # Overwrite the existing file if it exists
                    if updated_dest.exists():
                        updated_dest.unlink()
                    
                    shutil.copy(updated_src, updated_dest)
                    print(f"    Saved iteration {iteration} to {updated_dest.name}")

                print(f"    Successfully completed iteration {iteration} for {scenario_name}")
                
            except subprocess.CalledProcessError as e:
                print(f"    Error in iteration {iteration} for scenario {scenario_name}: {e}")
                continue
            
        print(f"Completed all {n_iterations} iterations for {scenario_name}")

    print(f"\nAll scenarios processed! Results saved in {dest_dir}")
    
    # Print summary statistics
    total_files = len(list(dest_dir.glob('*.xml')))
    expected_files = total_scenarios * n_iterations
    print(f"Generated {total_files}/{expected_files} files")

if __name__ == "__main__":
    output_dir = "updated_files_multiple_iterations_5x"
    n_iterations = 5
    run_simulations(output_dir, n_iterations)
