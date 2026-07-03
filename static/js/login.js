const loginForm = document.querySelector(".login-form");
const adminIdInput = document.querySelector("#admin-id");
const adminPasswordInput = document.querySelector("#admin-password");
const saveIdCheckbox = document.querySelector('input[name="save_id"]');

// 페이지 열릴 때 저장된 아이디 불러오기
document.addEventListener("DOMContentLoaded", () => {
  const savedAdminId = localStorage.getItem("savedAdminId");

  if (savedAdminId) {
    adminIdInput.value = savedAdminId;
    saveIdCheckbox.checked = true;
  }
});

if (loginForm) {
  loginForm.addEventListener("submit", function (event) {
    const adminId = adminIdInput.value.trim();
    const adminPassword = adminPasswordInput.value.trim();

    if (!adminId || !adminPassword) {
      event.preventDefault();
      alert("아이디와 비밀번호를 입력하세요.");
      return;
    }

    // 아이디 저장 체크 여부에 따라 저장/삭제
    if (saveIdCheckbox.checked) {
      localStorage.setItem("savedAdminId", adminId);
    } else {
      localStorage.removeItem("savedAdminId");
    }

    // 로그인 상태 저장
    sessionStorage.setItem("isLogin", "true");
  });
}