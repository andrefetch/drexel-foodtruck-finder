// File refactored on 04/07/26 @ 6:58 PM by Andre Nunes da Silva

let currentTotal = 0; // to count money total, to calculate how much you would spend.

// Go look through the HTML and give me the element whose id is equal to menu panel
const menuPanel = document.getElementById("menu-panel");
// Does this with all of it, and then stores it in these variables
const menuContent = document.getElementById("menu-content");
const closeBtn = document.getElementById("close-menu");
const lightModeBox = document.getElementById("light-mode-box");
// This adds the open class to the panel
function openMenuPanel() {
  menuPanel.classList.add("open");
  lightModeBox?.classList.add("shifted");
  document.getElementById("slider-box")?.classList.add("shifted");
}

// Removes the open class, goes back to default
function closeMenuPanel() {
  menuPanel.classList.remove("open");
  lightModeBox?.classList.remove("shifted");
  document.getElementById("slider-box")?.classList.remove("shifted");
}

// When the user clicks the x, the panel closes
closeBtn.addEventListener("click", closeMenuPanel);

// Andre Nunes da Silva 05/23/26
menuContent.addEventListener("click", (event) => {
  const item = event.target.closest(".menu-item");
  if (!item) return;
  addToTotal(item.dataset.name, item.dataset.price);
});

// HTML-escape user-supplied values before they go into innerHTML / attributes.
// Andre Nunes da Silva 05/23/26
function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// Spawns a ripple at the cursor position so the user gets visible feedback
// for every click inside the menu area.
// Andre Nunes da Silva 05/23/26
menuPanel.addEventListener("click", (event) => {
  const ripple = document.createElement("span");
  ripple.className = "menu-click-ripple";
  const panelRect = menuPanel.getBoundingClientRect();
  const x = event.clientX - panelRect.left + menuPanel.scrollLeft;
  const y = event.clientY - panelRect.top + menuPanel.scrollTop;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  menuPanel.appendChild(ripple);
  ripple.addEventListener("animationend", () => ripple.remove());
});

function showMenu(truckId) {
  //Calls the open panel function
  openMenuPanel();
  // This is only temporary text while it is fetching the data
  menuContent.innerHTML = "<p>Loading...</p>";
  // Sends a request to the route number
  fetch(`/api/trucks/${truckId}/menu`)
    // Converts the JSON into JS objects
    .then(res => res.json())
    //Passes menu items to renderer
    .then(data => renderMenu(data));
}

function renderMenu(items) {
  // If we didn't import the menu yet, it will say it isn't available
  // This is better than having blank text
  if (items.length === 0) {
    menuContent.innerHTML = "<p>No menu available.</p>";
    return;
  }
  // Empty String to build
  let html = "";
  // Loops over each menu item
  items.forEach(item => {
    // Builds HTML using menu data. Name + price live on data-* so the
    // delegated click handler can read them without inline JS.
    const safeName = escapeHtml(item.name);
    const safePrice = escapeHtml(item.price);
    html += `
    <div class="menu-item" role="button" data-name="${safeName}" data-price="${safePrice}">
        <h4>
            <span>${safeName}</span>
            <span class='price'>$${safePrice}</span>
            </h4>
      </div>
    `;
  });
  //Adds to the html the bottom of the menu: the basket list of selected
  //items followed by the running total.
  html += `
  </div>
  <div id="receipt-bottom">
  <div id="basket-list"></div>
  <div class="total-row">
    <span>Estimated Total:</span>
    <span id="grand-total">$0.00</span>
</div>
<button id="clear-calc" onclick="resetTotal()">
<i class="fas fa-trash-alt" style="margin-right: 5px;"></i> Clear Receipt
</button>
</div>
`;
  // Injects HTML into the panel
  menuContent.innerHTML = html;
  currentTotal = 0; // resets when a user refreshes or new time they load website
}