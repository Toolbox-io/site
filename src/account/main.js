'use strict';
import { Utils } from "../common.js";
var id = Utils.id;
var setUpTabs = Utils.setUpTabs;
(() => {
    function detectPage() {
        const path = window.location.pathname;
        if (path.includes('/login'))
            return 'login';
        if (path.includes('/register'))
            return 'register';
        return 'account';
    }
    function init() {
        setUpTabs();
        const currentPage = detectPage();
        switch (currentPage) {
            case 'login':
                initLogin();
                break;
            case 'register':
                initRegister();
                break;
            case 'account':
                initAccount();
                break;
        }
    }
    async function initLogin() {
        if (await checkAuthStatus()) {
            window.location.href = '/account/';
            return;
        }
        const loginForm = id('loginForm');
        const errorMessage = id('error-message');
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const credentials = {
                username: formData.get('username'),
                password: formData.get('password')
            };
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(credentials),
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('authToken', data.access_token || '');
                    window.location.href = '/account';
                }
                else {
                    showError(errorMessage, data.error || 'Login failed');
                }
            }
            catch (error) {
                showError(errorMessage, 'Network error. Please try again.');
            }
        });
    }
    async function initRegister() {
        if (await checkAuthStatus()) {
            window.location.href = '/account/';
            return;
        }
        const registerForm = id('registerForm');
        const errorMessage = id('error-message');
        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(registerForm);
                const password = formData.get('password');
                const confirmPassword = formData.get('confirm-password');
                const username = formData.get("username").trim();
                const email = formData.get("email").trim();
                if (password !== confirmPassword) {
                    showError(errorMessage, 'Passwords do not match');
                    return;
                }
                const registerData = {
                    username: username,
                    email: email,
                    password: password
                };
                try {
                    const response = await fetch('/api/auth/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(registerData),
                    });
                    const data = await response.json();
                    if (response.ok) {
                        window.location.href = '/account/login';
                    }
                    else {
                        showError(errorMessage, data.error || 'Registration failed');
                    }
                }
                catch (error) {
                    showError(errorMessage, 'Network error. Please try again.');
                }
            });
        }
    }
    async function initAccount() {
        if (!await checkAuthStatus()) {
            window.location.href = '/account/login';
            return;
        }
        setupEventListeners();
        await loadUserInfo();
    }
    async function checkAuthStatus() {
        const token = localStorage.getItem('authToken');
        try {
            const response = await fetch('/api/auth/check-auth', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            return response.ok;
        }
        catch (error) {
            return false;
        }
    }
    async function loadUserInfo() {
        const token = localStorage.getItem('authToken');
        try {
            const response = await fetch('/api/auth/user-info', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const userData = await response.json();
            if (response.ok) {
                const usernameDisplay = id('username-display');
                const emailDisplay = id('email-display');
                const createdAtDisplay = id('created-at-display');
                const loading = id('loading');
                const userInfo = id('user-info');
                if (usernameDisplay)
                    usernameDisplay.textContent = userData.username;
                if (emailDisplay)
                    emailDisplay.textContent = userData.email;
                if (createdAtDisplay) {
                    createdAtDisplay.textContent = new Date(userData.created_at).toLocaleDateString();
                }
                if (loading)
                    loading.style.display = 'none';
                if (userInfo)
                    userInfo.style.display = 'block';
            }
        }
        catch (error) {
            console.error('Failed to load user info:', error);
            showError(id('error-message'), 'Failed to load account information');
        }
    }
    function setupEventListeners() {
        const logoutBtn = id('logout-btn');
        const changePasswordBtn = id('change-password-btn');
        const passwordDialog = id('password-dialog');
        const cancelBtn = id('cancel-btn');
        const passwordForm = id('password-form');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', handleLogout);
        }
        if (changePasswordBtn) {
            changePasswordBtn.addEventListener('click', () => {
                openPasswordDialog();
            });
        }
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                closePasswordDialog();
            });
        }
        if (passwordForm) {
            passwordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                handlePasswordChange();
            });
        }
        if (passwordDialog) {
            passwordDialog.addEventListener('click', (e) => {
                if (e.target === passwordDialog) {
                    closePasswordDialog();
                }
            });
        }
    }
    async function handleLogout() {
        try {
            const response = await fetch('/api/auth/logout', { method: 'POST' });
            if (response.ok) {
                localStorage.removeItem('authToken');
                window.location.href = '/account/login';
            }
        }
        catch (error) {
            console.error('Logout failed:', error);
        }
    }
    async function openPasswordDialog() {
        const passwordDialog = id('password-dialog');
        if (passwordDialog) {
            passwordDialog.style.display = 'flex';
            await delay(1);
            passwordDialog.style.opacity = '1';
        }
    }
    async function closePasswordDialog() {
        const passwordDialog = id('password-dialog');
        const passwordForm = id('password-form');
        const dialogError = id('dialog-error');
        if (passwordDialog) {
            passwordDialog.style.opacity = '0';
            await delay(500);
            passwordDialog.style.display = 'none';
        }
        if (passwordForm)
            passwordForm.reset();
        if (dialogError)
            dialogError.style.display = 'none';
    }
    async function handlePasswordChange() {
        const currentPassword = id('current-password')?.value;
        const newPassword = id('new-password')?.value;
        const confirmPassword = id('confirm-password')?.value;
        const dialogError = id('dialog-error');
        const submitButton = document.querySelector('.dialog-button:not(.secondary)');
        if (!currentPassword || !newPassword || !confirmPassword) {
            showDialogError(dialogError, 'All fields are required');
            return;
        }
        if (newPassword !== confirmPassword) {
            showDialogError(dialogError, 'New passwords do not match');
            return;
        }
        if (newPassword.length < 6) {
            showDialogError(dialogError, 'New password must be at least 6 characters long');
            return;
        }
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Changing...';
        }
        try {
            const passwordData = {
                current_password: currentPassword,
                new_password: newPassword
            };
            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(passwordData),
            });
            const data = await response.json();
            if (response.ok) {
                showDialogError(dialogError, 'Password changed successfully!', 'success');
                setTimeout(() => {
                    closePasswordDialog();
                }, 2000);
            }
            else {
                showDialogError(dialogError, data.error || 'Failed to change password');
            }
        }
        catch (error) {
            showDialogError(dialogError, 'Network error. Please try again.');
        }
        finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Change Password';
            }
        }
    }
    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
        element.classList.add('error-show');
        setTimeout(() => {
            element.classList.remove('error-show');
            setTimeout(() => {
                element.style.display = 'none';
            }, 300);
        }, 3000);
    }
    function showDialogError(element, message, type = 'error') {
        element.textContent = message;
        element.className = type === 'success' ? 'success-message' : 'error-message';
        element.style.display = 'block';
    }
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    document.addEventListener('DOMContentLoaded', init);
})();
