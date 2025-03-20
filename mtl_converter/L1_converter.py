def convert_l1_to_mtl(L1: dict, lanelet_ids: list[str]) -> list[dict]:
    """
    Returns adjacency information for specified lanelets in a road network
    """
    lanelet_id_map = {l['id']: l for l in L1['lanelet']}
    
    result = []
    for lid in lanelet_ids:
        if lid not in lanelet_id_map:
            continue
            
        lanelet = lanelet_id_map[lid]
        adjacency_dict = {'lanelet_id': lid}
        
        # Add relationships only if they exist
        for relation in ['adjacentLeft', 'adjacentRight', 'successor', 'predecessor']:
            if value := lanelet.get(relation):
                adjacency_dict[relation] = value
        
        result.append(adjacency_dict)
    
    return result

def get_adjacent_lanelets(lanelet_id, L1):
    l = None
    for lanelet in L1['lanelet']:
        if lanelet['id'] == lanelet_id:
            l = lanelet
            break
    
    if not l:
        return {}
    
    result = {'lanelet_id': lanelet_id}
    if 'adjacentLeft' in l.keys():
        adj_left = l.get('adjacentLeft')
        result['adjacentLeft'] = adj_left

    if 'adjacentRight' in l:
        adj_right = l['adjacentRight']
        result['adjacentRight'] = adj_right

    if 'successor' in l:
        successor = l['successor']
        result['successor'] = successor

    if 'predecessor' in l:
        predecessor = l['predecessor']
        result['predecessor'] = predecessor

    return result