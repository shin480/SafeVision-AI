const cctvList = [
  {
    cctv_id: "cctv01",
    cctv_name: "CCTV-01",
    location: "1층 작업구역",
    stream_url: "/api/video-feed/cctv01",
    is_active: 1,
    created_at: "2026-07-06 10:00:00"
  },
  {
    cctv_id: "cctv02",
    cctv_name: "CCTV-02",
    location: "2층 적재구역",
    stream_url: "/api/video-feed/cctv02",
    is_active: 1,
    created_at: "2026-07-06 10:05:00"
  },
  {
    cctv_id: "cctv03",
    cctv_name: "CCTV-03",
    location: "지하 위험구역",
    stream_url: "/api/video-feed/cctv03",
    is_active: 0,
    created_at: "2026-07-06 10:10:00"
  }
];

let currentList = [...cctvList];

const tableBody = document.getElementById("cctvTableBody");
const totalCount = document.getElementById("totalCount");
const activeCount = document.getElementById("activeCount");
const inactiveCount = document.getElementById("inactiveCount");

const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

const modal = document.getElementById("cctvModal");
const openAddModalBtn = document.getElementById("openAddModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const cancelBtn = document.getElementById("cancelBtn");
const cctvForm = document.getElementById("cctvForm");

const formMode = document.getElementById("formMode");
const cctvId = document.getElementById("cctvId");
const cctvName = document.getElementById("cctvName");
const locationInput = document.getElementById("location");
const streamUrl = document.getElementById("streamUrl");
const isActive = document.getElementById("isActive");
const modalTitle = document.getElementById("modalTitle");

function renderSummary(list) {
  totalCount.textContent = list.length;
  activeCount.textContent = list.filter(item => Number(item.is_active) === 1).length;
  inactiveCount.textContent = list.filter(item => Number(item.is_active) === 0).length;
}

function renderTable(list) {
  tableBody.innerHTML = "";

  if (list.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; color:#6b7280;">
          조회된 CCTV가 없습니다.
        </td>
      </tr>
    `;
    return;
  }

  list.forEach(item => {
    const statusClass = Number(item.is_active) === 1 ? "status-active" : "status-inactive";
    const statusText = Number(item.is_active) === 1 ? "사용" : "미사용";

    const row = `
      <tr>
        <td>${item.cctv_id}</td>
        <td>${item.cctv_name}</td>
        <td>${item.location || "-"}</td>
        <td>${item.stream_url || "-"}</td>
        <td>
          <span class="status-badge ${statusClass}">${statusText}</span>
        </td>
        <td>${item.created_at || "-"}</td>
        <td>
          <div class="action-btns">
            <button class="edit-btn" onclick="openEditModal('${item.cctv_id}')">수정</button>
            <button class="delete-btn" onclick="deleteCctv('${item.cctv_id}')">삭제</button>
          </div>
        </td>
      </tr>
    `;

    tableBody.insertAdjacentHTML("beforeend", row);
  });
}

function refreshView(list = currentList) {
  renderSummary(list);
  renderTable(list);
}

function openModal() {
  modal.classList.add("active");
}

function closeModal() {
  modal.classList.remove("active");
  cctvForm.reset();
  formMode.value = "add";
  cctvId.disabled = false;
  modalTitle.textContent = "CCTV 등록";
}

function openAddModal() {
  cctvForm.reset();
  formMode.value = "add";
  cctvId.disabled = false;
  modalTitle.textContent = "CCTV 등록";
  openModal();
}

function openEditModal(id) {
  const item = cctvList.find(cctv => cctv.cctv_id === id);

  if (!item) {
    alert("CCTV 정보를 찾을 수 없습니다.");
    return;
  }

  formMode.value = "edit";
  cctvId.value = item.cctv_id;
  cctvId.disabled = true;
  cctvName.value = item.cctv_name;
  locationInput.value = item.location;
  streamUrl.value = item.stream_url;
  isActive.value = String(item.is_active);

  modalTitle.textContent = "CCTV 수정";
  openModal();
}

function deleteCctv(id) {
  const confirmed = confirm("해당 CCTV를 삭제하시겠습니까?");

  if (!confirmed) return;

  const index = cctvList.findIndex(item => item.cctv_id === id);

  if (index >= 0) {
    cctvList.splice(index, 1);
    currentList = [...cctvList];
    refreshView();
  }
}

function handleSubmit(event) {
  event.preventDefault();

  const data = {
    cctv_id: cctvId.value.trim(),
    cctv_name: cctvName.value.trim(),
    location: locationInput.value.trim(),
    stream_url: streamUrl.value.trim(),
    is_active: Number(isActive.value),
    created_at: new Date().toISOString().slice(0, 19).replace("T", " ")
  };

  if (!data.cctv_id || !data.cctv_name) {
    alert("CCTV ID와 CCTV명은 필수입니다.");
    return;
  }

  if (formMode.value === "add") {
    const exists = cctvList.some(item => item.cctv_id === data.cctv_id);

    if (exists) {
      alert("이미 등록된 CCTV ID입니다.");
      return;
    }

    cctvList.push(data);
  } else {
    const index = cctvList.findIndex(item => item.cctv_id === data.cctv_id);

    if (index >= 0) {
      cctvList[index] = {
        ...cctvList[index],
        cctv_name: data.cctv_name,
        location: data.location,
        stream_url: data.stream_url,
        is_active: data.is_active
      };
    }
  }

  currentList = [...cctvList];
  refreshView();
  closeModal();
}

function searchCctv() {
  const keyword = searchInput.value.trim().toLowerCase();

  currentList = cctvList.filter(item => {
    return (
      item.cctv_name.toLowerCase().includes(keyword) ||
      item.location.toLowerCase().includes(keyword) ||
      item.cctv_id.toLowerCase().includes(keyword)
    );
  });

  refreshView(currentList);
}

openAddModalBtn.addEventListener("click", openAddModal);
closeModalBtn.addEventListener("click", closeModal);
cancelBtn.addEventListener("click", closeModal);
cctvForm.addEventListener("submit", handleSubmit);
searchBtn.addEventListener("click", searchCctv);

searchInput.addEventListener("keyup", event => {
  if (event.key === "Enter") {
    searchCctv();
  }
});

refreshView();