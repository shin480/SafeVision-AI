def get_center(bbox):
    """
    YOLO bbox 중심점 계산
    bbox = (x1, y1, x2, y2)
    """

    x1, y1, x2, y2 = bbox

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    return center_x, center_y


def normalize_zone(zone):
    """
    프론트에서 넘어온 위험구역 좌표 정리
    zone = {
        "x1": 100,
        "y1": 80,
        "x2": 500,
        "y2": 350
    }

    드래그 방향이 반대여도 정상 처리
    """

    x1 = int(zone["x1"])
    y1 = int(zone["y1"])
    x2 = int(zone["x2"])
    y2 = int(zone["y2"])

    return {
        "x1": min(x1, x2),
        "y1": min(y1, y2),
        "x2": max(x1, x2),
        "y2": max(y1, y2)
    }


def is_in_danger_zone(center_x, center_y, danger_zone):
    """
    중심점이 위험구역 내부에 있는지 판단
    """

    zone = normalize_zone(danger_zone)

    return (
        zone["x1"] <= center_x <= zone["x2"]
        and zone["y1"] <= center_y <= zone["y2"]
    )


def check_danger_zone_violation(bbox, danger_zone):
    """
    bbox 중심점이 위험구역 안에 있으면 True 반환
    """

    center_x, center_y = get_center(bbox)

    return is_in_danger_zone(center_x, center_y, danger_zone)


def create_danger_zone_event(camera_id, bbox, danger_zone):
    """
    위험구역 침입 이벤트 생성
    DB 저장 전 임시 이벤트 데이터
    """

    center_x, center_y = get_center(bbox)

    event = {
        "camera_id": camera_id,
        "event_type": "DANGER_ZONE",
        "severity": "WARNING",
        "message": "위험구역 침입 감지",
        "bbox": {
            "x1": bbox[0],
            "y1": bbox[1],
            "x2": bbox[2],
            "y2": bbox[3]
        },
        "center": {
            "x": center_x,
            "y": center_y
        },
        "danger_zone": normalize_zone(danger_zone)
    }

    return event


def check_and_create_event(camera_id, bbox, danger_zone):
    """
    침입 여부 판단 후, 침입이면 이벤트 생성
    침입 아니면 None 반환
    """

    if check_danger_zone_violation(bbox, danger_zone):
        return create_danger_zone_event(camera_id, bbox, danger_zone)

    return None