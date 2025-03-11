import json
from llm_templates.llm_utils import send_local_llama_request

def modify_scenario(obstacle_id: str, critical_interval: tuple[int, int], lanelet_id: str, L4: dict, L7: dict):
    obstacle_timestamps = find_obstacle_timestamps(obstacle_id, critical_interval, L4)
    ego_timestamps = find_ego_timestamps(L7, critical_interval)

    system_prompt = """Adjust the trajectory of the dynamic obstacle to make it more safety-critical, 
so that the dynamic obstacle is more likely to produce a collision with the ego vehicle.

Alter the data for the dynamic obstacle and give me the new data in the same format. DO NOT WRITE ANY CODE.

Only adjust the data. It is not your task to write a program or generalize.
Do not include any other text than the altered json data.

Only give me the data for the dynamic obstacle, not the ego vehicle. The ego vehicle data is not changeable.
IMPORTANT: DO NOT PROVIDE CODE or any further text.
"""

    user_prompt = f"""
Ego vehicle trajectory:
[{',\n'.join([json.dumps(x) for x in ego_timestamps])}]

Dynamic obstacle trajectory (to be adjusted by you):
[{',\n'.join([json.dumps(x) for x in obstacle_timestamps])}]
"""

    return send_local_llama_request(system_prompt, user_prompt)

def find_obstacle_timestamps(obstacle_id: str, critical_interval: tuple[int, int], L4: dict):
        obstacle_timestamps = []
        # find the obstacle in the data
        for obstacle in L4['dynamicObstacle']:
            if obstacle['id'] == obstacle_id:
                timestamps = obstacle['trajectory']
                for timestamp in timestamps:
                    if int(timestamp['time']) >= int(critical_interval[0]) and int(timestamp['time']) <= int(critical_interval[1]):
                        obstacle_timestamps.append(timestamp)
        return obstacle_timestamps


def find_ego_timestamps(L7: dict, critical_interval: tuple[int, int]):
    ego_timestamps = []
    for timestamp in L7:
        if int(timestamp['timestep']) >= int(critical_interval[0]) and int(timestamp['timestep']) <= int(critical_interval[1]):
            ego_timestamps.append(timestamp)
    return ego_timestamps