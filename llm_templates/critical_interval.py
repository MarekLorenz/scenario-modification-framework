import json
from llm_templates.llm_utils import get_consistency_params, send_gemini_request, send_openai_request
from generation_types.generation import StepTwoGenerationResult, TimeInterval

INTERRUPT_PROMPT = """
Important note: Before proceeding, check if the ego vehicle is already in danger.
If so, only reply with "interrupt". The scenario is already very critical and does not require further adaptation.
"""

def find_critical_interval(L7_mtl, L4_mtl, L1_mtl):
    system_prompt = f"""
Important: Do not return any code, but just find the result through thinking.
Decide if the ego car in a given scenario is involved in a collision. If so, set the "has_collision" flag to true.
Be precise and check if the longitudinal TTC_longitudinal as well as the lateral TTC_lateral are both 0.0 or close to 0.0 (i.e. 0.07). The euclidean distance between the ego vehicle and the dynamic obstacle should be small, only consider this if the TTC_longitudinal and TTC_lateral are not very close to 0.0.
If both conditions are met, set the "has_collision" flag to true.

You are given statements in metric temporal logic format. The operator G[<start_time>, <end_time>] specifies a statement that is true for the entire time interval [<start_time>, <end_time>].
The operator F[<start_time>, <end_time>] specifies a statement that is true for at least one point in the time interval [<start_time>, <end_time>].

Find the critical section for the ego car in the following traffic scenario (without returning code):
For the obstacles, they are specified as follows:
G[start_time, start_time]: occupy(obstacle_id, lanelet_id)
F[start_time, start_time]: TTC_longitudinal = <time to collision value of the obstacle and the ego vehicle> AND TTC_lateral = <time to collision value of the obstacle and the ego vehicle> AND DTC = <euclidean distance between the obstacle and the ego vehicle>
G[<start_time>, <end_time>]: occupy...
...

For the ego vehicle, it is specified as follows:
<ego_id>: G[<start_time>, <end_time>]: <lanelet_id>, G[<start_time>, <end_time>]: <lanelet_id>, ...

Return the one most critical time interval where the ego vehicle might collide with a dynamic obstacle. If there is no such obstacle, return the one with the highest risk level. Never return None or anything else other than an id for the critical obstacle.
Also return the lanelet where it happens and the dynamic obstacle that is involved.

Write down the following json after your analysis. Only give me one dictionary, DO NOT WRITE ANY CODE OR PROGRAM:
{{
    "critical_obstacle_id": "<string: id of the dynamic obstacle that is most likely to collide with the ego vehicle or the one with the highest risk level>",
    "critical_interval_start_time": <int: start time of the critical interval>,
    "critical_interval_end_time": <int: end time of the critical interval>,
    "critical_lanelet_id": "<string: lanelet id where the collision might happen>",
    "has_collision": <bool: true, if the data is indicating a collision (meaning both TTC_long and TTC_lat are close to 0.0), false otherwise. If no TTC is specified, set to false.>
}}

Do not include any other text in your response, only the tuple that is the most critical.
{INTERRUPT_PROMPT}
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
    response = send_openai_request(system_prompt, user_prompt, **get_consistency_params())
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
        critical_lanelet_id=output_dict["critical_lanelet_id"],
        has_collision=output_dict["has_collision"]
    )