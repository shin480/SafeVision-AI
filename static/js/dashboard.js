const dashboardData = {
  overallStatus: {
    status: "SAFE",
    text: "안전",
  },

  todayWarning: {
    count: 12,
    change: "+3",
    changeText: "(어제 대비)",
  },

  ppeRate: {
    rate: 92.3,
    change: "+2.1%",
    changeText: "(어제 대비)",
  },

  cctv: {
    connected: 3,
    total: 3,
    text: "정상 연결",
  },

  recentEvents: [
    {
      time: "2026-07-02 14:35:21",
      cctv: "1번 CCTV",
      violation: "안전모 미착용",
      riskLevel: "DANGER",
      status: "미확인",
    },
    {
      time: "2026-07-02 14:32:10",
      cctv: "2번 CCTV",
      violation: "위험구역 진입",
      riskLevel: "WARNING",
      status: "확인",
    },
    {
      time: "2026-07-02 14:28:45",
      cctv: "1번 CCTV",
      violation: "안전조끼 미착용",
      riskLevel: "DANGER",
      status: "미확인",
    },
    {
      time: "2026-07-02 14:20:33",
      cctv: "1번 CCTV",
      violation: "안전모, 안전조끼 미착용",
      riskLevel: "CRITICAL",
      status: "미확인",
    },
    {
      time: "2026-07-02 14:18:11",
      cctv: "3번 CCTV",
      violation: "PPE 복합 위반",
      riskLevel: "CRITICAL",
      status: "조치완료",
    },
    {
      time: "2026-07-02 14:15:02",
      cctv: "1번 CCTV",
      violation: "안전모 미착용",
      riskLevel: "WARNING",
      status: "미확인",
    },
    {
      time: "2026-07-02 14:10:47",
      cctv: "2번 CCTV",
      violation: "안전모 미착용",
      riskLevel: "DANGER",
      status: "확인",
    },
  ],
};

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

  element.textContent = value;
}

function renderSummary(data) {
  setText("#overallStatus", data.overallStatus.status);
  setText("#overallStatusText", data.overallStatus.text);

  setText("#todayWarningCount", data.todayWarning.count);
  setText(
    "#todayWarningChange",
    `${data.todayWarning.change} ${data.todayWarning.changeText}`
  );

  setText("#ppeRate", `${data.ppeRate.rate}%`);
  setText("#ppeRateChange", `${data.ppeRate.change} ${data.ppeRate.changeText}`);

  setText("#cctvStatus", `${data.cctv.connected} / ${data.cctv.total}`);
  setText("#cctvStatusText", data.cctv.text);
}

function renderRecentEvents(events) {
  const tbody = document.querySelector("#recentEventTable");

  if (!tbody) {
    return;
  }

  tbody.innerHTML = "";

  events.forEach((event) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${event.time}</td>
      <td>${event.cctv}</td>
      <td>${event.violation}</td>
      <td class="${getRiskLevelClass(event.riskLevel)}">${event.riskLevel}</td>
      <td class="${getStatusClass(event.status)}">${event.status}</td>
    `;

    tbody.appendChild(tr);
  });
}

function initDashboard() {
  renderSummary(dashboardData);
  renderRecentEvents(dashboardData.recentEvents);
}

document.addEventListener("DOMContentLoaded", initDashboard);