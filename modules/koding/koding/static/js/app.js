document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-menu-toggle]");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const nav = document.querySelector("[data-nav]");

  const tutup = () => {
    if (sidebar) sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("show");
    if (nav) nav.classList.remove("open");
  };

  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      const buka = sidebar.classList.toggle("open");
      if (overlay) overlay.classList.toggle("show", buka);
      if (nav) nav.classList.toggle("open", buka);
    });
  }
  if (overlay) {
    overlay.addEventListener("click", tutup);
  }
  if (sidebar) {
    sidebar.addEventListener("click", (ev) => {
      if (ev.target.closest("a")) tutup();
    });
  }

  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((el) => {
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transition = "opacity .4s";
      setTimeout(() => el.remove(), 400);
    }, 4500);
  });
});
