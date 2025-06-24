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
        const loginBtn = id('login-btn');
        const errorMessage = id('error-message');
        loginBtn.addEventListener('click', async () => {
            const username = id('username').value;
            const password = id('password').value;
            const credentials = { username, password };
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
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
        const registerBtn = id('register-btn');
        const errorMessage = id('error-message');
        registerBtn.addEventListener('click', async () => {
            const username = id('username').value.trim();
            const email = id('email').value.trim();
            const password = id('password').value;
            const confirmPassword = id('confirm-password').value;
            if (password !== confirmPassword) {
                showError(errorMessage, 'Passwords do not match');
                return;
            }
            const registerData = { username, email, password };
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(registerData),
                });
                const data = await response.json();
                if (response.ok) {
                    await showVerifyDialog(email);
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
    async function showVerifyDialog(email) {
        const dialog = id('verify-dialog');
        const message = id('verify-dialog-message');
        const resendBtn = id('resend-btn');
        message.textContent = `Please check your email ${email} for a verification link.`;
        if (dialog) {
            dialog.style.display = 'flex';
            await delay(1);
            dialog.style.opacity = '1';
        }
        resendBtn.addEventListener("click", async () => {
            resendBtn.setAttribute('disabled', 'true');
            resendBtn.textContent = 'Sending...';
            await fetch('/verify-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            resendBtn.textContent = 'Resend';
            resendBtn.removeAttribute('disabled');
        });
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
        const changePasswordSubmitBtn = id('change-password-btn2');
        logoutBtn.addEventListener('click', handleLogout);
        changePasswordBtn.addEventListener('click', () => {
            openPasswordDialog();
        });
        cancelBtn.addEventListener('click', () => {
            closePasswordDialog();
        });
        changePasswordSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log("called!!!");
            handlePasswordChange();
        });
        passwordDialog.addEventListener('click', (e) => {
            if (e.target === passwordDialog) {
                closePasswordDialog();
            }
        });
    }
    async function handleLogout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("authToken")}`
                }
            });
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
        if (passwordDialog) {
            passwordDialog.style.opacity = '0';
            await delay(500);
            passwordDialog.style.display = 'none';
        }
        id('current-password').value = '';
        id('new-password').value = '';
        id('confirm-password').value = '';
    }
    async function handlePasswordChange() {
        const currentPassword = id('current-password')?.value;
        const newPassword = id('new-password')?.value;
        const confirmPassword = id('confirm-password')?.value;
        const dialogError = id('dialog-error');
        const submitButton = id('change-password-btn');
        if (!currentPassword || !newPassword || !confirmPassword) {
            await showDialogError(dialogError, 'All fields are required');
            return;
        }
        if (newPassword !== confirmPassword) {
            await showDialogError(dialogError, 'New passwords do not match');
            return;
        }
        if (newPassword.length < 6) {
            await showDialogError(dialogError, 'New password must be at least 6 characters long');
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
            const token = localStorage.getItem('authToken');
            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(passwordData),
            });
            const data = await response.json();
            if (response.ok) {
                await showDialogError(dialogError, 'Password changed successfully!', 'success');
                setTimeout(() => {
                    closePasswordDialog();
                }, 2000);
            }
            else {
                await showDialogError(dialogError, data.error || 'Failed to change password');
            }
        }
        catch (error) {
            await showDialogError(dialogError, 'Network error. Please try again.');
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
    async function showDialogError(element, message, type = 'error') {
        console.debug('[DialogError] showDialogError called:', { message, type });
        element.textContent = message;
        element.className = type === 'success' ? 'success-message' : 'error-message';
        element.classList.add('visible');
        console.debug('[DialogError] .visible class added');
        if (type === 'error') {
            await delay(3000);
            element.classList.remove('visible');
            console.debug('[DialogError] .visible class removed');
        }
    }
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    document.addEventListener('DOMContentLoaded', init);
})();
