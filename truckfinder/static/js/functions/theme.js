// Author: Maisha Sultana (ms5529), 05/17/26
// Feature: Light/Dark mode toggle — shared across all pages

const modeBtn = document.getElementById("mode-swap");
var isLight = false;

// Restores saved theme from localStorage when page loads
// So if user was in light mode and refreshes, it stays light
function restoreTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "light") {
        isLight = true;
        document.body.classList.add("light");
        modeBtn.innerHTML = `<i class="fas fa-moon"></i>`;

        // If on map page, also swap map tiles
        if (typeof tiles !== "undefined") {
            tiles.setUrl('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').redraw();
        }
    }
}

function swapModes() {
    if (isLight === false) {
        // Switch to light mode
        isLight = true;
        document.body.classList.add("light");
        modeBtn.innerHTML = `<i class="fas fa-moon"></i>`;
        localStorage.setItem("theme", "light");

        // Swap map tiles only if on map page
        if (typeof tiles !== "undefined") {
            tiles.setUrl('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').redraw();
        }

        // Update sidebar toggle button if on map page
        const togglePanel = document.getElementById("togglePanel");
        const sidePanel = document.getElementById("sidePanel");
        if (togglePanel && sidePanel && !sidePanel.classList.contains("open")) {
            togglePanel.classList.add("light");
        }

    } else {
        // Switch to dark mode
        isLight = false;
        document.body.classList.remove("light");
        modeBtn.innerHTML = `<i class="fas fa-sun"></i>`;
        localStorage.setItem("theme", "dark");

        // Swap map tiles only if on map page
        if (typeof tiles !== "undefined") {
            tiles.setUrl('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').redraw();
        }

        // Update sidebar toggle button if on map page
        const togglePanel = document.getElementById("togglePanel");
        const sidePanel = document.getElementById("sidePanel");
        if (togglePanel && sidePanel && !sidePanel.classList.contains("open")) {
            togglePanel.classList.remove("light");
        }
    }
}

// Attach click listener to the button
modeBtn.addEventListener('click', swapModes);

// Restore theme on every page load
restoreTheme();