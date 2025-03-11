from llm_templates.llm_utils import send_local_llama_request

def find_critical_interval(L7_mtl, L4_mtl, L1_mtl):
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

Write down the following tuple after your analysis. Only give me one tuple, DO NOT WRITE ANY CODE OR PROGRAM:
(
    <id of the dynamic obstacle that is most likely to collide with the ego vehicle>,
    <critical time interval, i.e. [start_time, end_time]>,
    <lanelet id where the collision might happen>
)

Do not include any other text in your response, only the tuple that is the most critical.
"""
    user_prompt = f"""
EGO VEHICLE MOVEMENTS:
{"\n".join(L7_mtl)}

DYNAMIC OBSTACLES:
{"\n".join(L4_mtl)}
"""
    response = send_local_llama_request(system_prompt, user_prompt)
    return response