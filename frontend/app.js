// API Configuration
const API_URL = 'http://127.0.0.1:5002/api';

// State Management
let currentUser = null;
let selectedMood = null;
let isSignUp = false;

// DOM Elements
const authBtn = document.getElementById('authBtn');
const authModal = document.getElementById('authModal');
const authForm = document.getElementById('authForm');
const authTitle = document.getElementById('authTitle');
const toggleAuthLink = document.getElementById('toggleAuth');
const emailGroup = document.getElementById('emailGroup');
const budgetGroup = document.getElementById('budgetGroup');
const closeModal = document.getElementsByClassName('close')[0];
const getStartedBtn = document.getElementById('getStartedBtn');
const getStartedLandingBtn = document.getElementById('getStartedLandingBtn');
const navLinks = document.querySelectorAll('.nav-link');
const spinner = document.getElementById('spinner');
const toast = document.getElementById('toast');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Note: authBtn click handler is set dynamically in updateAuthUI()

    closeModal.addEventListener('click', () => {
        authModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            authModal.style.display = 'none';
        }
    });

    toggleAuthLink.addEventListener('click', (e) => {
        e.preventDefault();
        toggleAuthMode();
    });

    authForm.addEventListener('submit', handleAuth);

    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = e.target.getAttribute('href').substring(1);
            navigateTo(target);
        });
    });

    // Landing "Get Started" - opens sign up
    getStartedLandingBtn.addEventListener('click', () => {
        if (!isSignUp) {
            toggleAuthMode(); // Switch to sign up mode
        }
        authModal.style.display = 'block';
    });

    // Home "Get Started" (after login) - goes to recommendations
    getStartedBtn.addEventListener('click', () => {
        if (currentUser) {
            navigateTo('recommend');
        }
    });

    // Mood Selection
    document.querySelectorAll('.mood-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedMood = btn.dataset.mood;
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

    // Menu Filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const category = btn.dataset.category;
            filterMenu(category);
        });
    });

    // Profile Budget Update
    const updateBudgetBtn = document.getElementById('updateBudgetBtn');
    if (updateBudgetBtn) {
        updateBudgetBtn.addEventListener('click', updateUserBudget);
    }
}

// Authentication
function toggleAuthMode() {
    isSignUp = !isSignUp;
    if (isSignUp) {
        authTitle.textContent = 'Sign Up';
        emailGroup.style.display = 'block';
        budgetGroup.style.display = 'block';
        toggleAuthLink.textContent = 'Sign In';
        toggleAuthLink.previousElementSibling.textContent = 'Already have an account? ';
        authForm.querySelector('button[type="submit"]').textContent = 'Sign Up';
    } else {
        authTitle.textContent = 'Sign In';
        emailGroup.style.display = 'none';
        budgetGroup.style.display = 'none';
        toggleAuthLink.textContent = 'Sign Up';
        toggleAuthLink.previousElementSibling.textContent = "Don't have an account? ";
        authForm.querySelector('button[type="submit"]').textContent = 'Sign In';
    }
}

async function handleAuth(e) {
    e.preventDefault();
    showSpinner();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;
    const weeklyBudget = document.getElementById('weeklyBudget').value || 25.0;

    try {
        const endpoint = isSignUp ? '/register' : '/login';
        const body = isSignUp 
            ? { username, email, password, weekly_budget: parseFloat(weeklyBudget) }
            : { username, password };

        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (response.ok) {
            if (isSignUp) {
                showToast('Account created successfully! Please sign in.', 'success');
                toggleAuthMode();
            } else {
                localStorage.setItem('token', data.token);
                localStorage.setItem('userId', data.user_id);
                localStorage.setItem('username', data.username);
                currentUser = { id: data.user_id, username: data.username };
                authModal.style.display = 'none';
                updateAuthUI();
                showToast('Welcome back, ' + data.username + '!', 'success');
                navigateTo('recommend');
            }
        } else {
            showToast(data.message || 'Authentication failed', 'error');
        }
    } catch (error) {
        showToast('Connection error. Please try again.', 'error');
        console.error('Auth error:', error);
    } finally {
        hideSpinner();
    }
}

function checkAuth() {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');

    if (token && userId && username) {
        currentUser = { id: parseInt(userId), username };
        // If user is already logged in, show recommendations page by default
        updateAuthUI();
        navigateTo('recommend');
    } else {
        // If not logged in, show landing page
        updateAuthUI();
    }
}

function updateAuthUI() {
    const navLinks = document.querySelectorAll('.nav-link');
    const landingSection = document.getElementById('landing');
    const homeSection = document.getElementById('home');

    if (currentUser) {
        authBtn.textContent = 'Sign Out';
        authBtn.onclick = signOut;
        // Show navigation links when logged in
        navLinks.forEach(link => {
            link.style.display = 'inline-block';
        });
        // Hide both landing and home hero sections by default
        // User will be on recommendations page
        landingSection.style.display = 'none';
        homeSection.style.display = 'none';
    } else {
        authBtn.textContent = 'Sign In';
        authBtn.onclick = () => {
            // Make sure we're in sign in mode, not sign up
            if (isSignUp) {
                toggleAuthMode();
            }
            authModal.style.display = 'block';
        };
        // Hide navigation links when not logged in
        navLinks.forEach(link => {
            link.style.display = 'none';
        });
        // Show landing section, hide home
        landingSection.style.display = 'block';
        homeSection.style.display = 'none';
    }
}

function signOut() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    currentUser = null;
    updateAuthUI();
    // Show landing section after sign out
    document.getElementById('landing').style.display = 'block';
    document.getElementById('home').style.display = 'none';
    // Hide other sections
    document.querySelectorAll('section:not(#landing)').forEach(s => s.style.display = 'none');
    showToast('Signed out successfully', 'success');
}

// Navigation
function navigateTo(section) {
    // Hide all sections including landing
    document.querySelectorAll('section').forEach(s => s.style.display = 'none');

    // Show target section
    const targetSection = document.getElementById(section);
    if (targetSection) {
        targetSection.style.display = 'block';
    }

    // Update nav links
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + section) {
            link.classList.add('active');
        }
    });

    // Load section-specific data
    if (section === 'recommend' && currentUser) {
        loadWeeklySpending();
    } else if (section === 'menu') {
        loadMenu();
    } else if (section === 'profile' && currentUser) {
        loadProfile();
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
    if (!currentUser) {
        showToast('Please sign in first', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/purchase/weekly-spending/${currentUser.id}`);
        const data = await response.json();

        if (response.ok) {
            const remaining = data.remaining;
            const suggestedBudget = Math.min(remaining * 0.8, 10); // 80% of remaining or $10
            
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

// Order Drink
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
            loadWeeklySpending(); // Refresh budget
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

// Menu
async function loadMenu(category = null) {
    showSpinner();

    try {
        let url = `${API_URL}/beverages`;
        const response = await fetch(url);
        const data = await response.json();

        if (response.ok) {
            displayMenu(data.beverages, category);
        }
    } catch (error) {
        showToast('Error loading menu', 'error');
        console.error('Menu error:', error);
    } finally {
        hideSpinner();
    }
}

function displayMenu(beverages, category = null) {
    const gridDiv = document.getElementById('menuGrid');
    gridDiv.innerHTML = '';

    let filteredBeverages = beverages;
    if (category && category !== 'all') {
        filteredBeverages = beverages.filter(b => b.category === category);
    }

    filteredBeverages.forEach(drink => {
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

// Profile
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
            loadWeeklySpending();
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
    spinner.style.display = 'flex';
}

function hideSpinner() {
    spinner.style.display = 'none';
}

function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
