/**
 * Account Management Script
 * Detects the current page and runs appropriate functionality
 */

'use strict';

// Types and interfaces
import {Utils} from "../common.js";
import id = Utils.id;
import setUpTabs = Utils.setUpTabs;
import changeUrl = Utils.changeUrl;

interface UserData {
    username: string;
    email: string;
    created_at: string;
}

interface LoginCredentials {
    username: string;
    password: string;
}

interface RegisterData {
    username: string;
    email: string;
    password: string;
}

interface PasswordChangeData {
    current_password: string;
    new_password: string;
}

interface ApiResponse<T = any> {
    data?: T;
    error?: string;
    message?: string;
    access_token?: string;
    token_type?: string;
}

type PageType = 'login' | 'register' | 'account';

(() => {
    /**
     * Detect which page we're on based on URL path
     */
    function detectPage(): PageType {
        const path = window.location.pathname;
        if (path.includes('/login')) return 'login';
        if (path.includes('/register')) return 'register';
        return 'account'; // Default to account dashboard
    }

    /**
     * Initialize the appropriate functionality based on current page
     */
    function init(): void {
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

    /**
     * Initialize login page functionality
     */
    async function initLogin() {
        if (await checkAuthStatus()) {
            window.location.href = '/account/';
            return;
        }

        const loginBtn = id('login-btn') as HTMLButtonElement;
        const errorMessage = id('error-message');
        const verifiedDialog = id("verified-dialog");

        loginBtn.addEventListener('click', async () => {
            const username = (id('username') as HTMLInputElement).value;
            const password = (id('password') as HTMLInputElement).value;
            const credentials: LoginCredentials = { username, password };
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(credentials),
                });
                const data: ApiResponse = await response.json();
                if (response.ok) {
                    localStorage.setItem('authToken', data.access_token || '');
                    window.location.href = '/account';
                } else {
                    showError(errorMessage, data.error || 'Login failed');
                }
            } catch (error) {
                showError(errorMessage, 'Network error. Please try again.');
            }
        });

        // Close dialog when clicking outside
        verifiedDialog.addEventListener('click', e => {
            if (e.target === verifiedDialog) {
                closePasswordDialog();
            }
        });

        const params = new URLSearchParams(location.search);
        if (params.get("verified") === "true") {
            await openVerifiedDialog();
            changeUrl("/account/login");
        }
    }

    /**
     * Initialize register page functionality
     */
    async function initRegister() {
        if (await checkAuthStatus()) {
            window.location.href = '/account/';
            return;
        }

        const registerBtn = id('register-btn') as HTMLButtonElement;
        const errorMessage = id('error-message');

        registerBtn.addEventListener('click', async () => {
            const username = (id('username') as HTMLInputElement).value.trim();
            const email = (id('email') as HTMLInputElement).value.trim();
            const password = (id('password') as HTMLInputElement).value;
            const confirmPassword = (id('confirm-password') as HTMLInputElement).value;
            if (password !== confirmPassword) {
                showError(errorMessage, 'Passwords do not match');
                return;
            }
            const registerData: RegisterData = { username, email, password };
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(registerData),
                });
                const data: ApiResponse = await response.json();
                if (response.ok) {
                    await showVerifyDialog(email);
                } else {
                    showError(errorMessage, data.error || 'Registration failed');
                }
            } catch (error) {
                showError(errorMessage, 'Network error. Please try again.');
            }
        });
    }

    async function showVerifyDialog(email: string) {
        const dialog = id('verify-dialog')!;
        const message = id('verify-dialog-message')!;
        const resendBtn = id('resend-btn')!;

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
            // Optionally show a toast or update the dialog to say "Sent!"
        });
    }

    /**
     * Initialize account dashboard functionality
     */
    async function initAccount(): Promise<void> {
        if (!await checkAuthStatus()) {
            window.location.href = '/account/login';
            return;
        }
        setupEventListeners();
        await loadUserInfo();
    }

    /**
     * Check if user is authenticated
     */
    async function checkAuthStatus(): Promise<boolean> {
        const token = localStorage.getItem('authToken');
        try {
            const response = await fetch('/api/auth/check-auth', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    /**
     * Load and display user information
     */
    async function loadUserInfo(): Promise<void> {
        const token = localStorage.getItem('authToken');
        try {
            const response = await fetch('/api/auth/user-info', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const userData: UserData = await response.json();

            if (response.ok) {
                const usernameDisplay = id('username-display');
                const emailDisplay = id('email-display');
                const createdAtDisplay = id('created-at-display');
                const loading = id('loading');
                const userInfo = id('user-info');

                if (usernameDisplay) usernameDisplay.textContent = userData.username;
                if (emailDisplay) emailDisplay.textContent = userData.email;
                if (createdAtDisplay) {
                    createdAtDisplay.textContent = new Date(userData.created_at).toLocaleDateString();
                }

                // Show user info and hide loading
                if (loading) loading.style.display = 'none';
                if (userInfo) userInfo.style.display = 'block';
            }
        } catch (error) {
            console.error('Failed to load user info:', error);
            showError(
                id('error-message'),
                'Failed to load account information'
            );
        }
    }

    /**
     * Setup event listeners for account dashboard
     */
    function setupEventListeners(): void {
        const logoutBtn = id('logout-btn') as HTMLButtonElement;
        const changePasswordBtn = id('change-password-btn') as HTMLButtonElement;
        const passwordDialog = id('password-dialog');
        const cancelBtn = id('cancel-btn') as HTMLButtonElement;
        const changePasswordSubmitBtn = id('change-password-btn2') as HTMLButtonElement;

        logoutBtn.addEventListener('click', handleLogout);

        changePasswordBtn.addEventListener('click', () => {
            openPasswordDialog();
        });

        cancelBtn.addEventListener('click', () => {
            closePasswordDialog();
        });

        changePasswordSubmitBtn.addEventListener('click', (e: Event) => {
            e.preventDefault();
            console.log("called!!!");
            handlePasswordChange();
        });

        // Close dialog when clicking outside
        passwordDialog.addEventListener('click', (e: Event) => {
            if (e.target === passwordDialog) {
                closePasswordDialog();
            }
        });
    }

    /**
     * Handle logout
     */
    async function handleLogout(): Promise<void> {
        try {
            const response = await fetch(
                '/api/auth/logout',
                {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("authToken")}`
                    }
                }
            );
            if (response.ok) {
                localStorage.removeItem('authToken');
                window.location.href = '/account/login';
            }
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }

    /**
     * Open password change dialog
     */
    async function openPasswordDialog(): Promise<void> {
        const passwordDialog = id('password-dialog');
        if (passwordDialog) {
            passwordDialog.style.display = 'flex';
            await delay(1);
            passwordDialog.style.opacity = '1';
        }
    }

    /**
     * Close password change dialog
     */
    async function closePasswordDialog(): Promise<void> {
        const passwordDialog = id('password-dialog');

        if (passwordDialog) {
            passwordDialog.style.opacity = '0';
            await delay(500);
            passwordDialog.style.display = 'none';
        }

        (id('current-password') as HTMLInputElement).value = '';
        (id('new-password') as HTMLInputElement).value = '';
        (id('confirm-password') as HTMLInputElement).value = '';
    }

    /**
     * Open password change dialog
     */
    async function openVerifiedDialog(): Promise<void> {
        const verifiedDialog = id('verified-dialog');
        if (verifiedDialog) {
            verifiedDialog.style.display = 'flex';
            await delay(1);
            verifiedDialog.style.opacity = '1';
        }

        id("verified-close").addEventListener("click", closeVerifiedDialog);
    }

    /**
     * Close password change dialog
     */
    async function closeVerifiedDialog(): Promise<void> {
        const verifiedDialog = id('verified-dialog');

        if (verifiedDialog) {
            verifiedDialog.style.opacity = '0';
            await delay(500);
            verifiedDialog.style.display = 'none';
        }
    }

    /**
     * Handle password change
     */
    async function handlePasswordChange(): Promise<void> {
        const currentPassword = (id('current-password') as HTMLInputElement)?.value;
        const newPassword = (id('new-password') as HTMLInputElement)?.value;
        const confirmPassword = (id('confirm-password') as HTMLInputElement)?.value;
        const dialogError = id('dialog-error');
        const submitButton = id('change-password-btn') as HTMLButtonElement;

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
            const passwordData: PasswordChangeData = {
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

            const data: ApiResponse = await response.json();

            if (response.ok) {
                await showDialogError(dialogError, 'Password changed successfully!', 'success');
                setTimeout(() => {
                    closePasswordDialog();
                }, 2000);
            } else {
                await showDialogError(dialogError, data.error || 'Failed to change password');
            }
        } catch (error) {
            await showDialogError(dialogError, 'Network error. Please try again.');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Change Password';
            }
        }
    }

    /**
     * Show error message with animation
     */
    function showError(element: HTMLElement, message: string): void {
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

    /**
     * Show dialog error message
     */
    async function showDialogError(element: HTMLElement, message: string, type: 'error' | 'success' = 'error'): Promise<void> {
        console.debug('[DialogError] showDialogError called:', { message, type });
        element.textContent = message;
        element.className = type === 'success' ? 'success-message' : 'error-message';
        // Animate height
        element.classList.add('visible');
        console.debug('[DialogError] .visible class added');
        // Remove after 3s if error
        if (type === 'error') {
            await delay(3000);
            element.classList.remove('visible');
            console.debug('[DialogError] .visible class removed');
        }
    }

    /**
     * Utility function for delays
     */
    function delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', init);
})(); 