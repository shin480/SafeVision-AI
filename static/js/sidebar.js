const menuItems = document.querySelectorAll(".menu-item");

const currentPath = window.location.pathname;

menuItems.forEach((item) => {
  const href = item.getAttribute("href");

  if (currentPath.includes(href.replace("./", ""))) {
    item.classList.add("active");
  }

  item.addEventListener("click", () => {
    menuItems.forEach((menu) => menu.classList.remove("active"));
    item.classList.add("active");
  });
});