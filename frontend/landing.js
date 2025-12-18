// Landing page (index.html) JavaScript

// Check if already logged in
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token) {
        // Redirect to recommendations if already logged in
        window.location.href = 'recommendations.html';
        return;
    }

    setupEventListeners();
});

let isSignUp = false;

function setupEventListeners() {
    const authBtn = document.getElementById('authBtn');
    const authModal = document.getElementById('authModal');
    const authForm = document.getElementById('authForm');
    const toggleAuthLink = document.getElementById('toggleAuth');
    const closeModal = document.getElementsByClassName('close')[0];
    const getStartedBtn = document.getElementById('getStartedBtn');

    // Sign In button - opens modal in sign in mode
    authBtn.addEventListener('click', () => {
        console.log('Sign In button clicked');
        // Ensure we're in Sign In mode
        isSignUp = false;
        updateFormMode();
        authModal.style.display = 'block';
        console.log('Modal display set to:', authModal.style.display);
    });

    // Get Started button - opens modal in sign up mode
    getStartedBtn.addEventListener('click', () => {
        console.log('Get Started button clicked');
        // Ensure we're in Sign Up mode
        isSignUp = true;
        updateFormMode();
        authModal.style.display = 'block';
        console.log('Modal display set to:', authModal.style.display);
    });

    // Close modal
    closeModal.addEventListener('click', () => {
        authModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            authModal.style.display = 'none';
        }
    });

    // Toggle between sign in and sign up
    toggleAuthLink.addEventListener('click', (e) => {
        e.preventDefault();
        toggleAuthMode();
    });

    // Form submission
    authForm.addEventListener('submit', handleAuth);
}

function toggleAuthMode() {
    isSignUp = !isSignUp;
    updateFormMode();
}

function updateFormMode() {
    const authTitle = document.getElementById('authTitle');
    const emailGroup = document.getElementById('emailGroup');
    const budgetGroup = document.getElementById('budgetGroup');
    const toggleAuthLink = document.getElementById('toggleAuth');
    const authToggleText = document.getElementById('authToggleText');
    const submitBtn = document.querySelector('button[type="submit"]');

    if (isSignUp) {
        authTitle.textContent = 'Sign Up';
        emailGroup.style.display = 'block';
        budgetGroup.style.display = 'block';
        toggleAuthLink.textContent = 'Sign In';
        authToggleText.textContent = 'Already have an account? ';
        submitBtn.textContent = 'Sign Up';
    } else {
        authTitle.textContent = 'Sign In';
        emailGroup.style.display = 'none';
        budgetGroup.style.display = 'none';
        toggleAuthLink.textContent = 'Sign Up';
        authToggleText.textContent = "Don't have an account? ";
        submitBtn.textContent = 'Sign In';
    }
}

async function handleAuth(e) {
    e.preventDefault();

    const spinner = document.getElementById('spinner');
    const toast = document.getElementById('toast');
    spinner.style.display = 'flex';

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;
    const weeklyBudget = document.getElementById('weeklyBudget').value || 25.0;

    try {
        const endpoint = isSignUp ? '/register' : '/login';
        const body = isSignUp
            ? { username, email, password, weekly_budget: parseFloat(weeklyBudget) }
            : { username, password };

        const response = await fetch(`http://127.0.0.1:5002/api${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (response.ok) {
            if (isSignUp) {
                toast.textContent = 'Account created successfully! Please sign in.';
                toast.className = 'toast success show';
                setTimeout(() => toast.classList.remove('show'), 3000);
                toggleAuthMode();
            } else {
                localStorage.setItem('token', data.token);
                localStorage.setItem('userId', data.user_id);
                localStorage.setItem('username', data.username);
                window.location.href = 'recommendations.html';
            }
        } else {
            toast.textContent = data.message || 'Authentication failed';
            toast.className = 'toast error show';
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
    } catch (error) {
        toast.textContent = 'Connection error. Please try again.';
        toast.className = 'toast error show';
        setTimeout(() => toast.classList.remove('show'), 3000);
        console.error('Auth error:', error);
    } finally {
        spinner.style.display = 'none';
    }
}
