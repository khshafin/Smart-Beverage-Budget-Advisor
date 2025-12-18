// Menu page JavaScript

const API_URL = 'http://127.0.0.1:5002/api';
let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');

    if (!token || !userId || !username) {
        window.location.href = 'index.html';
        return;
    }

    currentUser = { id: parseInt(userId), username };
    setupEventListeners();
    loadMenu();
});

function setupEventListeners() {
    // Sign out
    const authBtn = document.getElementById('authBtn');
    authBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
        localStorage.removeItem('selectedMood');
        window.location.href = 'index.html';
    });

    // Menu Filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const category = btn.dataset.category;
            filterMenu(category);
        });
    });
}

// Load Menu
async function loadMenu() {
    showSpinner();

    try {
        const response = await fetch(`${API_URL}/beverages`);
        const data = await response.json();

        if (response.ok) {
            displayMenu(data.beverages);
        }
    } catch (error) {
        showToast('Error loading menu', 'error');
        console.error('Menu error:', error);
    } finally {
        hideSpinner();
    }
}

function displayMenu(beverages) {
    const gridDiv = document.getElementById('menuGrid');
    gridDiv.innerHTML = '';

    beverages.forEach(drink => {
        const card = createDrinkCard(drink, false);
        gridDiv.appendChild(card);
    });
}

function filterMenu(category) {
    const menuGrid = document.getElementById('menuGrid');
    const cards = menuGrid.querySelectorAll('.drink-card');

    cards.forEach(card => {
        if (category === 'all') {
            card.style.display = 'block';
        } else {
            const categorySpan = card.querySelector('.drink-category');
            if (categorySpan && categorySpan.textContent === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        }
    });
}

// UI Helpers
function showSpinner() {
    document.getElementById('spinner').style.display = 'flex';
}

function hideSpinner() {
    document.getElementById('spinner').style.display = 'none';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Create drink card
function createDrinkCard(drink, isRecommendation = false, rank = null) {
    const card = document.createElement('div');
    card.className = 'drink-card';

    let cardHTML = `
        <h4>${drink.name}</h4>
        <div class="drink-price">$${drink.price.toFixed(2)}</div>
    `;

    if (drink.category) {
        cardHTML += `<span class="drink-category">${drink.category}</span>`;
    }

    if (isRecommendation && rank) {
        cardHTML += `
            <div style="background: #FFD700;
                        color: white;
                        padding: 0.5rem;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        margin-bottom: 1rem;">
                #${rank} Pick for You
            </div>
        `;
    }

    if (drink.score !== undefined) {
        const scorePercent = (drink.score * 100).toFixed(0);
        cardHTML += `<div class="drink-score">Match Score: ${scorePercent}%</div>`;
    }

    if (drink.suitable_moods && drink.suitable_moods.length > 0) {
        cardHTML += '<div class="drink-moods">';
        drink.suitable_moods.forEach(mood => {
            cardHTML += `<span class="mood-tag">${mood}</span>`;
        });
        cardHTML += '</div>';
    }

    cardHTML += `
        <div class="drink-actions">
            <button class="btn-order" onclick="orderDrink(${drink.id || 1}, '${drink.name}', ${drink.price})">
                Order Now
            </button>
        </div>
    `;

    card.innerHTML = cardHTML;
    return card;
}

// Order drink
async function orderDrink(beverageId, name, price) {
    if (!currentUser) {
        showToast('Please sign in first', 'error');
        return;
    }

    const selectedMood = localStorage.getItem('selectedMood') || 'Happy';

    showSpinner();

    try {
        const response = await fetch(`${API_URL}/purchase`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUser.id,
                beverage_id: beverageId,
                mood: selectedMood,
                price: price
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`${name} ordered successfully! Enjoy! ☕`, 'success');
        } else {
            showToast(data.message || 'Order failed', 'error');
        }
    } catch (error) {
        showToast('Error placing order', 'error');
        console.error('Order error:', error);
    } finally {
        hideSpinner();
    }
}
