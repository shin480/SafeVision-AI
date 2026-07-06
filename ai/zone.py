def get_center(bbox):
    x1, y1, x2, y2 = bbox

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    return center_x, center_y


def is_in_danger_zone(center_x, center_y, danger_zone):
    zone_x1, zone_y1, zone_x2, zone_y2 = danger_zone

    if zone_x1 <= center_x <= zone_x2 and zone_y1 <= center_y <= zone_y2:
        return True

    return False