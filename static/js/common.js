const isLogin = sessionStorage.getItem("isLogin");
const currentPage = window.location.pathname;

if (!currentPage.includes("login") && !isLogin) {
  location.href = "./login.html";
}

console.log("SafeVision-AI common.js loaded");