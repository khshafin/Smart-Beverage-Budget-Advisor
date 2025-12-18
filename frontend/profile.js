// Profile page JavaScript

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
    loadProfile();
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

    // Profile Budget Update
    const updateBudgetBtn = document.getElementById('updateBudgetBtn');
    if (updateBudgetBtn) {
        updateBudgetBtn.addEventListener('click', updateUserBudget);
    }
}

// Load Profile
async function loadProfile() {
    if (!currentUser) return;
    showSpinner();

    try {
        // Load user profile
        const profileResponse = await fetch(`${API_URL}/user/profile/${currentUser.id}`);
        const profileData = await profileResponse.json();

        if (profileResponse.ok) {
            document.getElementById('profileUsername').textContent = profileData.username;
            document.getElementById('profileEmail').textContent = profileData.email;
            document.getElementById('profileMemberSince').textContent =
                new Date(profileData.member_since).toLocaleDateString();
            document.getElementById('updateBudget').value = profileData.weekly_budget;
        }

        // Load purchase history
        const historyResponse = await fetch(`${API_URL}/purchase/history/${currentUser.id}`);
        const historyData = await historyResponse.json();

        if (historyResponse.ok) {
            displayPurchaseHistory(historyData.history);
        }
    } catch (error) {
        showToast('Error loading profile', 'error');
        console.error('Profile error:', error);
    } finally {
        hideSpinner();
    }
}

function displayPurchaseHistory(history) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';

    if (history.length === 0) {
        historyList.innerHTML = '<p style="text-align: center; color: var(--gray);">No purchase history yet</p>';
        return;
    }

    history.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-details">
                <h4>${item.beverage_name}</h4>
                <div class="history-meta">
                    ${item.mood} • ${new Date(item.date).toLocaleDateString()}
                </div>
            </div>
            <div class="history-price">$${item.price.toFixed(2)}</div>
        `;
        historyList.appendChild(historyItem);
    });
}

async function updateUserBudget() {
    if (!currentUser) return;

    const newBudget = document.getElementById('updateBudget').value;
    if (!newBudget || parseFloat(newBudget) <= 0) {
        showToast('Please enter a valid budget amount', 'error');
        return;
    }

    showSpinner();

    try {
        const response = await fetch(`${API_URL}/user/budget/${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ weekly_budget: parseFloat(newBudget) })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Budget updated successfully!', 'success');
        } else {
            showToast(data.message || 'Update failed', 'error');
        }
    } catch (error) {
        showToast('Error updating budget', 'error');
        console.error('Budget update error:', error);
    } finally {
        hideSpinner();
    }
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
