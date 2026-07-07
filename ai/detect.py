from pathlib import Path
from ultralytics import YOLO
import cv2
from collections import Counter
from ai.risk import calculate_risk
from ai.capture import get_capture_path_if_needed
from backend.event_log.getEventLogs import save_event_with_capture

from sqlalchemy import text
from backend.util.db import get_engine

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ai" / "models" / "weights" / "ppe100.pt"

# YOLO 모델 한 번만 로드
model = YOLO(str(MODEL_PATH))
latest_detection_status = {}

# YOLO 감지 결과를 JSON 형태로 정리하는 함수
def extract_detection_result(results, model):
    boxes = results[0].boxes

    # 감지된 객체가 없을 때
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

    # 프론트/백엔드로 넘기기 좋은 JSON 형태
    detection_result = {
        "person": counts.get("person", 0),
        "helmet": counts.get("helmet", 0),
        "no_helmet": counts.get("no_helmet", 0),
        "safety_vest": counts.get("safety_vest", 0),
        "no_safety_vest": counts.get("no_safety_vest", 0)
    }

    return detection_result

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

def check_danger_zone_intrusion(results, model, danger_zones):
    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return False

    for box in boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]

        if class_name != "person":
            continue

        x1, y1, x2, y2 = box.xyxy[0]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

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

# 감지 결과를 바탕으로 위험도 점수와 상태를 추가하는 함수 - 나중에 위험구역 기능을 붙이면 됨
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

def make_violation_type(detection_result):
    """
    감지 결과를 바탕으로 위반 유형을 만든다.
    쿨다운 중복 캡처 기준으로 사용된다.
    """

    violation_types = []

    if detection_result.get("no_helmet", 0) > 0:
        violation_types.append("NO_HELMET")

    if detection_result.get("no_safety_vest", 0) > 0:
        violation_types.append("NO_SAFETY_VEST")

    if detection_result.get("in_danger_zone"):
        violation_types.append("DANGER_ZONE")

    if not violation_types:
        return "NONE"

    return "_".join(violation_types)


def save_capture_if_needed(capture_frame, cctv_id, detection_result):
    """
    위험도 결과에 따라 캡처 이미지를 저장한다.
    실제 캡처는 위험구역 설정이 아니라 실시간 감지 결과 기준으로 수행된다.
    """

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

        # 프론트에서 이미지 src로 쓰기 좋은 경로
        detection_result["capture_url"] = "/" + capture_path.replace("\\", "/")
    else:
        detection_result["capture_path"] = None
        detection_result["capture_url"] = None

    detection_result["violation_type"] = violation_type

    return detection_result

# 파일을 실행하면 바로 실행할 테스트용 코드
def main():
    # ===============================
    # 1. 카메라 3대 연결
    # ===============================
    # 보통 0, 1, 2 순서로 잡힘
    # 안 잡히면 2를 3으로 바꿔보면 됨
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(1)
    cap3 = cv2.VideoCapture(2)


    # ===============================
    # 2. 카메라 연결 확인
    # ===============================
    if not cap1.isOpened():
        print("Camera 1을 열 수 없습니다. index 0 확인 필요")

    if not cap2.isOpened():
        print("Camera 2를 열 수 없습니다. index 1 확인 필요")

    if not cap3.isOpened():
        print("Camera 3을 열 수 없습니다. index 2 확인 필요")

    if not cap1.isOpened() and not cap2.isOpened() and not cap3.isOpened():
        print("연결된 카메라가 없습니다.")
        exit()


    print("YOLO 3-camera detection start")
    print("q 키를 누르면 종료됩니다.")


    # ===============================
    # 3. 프레임 단위 YOLO 감지
    # ===============================
    while True:
        # 각 카메라에서 프레임 읽기
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        ret3, frame3 = cap3.read()

        # -------------------------------
        # Camera 1 감지
        # -------------------------------
        if ret1:
            results1 = model(frame1, conf=0.5)

            detection_result1 = extract_detection_result(results1, model)
            detection_result1 = add_risk_result(detection_result1)

            annotated1 = results1[0].plot()
            detection_result1 = save_capture_if_needed(annotated1, "CCTV01", detection_result1)

            print("Camera 1:", detection_result1)

            cv2.imshow("Camera 1 Detection", annotated1)

        # -------------------------------
        # Camera 2 감지
        # -------------------------------
        if ret2:
            results2 = model(frame2, conf=0.5)

            detection_result2 = extract_detection_result(results2, model)
            detection_result2 = add_risk_result(detection_result2)

            annotated2 = results2[0].plot()
            detection_result2 = save_capture_if_needed(annotated2, "CCTV02", detection_result2)

            print("Camera 2:", detection_result2)

            cv2.imshow("Camera 2 Detection", annotated2)

        # -------------------------------
        # Camera 3 감지
        # -------------------------------
        if ret3:
            results3 = model(frame3, conf=0.5)

            detection_result3 = extract_detection_result(results3, model)
            detection_result3 = add_risk_result(detection_result3)

            annotated3 = results3[0].plot()
            detection_result3 = save_capture_if_needed(annotated3, "CCTV03", detection_result3)

            print("Camera 3:", detection_result3)

            cv2.imshow("Camera 3 Detection", annotated3)

        # q 키 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # ===============================
    # 4. 종료 처리
    # ===============================
    cap1.release()
    cap2.release()
    cap3.release()
    cv2.destroyAllWindows()

# 서버에 카메라 전송
def generate_frames(camera_index, cctv_id, conf=0.5):

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(f"카메라{camera_index} 열기 실패")

    while True:
        success, frame = cap.read()

        if not success:
            break

        results = model(frame, conf=conf)

        danger_zones = get_danger_zones(cctv_id)
        in_danger_zone = check_danger_zone_intrusion(results, model, danger_zones)

        detection_result = extract_detection_result(results, model)
        detection_result = add_risk_result(
            detection_result,
            in_danger_zone=in_danger_zone
        )

        annotated = results[0].plot()

        print("현재 CCTV ID:", cctv_id)
        print("위험구역 조회 결과:", danger_zones)
        print("위험구역 침입 여부:", in_danger_zone)

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

        detection_result = save_capture_if_needed(annotated, cctv_id, detection_result)
        save_event_with_capture(cctv_id, detection_result)

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