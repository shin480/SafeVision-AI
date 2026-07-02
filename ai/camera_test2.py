import cv2


# ===============================
# 1. 카메라 2개 연결
# ===============================
# 0번: 첫 번째 카메라
# 1번: 두 번째 카메라
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)


# ===============================
# 2. 카메라 연결 확인
# ===============================
if not cap1.isOpened():
    print("1번 카메라를 열 수 없습니다. index 0 확인 필요")

if not cap2.isOpened():
    print("2번 카메라를 열 수 없습니다. index 1 확인 필요")

# 둘 다 안 열렸으면 종료
if not cap1.isOpened() and not cap2.isOpened():
    print("연결된 카메라가 없습니다.")
    exit()


print("카메라 2개 테스트 시작")
print("q 키를 누르면 종료됩니다.")


# ===============================
# 3. 카메라 화면 출력
# ===============================
while True:
    # 각 카메라에서 프레임 읽기
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    # 1번 카메라 화면 출력
    if ret1:
        cv2.imshow("Camera 1", frame1)

    # 2번 카메라 화면 출력
    if ret2:
        cv2.imshow("Camera 2", frame2)

    # q 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ===============================
# 4. 종료 처리
# ===============================
cap1.release()
cap2.release()
cv2.destroyAllWindows()