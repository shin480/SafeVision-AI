fetch("./dashboard.html")
  .then((res) => res.text())
  .then((html) => {
    document.getElementById("sidebar-container").innerHTML = html;

    const currentPage = location.pathname.split("/").pop().replace(".html", "");

    document.querySelectorAll(".menu-item").forEach((item) => {
      if (item.dataset.page === currentPage) {
        item.classList.add("active");
      }
    });
  });

const DASHBOARD_API = "/api/dashboard";

function getRiskLevelClass(riskLevel) {
  switch (riskLevel) {
    case "SAFE":
      return "level-safe";
    case "WARNING":
      return "level-warning";
    case "DANGER":
      return "level-danger";
    case "CRITICAL":
      return "level-critical";
    default:
      return "";
  }
}

function getStatusClass(status) {
  if (status === "확인" || status === "조치완료") {
    return "status-done";
  }

  return "status-pending";
}

function setText(selector, value) {
  const element = document.querySelector(selector);

  if (!element) {
    return;
  }

  element.textContent = value ?? "-";
}

function resetDashboard() {
  setText("#overallStatus", "-");
  setText("#overallStatusText", "-");

  setText("#todayWarningCount", "-");
  setText("#todayWarningChange", "-");

  setText("#ppeRate", "-");
  setText("#ppeRateChange", "-");

  setText("#cctvStatus", "-");
  setText("#cctvStatusText", "-");

  const tbody = document.querySelector("#recentEventTable");

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5">데이터를 불러오는 중입니다.</td>
      </tr>
    `;
  }
}

function renderSummary(data) {
  setText("#overallStatus", data.overallStatus?.status);
  setText("#overallStatusText", data.overallStatus?.text);

  setText("#todayWarningCount", data.todayWarning?.count);

  const warningChange = data.todayWarning?.change;
  const warningChangeText = data.todayWarning?.changeText;

  setText(
    "#todayWarningChange",
    warningChange && warningChangeText
      ? `${warningChange} ${warningChangeText}`
      : "-"
  );

  const ppeRate = data.ppeRate?.rate;
  setText("#ppeRate", ppeRate !== undefined && ppeRate !== null ? `${ppeRate}%` : "-");

  const ppeChange = data.ppeRate?.change;
  const ppeChangeText = data.ppeRate?.changeText;

  setText(
    "#ppeRateChange",
    ppeChange && ppeChangeText ? `${ppeChange} ${ppeChangeText}` : "-"
  );

  const connected = data.cctv?.connected;
  const total = data.cctv?.total;

  setText(
    "#cctvStatus",
    connected !== undefined && total !== undefined ? `${connected} / ${total}` : "-"
  );

  setText("#cctvStatusText", data.cctv?.text);
}

function renderRecentEvents(events) {
  const tbody = document.querySelector("#recentEventTable");

  if (!tbody) {
    return;
  }

  tbody.innerHTML = "";

  if (!events || events.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5">최근 이벤트가 없습니다.</td>
      </tr>
    `;
    return;
  }

  events.forEach((event) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${event.time ?? "-"}</td>
      <td>${event.cctv ?? "-"}</td>
      <td>${event.violation ?? "-"}</td>
      <td class="${getRiskLevelClass(event.riskLevel)}">${event.riskLevel ?? "-"}</td>
      <td class="${getStatusClass(event.status)}">${event.status ?? "-"}</td>
    `;

    tbody.appendChild(tr);
  });
}

async function loadDashboard() {
  resetDashboard();

  try {
    const response = await fetch(DASHBOARD_API);

    if (!response.ok) {
      throw new Error("대시보드 데이터 조회 실패");
    }

    const data = await response.json();

    renderSummary(data);
    renderRecentEvents(data.recentEvents);
  } catch (error) {
    console.error(error);

    const tbody = document.querySelector("#recentEventTable");

    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5">대시보드 데이터를 불러오지 못했습니다.</td>
        </tr>
      `;
    }
  }
}

document.addEventListener("DOMContentLoaded", loadDashboard);