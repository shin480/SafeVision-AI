const API = {
  cctvList: "/api/cctv",
  monitoringStatus: "/api/monitoring/status",
};

/* =========================
   모니터링 sidebar 처리
========================= */

function setMonitoringSidebarActive() {
  const menuItems = document.querySelectorAll(".menu-item");

  menuItems.forEach((item) => {
    item.classList.remove("active");

    const href = item.getAttribute("href");
    const pageName = item.dataset.page;

    if (href === "./monitoring.html" || pageName === "monitoring") {
      item.classList.add("active");
    }
  });
}

function loadMonitoringSidebar() {
  const sidebarContainer = document.querySelector("#sidebar-container");

  if (!sidebarContainer) {
    return;
  }

  fetch("/sidebar")
    .then((res) => res.text())
    .then((html) => {
      sidebarContainer.innerHTML = html;
      setMonitoringSidebarActive();
    })
    .catch((error) => {
      console.error("sidebar 로드 실패:", error);
    });
}

/* =========================
   모니터링 데이터 처리
========================= */

function getRiskClass(riskLevel) {
  switch (riskLevel) {
    case "SAFE":
      return "risk-safe";
    case "WARNING":
      return "risk-warning";
    case "DANGER":
      return "risk-danger";
    case "CRITICAL":
      return "risk-critical";
    default:
      return "";
  }
}

function setText(selector, value) {
  const element = document.querySelector(selector);

  if (!element) {
    return;
  }

  element.textContent = value ?? "-";
}

function resetMonitoringView() {
  setText("#currentRiskLevel", "-");
  setText("#currentRiskText", "-");
  setText("#riskScore", "-");
  setText("#helmetViolation", "-");
  setText("#vestViolation", "-");
  setText("#zoneViolation", "-");

  const riskLevelEl = document.querySelector("#currentRiskLevel");
  const riskTextEl = document.querySelector("#currentRiskText");

  if (riskLevelEl) {
    riskLevelEl.className = "";
  }

  if (riskTextEl) {
    riskTextEl.className = "";
  }
}

function renderCctvOptions(cctvList) {
  const cctvSelect = document.querySelector("#cctvSelect");

  if (!cctvSelect) {
    return;
  }

  cctvSelect.innerHTML = `<option value="">CCTV 선택</option>`;

  cctvList.forEach((cctv) => {
    const option = document.createElement("option");

    option.value = cctv.id;
    option.textContent = cctv.name;

    cctvSelect.appendChild(option);
  });
}

function renderMonitoring(data) {
  const riskLevelEl = document.querySelector("#currentRiskLevel");
  const riskTextEl = document.querySelector("#currentRiskText");

  const riskClass = getRiskClass(data.riskLevel);

  if (riskLevelEl) {
    riskLevelEl.textContent = data.riskLevel ?? "-";
    riskLevelEl.className = riskClass;
  }

  if (riskTextEl) {
    riskTextEl.textContent = data.riskText ?? "-";
    riskTextEl.className = riskClass;
  }

  setText(
    "#riskScore",
    data.riskScore !== undefined && data.riskScore !== null
      ? `${data.riskScore} / 100`
      : "-"
  );

  setText("#helmetViolation", data.violations?.helmet);
  setText("#vestViolation", data.violations?.vest);
  setText("#zoneViolation", data.violations?.zone);
}

async function loadCctvList() {
  try {
    const response = await fetch(API.cctvList);

    if (!response.ok) {
      throw new Error("CCTV 목록 조회 실패");
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || "CCTV 목록 조회 실패");
    }

    renderCctvOptions(result.data);
  } catch (error) {
    console.error(error);
  }
}

async function loadMonitoringStatus(cctvId) {
  if (!cctvId) {
    resetMonitoringView();
    return;
  }

  try {
    const response = await fetch(`${API.monitoringStatus}?cctvId=${cctvId}`);

    if (!response.ok) {
      throw new Error("모니터링 상태 조회 실패");
    }

    const data = await response.json();
    renderMonitoring(data);
  } catch (error) {
    console.error(error);
    resetMonitoringView();
  }
}

function updateVideoFeed(cctvId) {
  const video = document.querySelector("#cctvVideo");
  const placeholder = document.querySelector("#videoPlaceholder");

  if (!video || !placeholder) {
    return;
  }

  if (!cctvId) {
    video.removeAttribute("src");
    video.classList.add("hidden");
    placeholder.classList.remove("hidden");
    return;
  }

  video.src = `/api/video-feed/${cctvId}`;
  video.classList.remove("hidden");
  placeholder.classList.add("hidden");
}

/* =========================
   전체보기 처리
========================= */

function openFullscreen() {
  const video = document.querySelector("#cctvVideo");
  const fullscreenModal = document.querySelector("#fullscreenModal");
  const fullscreenVideo = document.querySelector("#fullscreenVideo");

  if (!video || !fullscreenModal || !fullscreenVideo) {
    return;
  }

  if (!video.src || video.classList.contains("hidden")) {
    alert("먼저 CCTV를 선택해주세요.");
    return;
  }

  fullscreenVideo.src = video.src;
  fullscreenModal.classList.add("active");
}

function closeFullscreen() {
  const fullscreenModal = document.querySelector("#fullscreenModal");
  const fullscreenVideo = document.querySelector("#fullscreenVideo");

  if (!fullscreenModal || !fullscreenVideo) {
    return;
  }

  fullscreenModal.classList.remove("active");
  fullscreenVideo.removeAttribute("src");
}

function initFullscreen() {
  const fullscreenBtn = document.querySelector("#fullscreenBtn");
  const fullscreenModal = document.querySelector("#fullscreenModal");
  const closeFullscreenBtn = document.querySelector("#closeFullscreenBtn");

  if (fullscreenBtn) {
    fullscreenBtn.addEventListener("click", openFullscreen);
  }

  if (closeFullscreenBtn) {
    closeFullscreenBtn.addEventListener("click", closeFullscreen);
  }

  if (fullscreenModal) {
    fullscreenModal.addEventListener("click", (event) => {
      if (event.target === fullscreenModal) {
        closeFullscreen();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeFullscreen();
    }
  });
}

/* =========================
   초기 실행
========================= */

function initMonitoring() {
  loadMonitoringSidebar();

  resetMonitoringView();
  loadCctvList();
  initFullscreen();

  const searchBtn = document.querySelector("#searchBtn");
  const cctvSelect = document.querySelector("#cctvSelect");

  if (searchBtn && cctvSelect) {
    searchBtn.addEventListener("click", () => {
      const cctvId = cctvSelect.value;

      updateVideoFeed(cctvId);
      loadMonitoringStatus(cctvId);
    });
  }
}

document.addEventListener("DOMContentLoaded", initMonitoring);