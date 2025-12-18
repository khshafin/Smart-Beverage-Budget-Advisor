// Home page (home.html) JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');

    if (!token || !userId || !username) {
        window.location.href = 'index.html';
        return;
    }

    setupEventListeners();
});

function setupEventListeners() {
    const authBtn = document.getElementById('authBtn');
    authBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    });
}
