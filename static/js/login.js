const loginForm = document.querySelector("#loginForm");
const adminId = document.querySelector("#adminId");
const adminPw = document.querySelector("#adminPw");
const loginMessage = document.querySelector("#loginMessage");

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const id = adminId.value.trim();
  const pw = adminPw.value.trim();

  if (!id || !pw) {
    loginMessage.textContent = "아이디와 비밀번호를 모두 입력하세요.";
    return;
  }

  // 백엔드 연결 전 임시 관리자 계정
  if (id === "admin" && pw === "1234") {
    sessionStorage.setItem("isLogin", "true");
    location.href = "./index.html";
  } else {
    loginMessage.textContent = "아이디 또는 비밀번호가 올바르지 않습니다.";
  }
});