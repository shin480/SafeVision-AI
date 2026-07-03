const loginForm = document.querySelector(".login-form");

if (loginForm) {
  loginForm.addEventListener("submit", function (event) {
    const adminId = document.querySelector("#admin-id").value.trim();
    const adminPassword = document.querySelector("#admin-password").value.trim();

    if (!adminId || !adminPassword) {
      event.preventDefault();
      alert("아이디와 비밀번호를 입력하세요.");
      return;
    }

    sessionStorage.setItem("isLogin", "true");
  });
}