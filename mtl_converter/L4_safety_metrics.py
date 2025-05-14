import csv
import math

LATERAL = "lateral"
LONGITUDINAL = "longitudinal"

class TTC_Evaluation:
    def __init__(self, direction_type: str, ttc_long: float, ttc_lat: float, direction: str):
        self.direction_type = direction_type
        self.ttc_long = ttc_long
        self.ttc_lat = ttc_lat
        self.direction = direction

def time_to_collision(timestamp: float, obstacle_id: float, csv_file_path: str) -> TTC_Evaluation:
    # Allow slight floating point tolerance
    EPSILON = 1e-3
    
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Match row with floating point tolerance
            if (abs(float(row['timestep']) - timestamp) < EPSILON and
                abs(float(row['obstacle_id']) - obstacle_id) < EPSILON):
                
                direction = row['motion_description']
                longitudinal_direction_type = direction.split('.')[0]
                lateral_direction_type = direction.split('.')[1]
                # Get TTC values from CSV columns
                try:
                    ttc_long = float(row['ttc_long']) if "toward" in longitudinal_direction_type or "alignment" in longitudinal_direction_type else math.inf
                    ttc_lat = float(row['ttc_lat']) if "toward" in lateral_direction_type or "alignment" in lateral_direction_type else math.inf
                except ValueError:
                    return TTC_Evaluation(LATERAL, ttc_long, ttc_lat, direction)
                
                # Find minimum non-infinite TTC
                if ttc_long < ttc_lat:
                    return TTC_Evaluation(LONGITUDINAL, ttc_long, ttc_lat, direction)
                else:
                    return TTC_Evaluation(LATERAL, ttc_lat, ttc_long, direction)
    
    # No matching entry found
    return TTC_Evaluation(LATERAL, math.inf, math.inf, "")