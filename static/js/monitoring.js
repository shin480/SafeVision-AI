// 실시간 모니터링 페이지 웹캠 출력용 JS

let webcamStream = null;

const webcam = document.getElementById("webcam");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const videoBox = document.querySelector(".video-box");

// 감지 시작 버튼 클릭 시 웹캠 실행
startBtn.addEventListener("click", async () => {
  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false
    });

    webcam.srcObject = webcamStream;

    if (videoBox) {
      videoBox.style.border = "3px solid #03c75a";
    }

    console.log("웹캠이 시작되었습니다.");
  } catch (error) {
    console.error("웹캠 실행 실패:", error);
    alert("웹캠을 실행할 수 없습니다. 브라우저 카메라 권한을 확인하세요.");
  }
});

// 감지 중지 버튼 클릭 시 웹캠 중지
stopBtn.addEventListener("click", () => {
  if (webcamStream) {
    webcamStream.getTracks().forEach((track) => {
      track.stop();
    });

    webcam.srcObject = null;
    webcamStream = null;

    if (videoBox) {
      videoBox.style.border = "none";
    }

    console.log("웹캠이 중지되었습니다.");
  }
});