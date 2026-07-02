// 로그인 여부 확인
// login.html을 거치지 않고 대시보드나 관리 페이지에 접근하는 것을 막기 위한 임시 코드

const isLogin = sessionStorage.getItem("isLogin");

if (!isLogin) {
  location.href = "./login.html";
}

console.log("SafeVision-AI common.js loaded");