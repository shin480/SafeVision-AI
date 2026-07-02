from ultralytics import YOLO
import cv2


# ===============================
# 1. YOLO 모델 불러오기
# ===============================
# 아직 학습 모델이 없으면 yolo11n.pt 사용
# 나중에 best.pt 받으면 아래 경로로 변경
# model = YOLO("ai/models/weights/best.pt")
model = YOLO("yolo11n.pt")


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
        annotated1 = results1[0].plot()
        cv2.imshow("Camera 1 Detection", annotated1)

    # -------------------------------
    # Camera 2 감지
    # -------------------------------
    if ret2:
        results2 = model(frame2, conf=0.5)
        annotated2 = results2[0].plot()
        cv2.imshow("Camera 2 Detection", annotated2)

    # -------------------------------
    # Camera 3 감지
    # -------------------------------
    if ret3:
        results3 = model(frame3, conf=0.5)
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
