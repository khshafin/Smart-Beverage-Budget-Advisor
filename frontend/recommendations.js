// Recommendations page JavaScript

const API_URL = 'http://127.0.0.1:5002/api';
let currentUser = null;
let selectedMood = null;

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
    loadWeeklySpending();
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

    // Mood Selection
    document.querySelectorAll('.mood-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedMood = btn.dataset.mood;
            localStorage.setItem('selectedMood', selectedMood);
            checkRecommendationReady();
        });
    });

    // Budget Input
    const budgetInput = document.getElementById('budgetInput');
    budgetInput.addEventListener('input', checkRecommendationReady);

    // Splurge Button
    const splurgeBtn = document.getElementById('splurgeBtn');
    splurgeBtn.addEventListener('click', handleSplurge);

    // Get Recommendations
    const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
    getRecommendationsBtn.addEventListener('click', getRecommendations);

    // Restore selected mood if exists
    const savedMood = localStorage.getItem('selectedMood');
    if (savedMood) {
        selectedMood = savedMood;
        document.querySelectorAll('.mood-btn').forEach(btn => {
            if (btn.dataset.mood === savedMood) {
                btn.classList.add('selected');
            }
        });
    }
}

// Budget Progress
async function loadWeeklySpending() {
    if (!currentUser) return;

    try {
        const response = await fetch(`${API_URL}/purchase/weekly-spending/${currentUser.id}`);
        const data = await response.json();

        if (response.ok) {
            const spentPercent = (data.spent_this_week / data.weekly_budget) * 100;

            document.getElementById('spentAmount').textContent = `$${data.spent_this_week.toFixed(2)}`;
            document.getElementById('totalBudget').textContent = `$${data.weekly_budget.toFixed(2)}`;
            document.getElementById('remainingAmount').textContent = `$${data.remaining.toFixed(2)}`;

            const progressFill = document.getElementById('progressFill');
            progressFill.style.width = `${Math.min(spentPercent, 100)}%`;

            // Update progress bar color
            progressFill.classList.remove('warning', 'danger');
            if (spentPercent > 80) {
                progressFill.classList.add('danger');
            } else if (spentPercent > 60) {
                progressFill.classList.add('warning');
            }
        }
    } catch (error) {
        console.error('Error loading weekly spending:', error);
    }
}

// Splurge Button
async function handleSplurge() {
    if (!currentUser) return;

    try {
        const response = await fetch(`${API_URL}/purchase/weekly-spending/${currentUser.id}`);
        const data = await response.json();

        if (response.ok) {
            const remaining = data.remaining;
            const suggestedBudget = Math.min(remaining * 0.8, 10);

            if (remaining < 2) {
                showToast('Budget is too tight to splurge this week!', 'error');
            } else {
                document.getElementById('budgetInput').value = suggestedBudget.toFixed(2);
                showToast(`You can splurge up to $${suggestedBudget.toFixed(2)}! 🎉`, 'success');
                checkRecommendationReady();
            }
        }
    } catch (error) {
        console.error('Error checking splurge:', error);
    }
}

// Recommendations
function checkRecommendationReady() {
    const budgetInput = document.getElementById('budgetInput').value;
    const btn = document.getElementById('getRecommendationsBtn');

    if (selectedMood && budgetInput && parseFloat(budgetInput) > 0) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    }
}

async function getRecommendations() {
    if (!currentUser || !selectedMood) return;

    const budget = document.getElementById('budgetInput').value;
    showSpinner();

    try {
        const response = await fetch(
            `${API_URL}/recommendations/${currentUser.id}?mood=${selectedMood}&budget=${budget}`
        );
        const recommendations = await response.json();

        if (response.ok && recommendations.length > 0) {
            displayRecommendations(recommendations);
            showToast('Recommendations ready!', 'success');
        } else {
            showToast('No recommendations found. Try adjusting your budget.', 'error');
        }
    } catch (error) {
        showToast('Error getting recommendations', 'error');
        console.error('Recommendation error:', error);
    } finally {
        hideSpinner();
    }
}

function displayRecommendations(recommendations) {
    const resultsDiv = document.getElementById('recommendationsResults');
    const gridDiv = document.getElementById('drinksGrid');

    gridDiv.innerHTML = '';

    recommendations.forEach((drink, index) => {
        const card = createDrinkCard(drink, true, index + 1);
        gridDiv.appendChild(card);
    });

    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
            loadWeeklySpending();
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
