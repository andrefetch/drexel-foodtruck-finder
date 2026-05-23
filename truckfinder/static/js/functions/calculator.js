// File refactored on 04/07/26 @ 6:58 PM by Andre Nunes da Silva

//Adds the price of a food item to the total price of your order, updates the
//running total, and appends the item to the basket list so the user can see
//everything they have selected so far.
function addToTotal(name, price) {
    const numericPrice = parseFloat(price);
    currentTotal += numericPrice;
    const totalDisplay = document.getElementById('grand-total');

    // Updates text, rounds to 2nd decimal place
    totalDisplay.innerText = `$${currentTotal.toFixed(2)}`;

    totalDisplay.style.transform = "scale(1.2)";
    totalDisplay.style.color = "#2ecc71"; // Turn green briefly
    setTimeout(() => {
        totalDisplay.style.transform = "scale(1)";
    }, 150);

    // Appends a row to the basket. textContent keeps user-supplied names safe.
    const basketList = document.getElementById('basket-list');
    if (basketList) {
        const row = document.createElement('div');
        row.className = 'basket-item';
        const nameCell = document.createElement('span');
        nameCell.className = 'basket-item-name';
        nameCell.textContent = name;
        const priceCell = document.createElement('span');
        priceCell.className = 'basket-item-price';
        priceCell.textContent = `$${numericPrice.toFixed(2)}`;

        // Per-item remove button. The row stores its own price so removal
        // doesn't have to re-parse the displayed string.
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'basket-item-remove';
        removeBtn.setAttribute('aria-label', `Remove ${name}`);
        removeBtn.textContent = '✕';
        row.dataset.price = String(numericPrice);
        removeBtn.addEventListener('click', () => removeBasketItem(row));

        row.appendChild(nameCell);
        row.appendChild(priceCell);
        row.appendChild(removeBtn);
        basketList.appendChild(row);
    }
}

// Removes one basket row, subtracts its price from the running total, and
// briefly flashes the total red so the change is visible.
function removeBasketItem(row) {
    const price = parseFloat(row.dataset.price);
    if (!Number.isNaN(price)) {
        currentTotal = Math.max(0, currentTotal - price);
        const totalDisplay = document.getElementById('grand-total');
        if (totalDisplay) {
            totalDisplay.innerText = `$${currentTotal.toFixed(2)}`;
            totalDisplay.style.transform = "scale(1.2)";
            totalDisplay.style.color = "#e74c3c";
            setTimeout(() => {
                totalDisplay.style.transform = "scale(1)";
            }, 150);
        }
    }
    row.remove();
}

//Sets the total value of items ordered to 0 and empties the basket list
function resetTotal() {
    currentTotal = 0;
    document.getElementById('grand-total').innerText = "$0.00";
    const basketList = document.getElementById('basket-list');
    if (basketList) basketList.innerHTML = "";
}