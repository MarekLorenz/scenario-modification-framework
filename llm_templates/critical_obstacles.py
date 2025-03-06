from llm_templates.llm_utils import send_local_llama_request

def find_critical_obstacles(L4_mtl, L7_mtl):
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
    The output should be a list of five obstacle ids, like this:
    [
        "obstacle_id_1",
        ...
        "obstacle_id_5"
    ]
    Do not include any other text in your response.
    """

    user_prompt = f"""
    Here is the scenario description:

    Here are the MTL specifications:
    Obstacles: 
    {L4_mtl}

    Ego car: 
    {L7_mtl}
    """

    print(f"Sending request to LLM")
    response = send_local_llama_request(system_prompt, user_prompt)

    return response
