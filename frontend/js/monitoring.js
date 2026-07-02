// 실시간 모니터링 페이지용 JS

const startButton = document.querySelector(".button");
const stopButton = document.querySelector(".button.secondary");
const videoBox = document.querySelector(".video-box");

if (startButton && stopButton && videoBox) {
  startButton.addEventListener("click", () => {
    videoBox.textContent = "감지 실행 중...";
    videoBox.style.border = "3px solid #03c75a";
    alert("감지를 시작합니다.");
  });

  stopButton.addEventListener("click", () => {
    videoBox.textContent = "실시간 영상 영역";
    videoBox.style.border = "none";
    alert("감지를 중지합니다.");
  });
}