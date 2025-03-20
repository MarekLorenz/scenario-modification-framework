import json
from llm_templates.llm_utils import send_gemini_request
from generation_types.generation import StepTwoGenerationResult, TimeInterval

def find_critical_interval(L7_mtl, L4_mtl, L1_mtl):
    # Gefahrenstufe für jedes Dynamic Obstacle definieren -> als Indikator um Loop zu unterbrechen
    system_prompt = f"""
Important: Do not return any code, but just find the result through thinking.
Find the critical section for the ego car in the following traffic scenario (without returning code):
For the obstacles, they are specified as follows:
<obstacle_id>: G[<start_time>, <end_time>]: <lanelet_id>, G[<start_time>, <end_time>]: <lanelet_id>, ...
...

For the ego vehicle, it is specified as follows:
<ego_id>: G[<start_time>, <end_time>]: <lanelet_id>, G[<start_time>, <end_time>]: <lanelet_id>, ...

Return the one most critical time interval where the ego vehicle might collide with a dynamic obstacle. 
Also return the lanelet where it happens and the dynamic obstacle that is involved.

Write down the following json after your analysis. Only give me one dictionary, DO NOT WRITE ANY CODE OR PROGRAM:
{{
    "critical_obstacle_id": "<string: id of the dynamic obstacle that is most likely to collide with the ego vehicle>",
    "critical_interval_start_time": <int: start time of the critical interval>,
    "critical_interval_end_time": <int: end time of the critical interval>,
    "critical_lanelet_id": "<string: lanelet id where the collision might happen>"
}}

Do not include any other text in your response, only the tuple that is the most critical.
If you think the scenario is already severly safety-critical or a collision of the ego vehicle is likely, return "interrupt".
"""
    user_prompt = f"""
EGO VEHICLE MOVEMENTS:
{"\n".join(L7_mtl)}

DYNAMIC OBSTACLES:
{"\n".join(L4_mtl)}

This is very important: Start answering with ```json 
{{
    "critical_obstacle_id":
"""
    response = send_gemini_request(system_prompt, user_prompt)
    return response

def parse_critical_interval_output(output: str) -> StepTwoGenerationResult:
    """
    Parse the output of the critical interval generation
    """
    output = output.replace("```json", "").replace("```", "")
    output = output.strip()
    output_dict = json.loads(output)
    time_interval = TimeInterval(
        start_time=output_dict["critical_interval_start_time"],
        end_time=output_dict["critical_interval_end_time"]
    )
    return StepTwoGenerationResult(
        critical_obstacle_id=output_dict["critical_obstacle_id"],
        critical_interval=time_interval,
        critical_lanelet_id=output_dict["critical_lanelet_id"]
    )