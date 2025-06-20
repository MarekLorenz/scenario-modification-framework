import json
from llm_templates.llm_utils import send_gemini_request, send_openai_request, get_consistency_params
from generation_types.generation import StepOneGenerationResult

def find_critical_obstacles(L4_mtl, L7_mtl) -> str:
    """
    Find critical obstacles in the scenario
    """
    system_prompt = f"""
    You are an expert in identifying critical obstacles for the ego vehicle in a traffic scenario. You are given a scenario description.
    The format specifies the lanelets that are occupied by the dynamic obstacles and the ego vehicle in metric temporal logic.

    For the obstacles, they are specified as follows:
    <obstacle_id>: G[<start_time>, <end_time>]: <lanelet_id>, G[<start_time>, <end_time>]: <lanelet_id>, ...
    ...

    For the ego vehicle, it is specified as follows:
    <ego_id>: G[<start_time>, <end_time>]: <lanelet_id>, G[<start_time>, <end_time>]: <lanelet_id>, ...
 
    Your task is to identify the critical obstacles in the scenario that might lead to a collision with the ego vehicle. Return a list of obstacle ids that are critical.
    The output should be a dictionary with the key "critical_obstacle_ids" and a list of five obstacle ids, like this:

    {{
        "critical_obstacle_ids": [
            "obstacle_id_1",
            ...
            "obstacle_id_5"
        ]
    }}

    Do not include any other text in your response, only the list.
    """

    ablation_study = False
    user_prompt = f"""
    {f'''Write down the following json after your analysis. Only give me one dictionary containing the list of five (5) critical obstacle ids. DO NOT WRITE ANY CODE OR PROGRAM:
    {{
        "critical_obstacle_ids": [
            "obstacle_id_1",
            ...
            "obstacle_id_5"
        ]
    }}''' if ablation_study else ""}
Here is the scenario description:

Here are the MTL specifications:
Obstacles: 
{L4_mtl}

Ego car: 
{L7_mtl}
This is important: Start your response with ```json
{{
    "critical_obstacle_ids": [
}}

"""

    response = send_openai_request(system_prompt, user_prompt, **get_consistency_params())

    return response

def parse_critical_obstacles_output(output: str) -> StepOneGenerationResult:
    """
    Parse the output of the critical obstacles generation
    """
    output = output.replace("```json", "").replace("```", "")
    output = output.strip()
    output_dict = json.loads(output)
    return StepOneGenerationResult(critical_obstacle_ids=output_dict["critical_obstacle_ids"])