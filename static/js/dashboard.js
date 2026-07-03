const dashboardData = {
  overallStatus: {
    status: "SAFE",
    label: "안전",
  },
  todayWarning: {
    count: 12,
    change: "+3",
    changeLabel: "(어제 대비)",
  },
  ppeRate: {
    rate: 92.3,
    change: "+2.1%",
    changeLabel: "(어제 대비)",
  },
  cctv: {
    connected: 3,
    total: 3,
    label: "정상 연결",
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

  return "";
}

function renderSummary(data) {
  document.querySelector("#overall-status").textContent = data.overallStatus.status;
  document.querySelector("#overall-status-label").textContent = data.overallStatus.label;

  document.querySelector("#today-warning-count").textContent = data.todayWarning.count;
  document.querySelector("#warning-change").textContent = data.todayWarning.change;
  document.querySelector("#warning-change-label").textContent = data.todayWarning.changeLabel;

  document.querySelector("#ppe-rate").textContent = `${data.ppeRate.rate}%`;
  document.querySelector("#ppe-change").textContent = data.ppeRate.change;
  document.querySelector("#ppe-change-label").textContent = data.ppeRate.changeLabel;

  document.querySelector("#cctv-status").textContent = `${data.cctv.connected} / ${data.cctv.total}`;
  document.querySelector("#cctv-status-label").textContent = data.cctv.label;
}

function renderRecentEvents(events) {
  const tbody = document.querySelector("#recent-event-tbody");

  tbody.innerHTML = events
    .map((event) => {
      const riskClass = getRiskLevelClass(event.riskLevel);
      const statusClass = getStatusClass(event.status);

      return `
        <tr>
          <td>${event.time}</td>
          <td>${event.cctv}</td>
          <td>${event.violation}</td>
          <td class="${riskClass}">${event.riskLevel}</td>
          <td class="${statusClass}">${event.status}</td>
        </tr>
      `;
    })
    .join("");
}

function initDashboard() {
  renderSummary(dashboardData);
  renderRecentEvents(dashboardData.recentEvents);
}

document.addEventListener("DOMContentLoaded", initDashboard);