import json
from llm_templates.llm_utils import send_gemini_request, get_consistency_params
from mtl_converter.L1_converter import get_adjacent_lanelets
from generation_types.generation import StepTwoGenerationResult, TimeInterval

def modify_scenario(step_two_result: StepTwoGenerationResult, L1: dict, L4: dict, L7: dict, ego_lanelets: list[int], dynamic_obstacle_lanelets: list[int], previous_failed_reason: str = None):
    obstacle_id = step_two_result.critical_obstacle_id
    critical_interval = step_two_result.critical_interval
    obstacle_timestamps = find_obstacle_timestamps(obstacle_id, critical_interval, L4)
    obstacle_timestamps_after_critical_interval = find_obstacle_timestamps_after_critical_interval(obstacle_id, critical_interval, L4)
    ego_timestamps = find_ego_timestamps(L7, critical_interval)

    system_prompt = f"""You are a JSON output engine.
Adjust the trajectory of the dynamic obstacle in the critical time interval to make it more safety-critical, 
so that the dynamic obstacle is more likely to produce a collision with the ego vehicle.

Alter the data for the dynamic obstacle and give me the full updated data in the same format. DO NOT WRITE ANY CODE.

Only adjust the data explicitly. It is not your task to write a program or generalize.

Only give me the data for the dynamic obstacle, not the ego vehicle. The ego vehicle data is not changeable.
IMPORTANT: DO NOT PROVIDE CODE or any further text.
{f"DO NOT REPEAT YOUR PREVIOUS MISTAKES. Your previous attempt failed because of the following reason: {previous_failed_reason}. Especially do not use the same point if it is not inside a lanelet." if previous_failed_reason else ""}
"""

    dynamic_obstacle_lanelet_info = ""
    for lanelet in dynamic_obstacle_lanelets:
        adjacent_lanelets = get_adjacent_lanelets(lanelet, L1)
        dynamic_obstacle_lanelet_info += json.dumps(adjacent_lanelets)
        dynamic_obstacle_lanelet_info += "\n"

    ego_lanelet_info = ""
    for lanelet in ego_lanelets:
        adjacent_lanelets = get_adjacent_lanelets(lanelet, L1)
        ego_lanelet_info += json.dumps(adjacent_lanelets)
        ego_lanelet_info += "\n"

    print(f"Dynamic obstacle lanelet info: {dynamic_obstacle_lanelet_info}")
    print(f"Ego lanelet info: {ego_lanelet_info}")
    user_prompt = f"""
Road Network information:
Lanelets of the dynamic obstacle:
[{',\n'.join([json.dumps(x) for x in dynamic_obstacle_lanelets])}]

Lanelets of the ego vehicle:
[{',\n'.join([json.dumps(x) for x in ego_lanelets])}]

Ego vehicle trajectory:
[{',\n'.join([json.dumps(x) for x in ego_timestamps])}]

Try to achieve a smooth trajectory for the dynamic obstacle, in the end it should transition back into the original trajectory that comes after the critical interval.
Dynamic obstacle trajectory after the critical interval:
[{',\n'.join([json.dumps(x) for x in obstacle_timestamps_after_critical_interval])}]

Dynamic obstacle trajectory (to be adjusted by you):
[{',\n'.join([json.dumps(x) for x in obstacle_timestamps])}]

This is very important: Start answering with ```json [...
"""
    
    response = send_gemini_request(system_prompt, user_prompt, **get_consistency_params())
    print("Step 3: ", response)
    return response

def find_obstacle_timestamps(obstacle_id: str, time_interval: TimeInterval, L4: dict):
        obstacle_timestamps = []
        # find the obstacle in the data
        for obstacle in L4['dynamicObstacle']:
            if obstacle['id'] == obstacle_id:
                timestamps = obstacle['trajectory']
                for timestamp in timestamps:
                    if int(timestamp['time']) >= int(time_interval.start_time) and int(timestamp['time']) <= int(time_interval.end_time):
                        obstacle_timestamps.append(timestamp)
        return obstacle_timestamps

def find_obstacle_timestamps_after_critical_interval(obstacle_id: str, time_interval: TimeInterval, L4: dict):
        obstacle_timestamps = []
        # find the obstacle in the data
        for obstacle in L4['dynamicObstacle']:
            if obstacle['id'] == obstacle_id:
                timestamps = obstacle['trajectory']
                for timestamp in timestamps:
                    if int(timestamp['time']) >= int(time_interval.end_time) and int(timestamp['time']) <= int(time_interval.end_time) + 5:
                        obstacle_timestamps.append(timestamp)
        return obstacle_timestamps

def find_ego_timestamps(L7: dict, time_interval: TimeInterval):
    ego_timestamps = []
    for timestamp in L7:
        if int(timestamp['timestep']) >= int(time_interval.start_time) and int(timestamp['timestep']) <= int(time_interval.end_time):
            ego_timestamps.append(timestamp)
    return ego_timestamps