document.addEventListener("DOMContentLoaded", () => {
  const sidebarContainer = document.querySelector("#sidebar-container");

  if (sidebarContainer) {
    fetch("./sidebar.html")
      .then((response) => {
        if (!response.ok) {
          throw new Error("sidebar.html을 불러오지 못했습니다.");
        }

        return response.text();
      })
      .then((html) => {
        sidebarContainer.innerHTML = html;

        if (typeof setActiveSidebar === "function") {
          setActiveSidebar();
        }

        const logoutBtn = document.querySelector("#logoutBtn");

        if (logoutBtn) {
          logoutBtn.addEventListener("click", () => {
            sessionStorage.removeItem("isLogin");
            location.href = "/login";
          });
        }
      })
      .catch((error) => {
        console.error("sidebar 로드 실패:", error);
      });
  }
});