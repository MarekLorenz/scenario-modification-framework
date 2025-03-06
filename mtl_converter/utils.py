def is_within_lanelet(position, lanelet):
    # Assuming lanelet has 'leftBound' and 'rightBound' with 'x' and 'y' coordinates
    # Use a ray-casting algorithm for point-in-polygon test
    def point_in_polygon(x, y, polygon):
        num = len(polygon)
        j = num - 1
        inside = False
        for i in range(num):
            xi, yi = float(polygon[i]['x']), float(polygon[i]['y'])
            xj, yj = float(polygon[j]['x']), float(polygon[j]['y'])
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    # Combine left and right bounds to form a polygon
    polygon = lanelet['leftBound'] + lanelet['rightBound'][::-1]

    # Check if position is within the polygon
    return point_in_polygon(float(position['x']), float(position['y']), polygon)