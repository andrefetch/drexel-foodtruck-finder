// Author : Andre Nunes da Silva (05/17/26)

document.addEventListener("DOMContentLoaded", () => {
  fetch("/stats/api") // fetches from a new route called /stats/api in routes.py
    .then((res) => res.json())
    .then((stats) => {
      const map = {
        "stat-trucks": stats.trucks,
        "stat-menu-items": stats.menu_items,
        "stat-cuisines": stats.cuisines,
      };
      for (const [id, value] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
      }
    })
    .catch((err) => console.error("Failed to load home stats:", err));
});
