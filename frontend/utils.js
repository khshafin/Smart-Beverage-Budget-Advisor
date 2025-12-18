// API Configuration
const API_URL = 'http://127.0.0.1:5002/api';

// Get current user from localStorage
function getCurrentUser() {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');

    if (token && userId && username) {
        return { id: parseInt(userId), username, token };
    }
    return null;
}

// Check if user is authenticated
function requireAuth() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = 'index.html';
        return null;
    }
    return user;
}

// Sign out
function signOut() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// UI Helpers
function showSpinner() {
    const spinner = document.getElementById('spinner');
    if (spinner) spinner.style.display = 'flex';
}

function hideSpinner() {
    const spinner = document.getElementById('spinner');
    if (spinner) spinner.style.display = 'none';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = message;
        toast.className = `toast ${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
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

// Order drink (global function)
async function orderDrink(beverageId, name, price) {
    const currentUser = getCurrentUser();
    if (!currentUser) {
        showToast('Please sign in first', 'error');
        return;
    }

    const selectedMood = localStorage.getItem('selectedMood');
    if (!selectedMood) {
        showToast('Please select your mood first', 'error');
        return;
    }

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
            // Reload budget if on recommendations page
            if (typeof loadWeeklySpending === 'function') {
                loadWeeklySpending();
            }
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
