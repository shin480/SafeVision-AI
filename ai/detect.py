from pathlib import Path
from ultralytics import YOLO
import cv2
from collections import Counter
from ai.risk import calculate_risk

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ai" / "models" / "weights" / "ppe100.pt"

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

# 감지 결과를 바탕으로 위험도 점수와 상태를 추가하는 함수
def add_risk_result(detection_result):
    no_helmet = detection_result["no_helmet"] > 0
    no_safety_vest = detection_result["no_safety_vest"] > 0

    # 위험구역 판정은 아직 구현 전이라 임시로 False
    in_danger_zone = False

    risk_score, risk_status = calculate_risk(
        no_helmet=no_helmet,
        no_safety_vest=no_safety_vest,
        in_danger_zone=in_danger_zone
    )

    detection_result["risk_score"] = risk_score
    detection_result["risk_status"] = risk_status

    return detection_result

# 파일을 실행하면 바로 실행할 테스트용 코드
def main():
    # ===============================
    # 1. YOLO 모델 불러오기
    # ===============================
    # 아직 학습 모델이 없으면 yolo11n.pt 사용
    # 나중에 best.pt 받으면 아래 경로로 변경
    # model = YOLO("ai/models/weights/best.pt")
    model = YOLO(str(MODEL_PATH))
    # ===============================
    # 2. 카메라 3대 연결
    # ===============================
    # 보통 0, 1, 2 순서로 잡힘
    # 안 잡히면 2를 3으로 바꿔보면 됨
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(1)
    cap3 = cv2.VideoCapture(2)


    # ===============================
    # 3. 카메라 연결 확인
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
    # 4. 프레임 단위 YOLO 감지
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

            print("Camera 1:", detection_result1)

            annotated1 = results1[0].plot()
            cv2.imshow("Camera 1 Detection", annotated1)

        # -------------------------------
        # Camera 2 감지
        # -------------------------------
        if ret2:
            results2 = model(frame2, conf=0.5)

            detection_result2 = extract_detection_result(results2, model)
            detection_result2 = add_risk_result(detection_result2)

            print("Camera 2:", detection_result2)

            annotated2 = results2[0].plot()
            cv2.imshow("Camera 2 Detection", annotated2)

        # -------------------------------
        # Camera 3 감지
        # -------------------------------
        if ret3:
            results3 = model(frame3, conf=0.5)

            detection_result3 = extract_detection_result(results3, model)
            detection_result3 = add_risk_result(detection_result3)

            print("Camera 3:", detection_result3)

            annotated3 = results3[0].plot()
            cv2.imshow("Camera 3 Detection", annotated3)

        # q 키 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # ===============================
    # 5. 종료 처리
    # ===============================
    cap1.release()
    cap2.release()
    cap3.release()
    cv2.destroyAllWindows()

# 서버에 카메라 전송
def generate_frames(camera_index, conf=0.5):
    model = YOLO(str(MODEL_PATH))

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(f"카메라{camera_index} 열기 실패")

    while True:
        success, frame = cap.read()

        if not success:
            break

        results = model(frame, conf=conf)

        annotated = results[0].plot()

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


if __name__ == "__main__":
    main()