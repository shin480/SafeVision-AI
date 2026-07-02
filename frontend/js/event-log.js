// 이벤트 로그 페이지용 JS

const searchButton = document.querySelector(".button");

if (searchButton) {
  searchButton.addEventListener("click", () => {
    alert("이벤트 로그를 검색합니다.");
  });
}