const monitoringData = {
  cctvId: "1",
  riskLevel: "DANGER",
  riskText: "위험",
  riskScore: 65,
  violations: {
    helmet: 1,
    vest: 1,
    zone: 0,
  },
};

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

function renderMonitoring(data) {
  const riskLevelEl = document.querySelector("#currentRiskLevel");
  const riskTextEl = document.querySelector("#currentRiskText");

  riskLevelEl.textContent = data.riskLevel;
  riskTextEl.textContent = data.riskText;

  const riskClass = getRiskClass(data.riskLevel);
  riskLevelEl.className = riskClass;
  riskTextEl.className = riskClass;

  document.querySelector("#riskScore").textContent = `${data.riskScore} / 100`;

  document.querySelector("#helmetViolation").textContent = data.violations.helmet;
  document.querySelector("#vestViolation").textContent = data.violations.vest;
  document.querySelector("#zoneViolation").textContent = data.violations.zone;
}

function handleCctvSearch() {
  const selectedCctv = document.querySelector("#cctvSelect").value;

  console.log(`${selectedCctv}번 CCTV 검색`);

  // 나중에 여기서 API 호출하면 됨.
  // fetch(`/api/monitoring?cctv=${selectedCctv}`)
  //   .then((res) => res.json())
  //   .then((data) => renderMonitoring(data));

  renderMonitoring(monitoringData);
}

function initMonitoring() {
  renderMonitoring(monitoringData);

  const searchBtn = document.querySelector("#searchBtn");
  searchBtn.addEventListener("click", handleCctvSearch);
}

document.addEventListener("DOMContentLoaded", initMonitoring);