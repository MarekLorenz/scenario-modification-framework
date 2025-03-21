import csv
import math

def time_to_collision(timestamp: float, obstacle_id: float, csv_file_path: str) -> float:
    # Allow slight floating point tolerance
    EPSILON = 1e-3
    
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Match row with floating point tolerance
            if (abs(float(row['timestep']) - timestamp) < EPSILON and
                abs(float(row['obstacle_id']) - obstacle_id) < EPSILON):
                
                # Get TTC values from CSV columns
                try:
                    ttc_long = float(row['ttc_long'])
                    ttc_lat = float(row['ttc_lat'])
                except ValueError:
                    return math.inf
                
                # Find minimum non-infinite TTC
                valid_ttcs = [ttc for ttc in [ttc_long, ttc_lat] 
                            if not math.isinf(ttc)]
                
                return min(valid_ttcs) if valid_ttcs else math.inf
    
    # No matching entry found
    return math.inf