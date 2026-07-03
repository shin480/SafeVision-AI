let events = [];

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

async function loadEvents() {
  // 나중에 Flask랑 연결하면 여기를 수정하면 됨
  // 예: const response = await fetch("/api/events");
  // events = await response.json();

  events = await getEventData();
  renderTable(events);
}

async function getEventData() {
  return [
    {
      id: 101,
      time: "2026-07-02 14:35:21",
      cctv: "1번 CCTV",
      type: "안전모 미착용",
      risk: "DANGER",
      score: 65,
      status: "미확인",
      memo: ""
    },
    {
      id: 100,
      time: "2026-07-02 14:32:10",
      cctv: "2번 CCTV",
      type: "위험구역 진입",
      risk: "WARNING",
      score: 30,
      status: "확인",
      memo: ""
    },
    {
      id: 99,
      time: "2026-07-02 14:28:45",
      cctv: "1번 CCTV",
      type: "안전조끼 미착용",
      risk: "DANGER",
      score: 60,
      status: "미확인",
      memo: ""
    }
  ];
}

function renderTable(data) {
  const tbody = document.getElementById("eventTableBody");
  tbody.innerHTML = "";

  data.forEach((event) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${event.id}</td>
      <td>${event.time}</td>
      <td>${event.cctv}</td>
      <td>${event.type}</td>
      <td class="${getRiskClass(event.risk)}">${event.risk}</td>
      <td class="${event.status !== "미확인" ? "status-ok" : ""}">
        ${event.status}
      </td>
      <td>
        <button class="detail-btn" data-id="${event.id}">상세</button>
      </td>
    `;

    tbody.appendChild(tr);
  });

  document.querySelectorAll(".detail-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = Number(btn.dataset.id);
      openDetail(id);
    });
  });
}

function getRiskClass(risk) {
  if (risk === "WARNING") return "risk-warning";
  if (risk === "DANGER") return "risk-danger";
  if (risk === "CRITICAL") return "risk-critical";
  return "";
}

function openDetail(id) {
  const event = events.find((item) => item.id === id);

  if (!event) return;

  document.getElementById("detailTime").textContent = event.time;
  document.getElementById("detailCctv").textContent = event.cctv;
  document.getElementById("detailType").textContent = event.type;
  document.getElementById("detailRisk").textContent = `${event.risk} (${event.score}점)`;
  document.getElementById("detailRisk").className = getRiskClass(event.risk);

  document.getElementById("statusSelect").value = event.status;
  document.getElementById("memoInput").value = event.memo || "";

  document.getElementById("detailModal").classList.add("show");

  document.getElementById("saveBtn").onclick = () => {
    event.status = document.getElementById("statusSelect").value;
    event.memo = document.getElementById("memoInput").value;

    renderTable(events);
    closeDetail();
  };
}

function closeDetail() {
  document.getElementById("detailModal").classList.remove("show");
}

document.getElementById("closeBtn").addEventListener("click", closeDetail);

document.getElementById("searchBtn").addEventListener("click", () => {
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;
  const cctv = document.getElementById("cctvSelect").value;

  let filtered = events;

  if (startDate) {
    filtered = filtered.filter((event) => event.time.slice(0, 10) >= startDate);
  }

  if (endDate) {
    filtered = filtered.filter((event) => event.time.slice(0, 10) <= endDate);
  }

  if (cctv !== "all") {
    filtered = filtered.filter((event) => event.cctv === cctv);
  }

  renderTable(filtered);
});

loadEvents();