import matplotlib.pyplot as plt

# Visualize Dynamic Obstacles
# Step 1: Extract the recorded trajectories for dynamic obstacles
def extract_obstacle_trajectories(data):
    """
    Extract the recorded trajectories for dynamic obstacles.
    Handles missing fields gracefully.
    """
    obstacle_trajectories = []

    for obstacle in data.get("dynamicObstacle", []):
        try:
            obstacle_id = obstacle.get("id", "Unknown")
            trajectory = obstacle.get("trajectory", [])
            
            if not isinstance(trajectory, list) or not trajectory:
                print(f"No recorded trajectory for obstacle {obstacle_id}")
                continue

            # Extract the trajectory data
            positions = [{"x": float(state["position"]["x"]), "y": float(state["position"]["y"])} for state in trajectory]
            times = [float(state["time"]) for state in trajectory]

            # Append data
            obstacle_trajectories.append({
                "id": obstacle_id,
                "positions": positions,
                "times": times,
            })
        except (KeyError, ValueError) as e:
            print(f"Skipping obstacle {obstacle_id} due to missing or invalid data: {e}")

    return obstacle_trajectories
# Step 2: Visualize the recorded trajectories for all dynamic obstacles
def visualize_dynamic_obstacles_with_time(obstacle_data, show_plot=True):
    # Extract the recorded trajectories of dynamic obstacles
    obstacle_trajectories = extract_obstacle_trajectories(obstacle_data)

    # Print information about the starting time and position
    for obstacle in obstacle_trajectories:
        positions = obstacle["positions"]
        times = obstacle["times"]

        # Extract x and y positions
        x_vals = [pos["x"] for pos in positions]
        y_vals = [pos["y"] for pos in positions]

        # Print the starting time and position
        #print(f"Obstacle {obstacle['id']} - Start Time: {times[0]}s, Start Position: ({x_vals[0]}, {y_vals[0]})")

    # Plot recorded trajectories if show_plot is True
    if show_plot:
        plt.figure(figsize=(10, 6))
        for obstacle in obstacle_trajectories:
            positions = obstacle["positions"]
            times = obstacle["times"]

            # Extract x and y positions
            x_vals = [pos["x"] for pos in positions]
            y_vals = [pos["y"] for pos in positions]

            # Plot trajectory
            plt.plot(x_vals, y_vals, label=f"Obstacle {obstacle['id']}")
            plt.scatter(x_vals[0], y_vals[0], label=f"Start {obstacle['id']} (t={times[0]:.2f}s)", zorder=5)

        # Improve visualization
        plt.xlabel("X Position (m)")
        plt.ylabel("Y Position (m)")
        plt.title("Dynamic Obstacles Recorded Trajectories with Time Information")
        plt.legend()
        plt.grid(True)
        plt.axis("equal")
        plt.show()

