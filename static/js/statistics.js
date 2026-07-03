let hourlyChart = null;
let typeChart = null;

fetch("./sidebar.html")
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

async function loadStatistics() {
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;

  // Flask 연결 시 이 부분만 바꾸면 됨
  // const response = await fetch(`/api/statistics?start=${startDate}&end=${endDate}`);
  // const data = await response.json();

  const data = await getStatisticsData(startDate, endDate);

  renderSummary(data.summary);
  renderHourlyChart(data.hourlyWarnings);
  renderTypeChart(data.violationTypes);
}

async function getStatisticsData(startDate, endDate) {
  return {
    summary: {
      totalCount: 1234,
      warningCount: 35,
      ppeRate: 92.3,
      riskScore: 32.5
    },
    hourlyWarnings: [
      { time: "09시", count: 3 },
      { time: "10시", count: 6 },
      { time: "11시", count: 4 },
      { time: "12시", count: 9 },
      { time: "13시", count: 7 },
      { time: "14시", count: 11 },
      { time: "15시", count: 5 }
    ],
    violationTypes: [
      { type: "안전모 미착용", rate: 45 },
      { type: "안전조끼 미착용", rate: 25 },
      { type: "위험구역 출입", rate: 20 },
      { type: "기타", rate: 10 }
    ]
  };
}

function renderSummary(summary) {
  document.getElementById("totalCount").textContent =
    `${summary.totalCount.toLocaleString()} 건`;

  document.getElementById("warningCount").textContent =
    `${summary.warningCount.toLocaleString()} 건`;

  document.getElementById("ppeRate").textContent =
    `${summary.ppeRate} %`;

  document.getElementById("riskScore").textContent =
    `${summary.riskScore} 점`;
}

function renderHourlyChart(hourlyData) {
  const labels = hourlyData.map((item) => item.time);
  const counts = hourlyData.map((item) => item.count);

  const ctx = document.getElementById("hourlyChart");

  if (hourlyChart) {
    hourlyChart.destroy();
  }

  hourlyChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "경고 횟수",
          data: counts,
          backgroundColor: "#08a64b",
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 2
          }
        }
      }
    }
  });
}

function renderTypeChart(typeData) {
  const labels = typeData.map((item) => item.type);
  const rates = typeData.map((item) => item.rate);
  const colors = ["#3b82f6", "#ef4444", "#facc15", "#f97316"];

  const ctx = document.getElementById("typeChart");

  if (typeChart) {
    typeChart.destroy();
  }

  typeChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          data: rates,
          backgroundColor: colors,
          borderWidth: 0
        }
      ]
    },
    options: {
      cutout: "50%",
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });

  renderLegend(typeData, colors);
}

function renderLegend(typeData, colors) {
  const legend = document.getElementById("typeLegend");
  legend.innerHTML = "";

  typeData.forEach((item, index) => {
    const li = document.createElement("li");

    li.innerHTML = `
      <span class="legend-color" style="background-color: ${colors[index]}"></span>
      <span>${item.type} (${item.rate}%)</span>
    `;

    legend.appendChild(li);
  });
}

document.getElementById("searchBtn").addEventListener("click", loadStatistics);

loadStatistics();