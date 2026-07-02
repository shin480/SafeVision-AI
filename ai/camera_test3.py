import cv2


# ===============================
# 1. 카메라 3개 연결
# ===============================
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
cap3 = cv2.VideoCapture(2)


# ===============================
# 2. 카메라 연결 확인
# ===============================
if not cap1.isOpened():
    print("1번 카메라를 열 수 없습니다. index 0 확인 필요")

if not cap2.isOpened():
    print("2번 카메라를 열 수 없습니다. index 1 확인 필요")

if not cap3.isOpened():
    print("3번 카메라를 열 수 없습니다. index 2 확인 필요")

if not cap1.isOpened() and not cap2.isOpened() and not cap3.isOpened():
    print("연결된 카메라가 없습니다.")
    exit()


print("카메라 3개 테스트 시작")
print("q 키를 누르면 종료됩니다.")


# ===============================
# 3. 카메라 화면 출력
# ===============================
while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    ret3, frame3 = cap3.read()

    if ret1:
        cv2.imshow("Camera 1", frame1)

    if ret2:
        cv2.imshow("Camera 2", frame2)

    if ret3:
        cv2.imshow("Camera 3", frame3)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ===============================
# 4. 종료 처리
# ===============================
cap1.release()
cap2.release()
cap3.release()
cv2.destroyAllWindows()