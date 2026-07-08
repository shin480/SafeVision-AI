from pathlib import Path
from ultralytics import YOLO
import cv2
from collections import Counter
import time

from ai.risk import calculate_risk
from ai.capture import get_capture_path_if_needed
from backend.event_log.getEventLogs import save_event_with_capture, save_detection_log

from sqlalchemy import text
from backend.util.db import get_engine


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ai" / "models" / "weights" / "ppe100.pt"

# YOLO 모델 한 번만 로드
model = YOLO(str(MODEL_PATH))

# 실시간 모니터링 화면에 보여줄 최신 감지 상태 저장
latest_detection_status = {}

# detection_log가 프레임마다 과도하게 쌓이지 않도록 저장 간격 제한
DETECTION_LOG_COOLDOWN = 5
last_detection_log_time = {}


# YOLO 감지 결과를 JSON 형태로 정리하는 함수
def extract_detection_result(results, model):
    boxes = results[0].boxes

    # 감지된 객체가 없을 때 기본값 반환
    if boxes is None or len(boxes) == 0:
        return {
            "person": 0,
            "helmet": 0,
            "no_helmet": 0,
            "safety_vest": 0,
            "no_safety_vest": 0
        }

    # 감지된 클래스 ID 추출
    class_ids = boxes.cls.tolist()

    # 클래스 ID를 클래스명으로 변환
    class_names = [model.names[int(cls_id)] for cls_id in class_ids]

    # 클래스별 개수 계산
    counts = Counter(class_names)

    return {
        "person": counts.get("person", 0),
        "helmet": counts.get("helmet", 0),
        "no_helmet": counts.get("no_helmet", 0),
        "safety_vest": counts.get("safety_vest", 0),
        "no_safety_vest": counts.get("no_safety_vest", 0)
    }


# CCTV별 저장된 위험구역 좌표 조회
def get_danger_zones(cctv_id):
    db = get_engine()

    try:
        sql = text("""
            SELECT zone_id, zone_name, x1, y1, x2, y2
            FROM danger_zone
            WHERE cctv_id = :cctv_id
              AND is_active = 1
        """)

        rows = db.execute(sql, {"cctv_id": cctv_id}).mappings().all()
        return [dict(row) for row in rows]

    finally:
        db.close()


# 감지된 객체의 중심점이 위험구역 안에 들어왔는지 확인
def check_danger_zone_intrusion(results, model, danger_zones):
    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return False

    target_classes = [
        "person",
        "helmet",
        "no_helmet",
        "safety_vest",
        "no_safety_vest"
    ]

    for box in boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]

        if class_name not in target_classes:
            continue

        x1, y1, x2, y2 = box.xyxy[0]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        # 감지 박스의 중심점 계산
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        for zone in danger_zones:
            zx1 = min(zone["x1"], zone["x2"])
            zy1 = min(zone["y1"], zone["y2"])
            zx2 = max(zone["x1"], zone["x2"])
            zy2 = max(zone["y1"], zone["y2"])

            if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                return True

    return False


# 감지 결과를 바탕으로 위험도 점수와 등급 추가
def add_risk_result(detection_result, in_danger_zone=False):
    no_helmet = detection_result["no_helmet"] > 0
    no_safety_vest = detection_result["no_safety_vest"] > 0

    risk_score, risk_status = calculate_risk(
        no_helmet=no_helmet,
        no_safety_vest=no_safety_vest,
        in_danger_zone=in_danger_zone
    )

    detection_result["in_danger_zone"] = in_danger_zone
    detection_result["risk_score"] = risk_score
    detection_result["risk_status"] = risk_status

    return detection_result


# 감지 결과를 DB와 화면에 표시할 위반 유형 문자열로 변환
def make_violation_type(detection_result):
    no_helmet = detection_result.get("no_helmet", 0) > 0
    no_safety_vest = detection_result.get("no_safety_vest", 0) > 0
    in_danger_zone = detection_result.get("in_danger_zone")

    violation_types = []

    if no_helmet and no_safety_vest:
        violation_types.append("PPE 미착용")
    elif no_helmet:
        violation_types.append("안전모 미착용")
    elif no_safety_vest:
        violation_types.append("안전조끼 미착용")

    if in_danger_zone:
        violation_types.append("위험구역 진입")

    if not violation_types:
        return "NONE"

    return " + ".join(violation_types)


# 위험도 결과에 따라 캡처 이미지를 저장하고 경로 정보를 detection_result에 추가
def save_capture_if_needed(capture_frame, cctv_id, detection_result):
    risk_status = detection_result["risk_status"]
    violation_type = make_violation_type(detection_result)

    capture_path = get_capture_path_if_needed(
        cctv_id=cctv_id,
        violation_type=violation_type,
        status=risk_status
    )

    if capture_path:
        cv2.imwrite(capture_path, capture_frame)

        # 백엔드 저장 경로
        detection_result["capture_path"] = capture_path

        # 프론트 이미지 src에서 사용할 경로
        detection_result["capture_url"] = "/" + capture_path.replace("\\", "/")
    else:
        detection_result["capture_path"] = None
        detection_result["capture_url"] = None

    detection_result["violation_type"] = violation_type

    return detection_result


# CCTV별 detection_log 저장 간격 체크
def should_save_detection_log(cctv_id):
    now = time.time()
    last_time = last_detection_log_time.get(cctv_id, 0)

    if now - last_time >= DETECTION_LOG_COOLDOWN:
        last_detection_log_time[cctv_id] = now
        return True

    return False


# 서버에 카메라 프레임을 전송하고, 감지/위험판단/DB저장을 처리
def generate_frames(camera_index, cctv_id, conf=0.5):
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(f"카메라{camera_index} 열기 실패")

    while True:
        success, frame = cap.read()

        if not success:
            break

        # YOLO 객체 감지 수행
        results = model(frame, conf=conf)

        # 저장된 위험구역 조회 후 진입 여부 판단
        danger_zones = get_danger_zones(cctv_id)
        in_danger_zone = check_danger_zone_intrusion(results, model, danger_zones)

        # 감지 결과 정리 + 위험도 계산
        detection_result = extract_detection_result(results, model)
        detection_result = add_risk_result(
            detection_result,
            in_danger_zone=in_danger_zone
        )

        # YOLO 박스가 표시된 프레임 생성
        annotated = results[0].plot()

        print("현재 CCTV ID:", cctv_id)
        print("위험구역 조회 결과:", danger_zones)
        print("위험구역 진입 여부:", in_danger_zone)

        # 화면에 위험구역 사각형 표시
        for zone in danger_zones:
            cv2.rectangle(
                annotated,
                (zone["x1"], zone["y1"]),
                (zone["x2"], zone["y2"]),
                (0, 0, 255),
                3
            )

            cv2.putText(
                annotated,
                zone["zone_name"],
                (zone["x1"], zone["y1"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # 위험 이벤트 발생 시 캡처 이미지 저장 여부 판단
        detection_result = save_capture_if_needed(annotated, cctv_id, detection_result)

        # 감지 분석 결과는 CCTV별 5초에 1번만 detection_log에 저장
        if should_save_detection_log(cctv_id):
            save_detection_log(cctv_id, detection_result)

        print("DB 저장 직전:", cctv_id, detection_result)

        # 캡처가 있는 위험 이벤트만 event_log, capture_image에 저장
        save_event_with_capture(cctv_id, detection_result)

        # 실시간 모니터링 화면에 표시할 최신 상태 저장
        latest_detection_status[cctv_id] = {
            "riskLevel": detection_result.get("risk_status", "-"),
            "riskText": get_risk_text(detection_result.get("risk_status", "-")),
            "riskScore": detection_result.get("risk_score", 0),
            "violations": {
                "helmet": detection_result.get("no_helmet", 0),
                "vest": detection_result.get("no_safety_vest", 0),
                "zone": 1 if detection_result.get("in_danger_zone") else 0
            },
            "person": detection_result.get("person", 0),
            "helmet": detection_result.get("helmet", 0),
            "safetyVest": detection_result.get("safety_vest", 0),
            "violationType": detection_result.get("violation_type", "NONE"),
            "captureUrl": detection_result.get("capture_url")
        }

        print(cctv_id, detection_result)

        # 프레임을 jpg로 변환해서 브라우저에 스트리밍
        ret, buffer = cv2.imencode(".jpg", annotated)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

    cap.release()


# 위험도 등급을 화면 표시용 한글 문구로 변환
def get_risk_text(risk_status):
    if risk_status == "SAFE":
        return "정상"
    if risk_status == "WARNING":
        return "주의"
    if risk_status == "DANGER":
        return "위험"
    if risk_status == "CRITICAL":
        return "매우 위험"
    return "-"


# 선택한 CCTV의 최신 감지 상태 반환
def get_latest_detection_status(cctv_id):
    return latest_detection_status.get(cctv_id, {
        "riskLevel": "-",
        "riskText": "-",
        "riskScore": 0,
        "violations": {
            "helmet": 0,
            "vest": 0,
            "zone": 0
        },
        "person": 0,
        "helmet": 0,
        "safetyVest": 0,
        "violationType": "NONE",
        "captureUrl": None
    })