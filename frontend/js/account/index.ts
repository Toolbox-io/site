/**
 * Account Management Script
 * Detects the current page and runs appropriate functionality
 */

import { changeUrl, id, setUpTabs } from "../common/utils";

// Types and interfaces
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
    access_token?: string
}

type PageType = 'login' | 'register' | 'account';

/**
 * Detect which page we're on based on URL path
 */
function detectPage(): PageType {
    const path = location.pathname;
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
        location.href = '/account/';
        return;
    }

    const loginBtn = id('login-btn') as HTMLButtonElement;
    const errorMessage = id('error-message')!;
    const verifiedDialog = id("verified-dialog")!;

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
                location.href = '/account';
            } else {
                showError(errorMessage, data.error || 'Не удалось войти');
            }
        } catch (error) {
            showError(errorMessage, 'Неизвестная ошибка');
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
        location.href = '/account/';
        return;
    }

    const registerBtn = id('register-btn') as HTMLButtonElement;
    const errorMessage = id('error-message')!;

    registerBtn.addEventListener('click', async () => {
        const username = (id('username') as HTMLInputElement).value.trim();
        const email = (id('email') as HTMLInputElement).value.trim();
        const password = (id('password') as HTMLInputElement).value;
        const confirmPassword = (id('confirm-password') as HTMLInputElement).value;
        if (password !== confirmPassword) {
            showError(errorMessage, 'Пароли не совпадают');
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
                location.href = `/account/register-code.html?email=${encodeURIComponent(email)}`;
            } else {
                showError(errorMessage, data.error || 'Не удалось зарегистрироваться');
            }
        } catch (error) {
            showError(errorMessage, 'Неизвестная ошибка');
        }
    });
}

/**
 * Initialize account dashboard functionality
 */
async function initAccount(): Promise<void> {
    if (!await checkAuthStatus()) {
        location.href = '/account/login';
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
            id('error-message')!,
            'Не удалось загрузить информацию об аккаунте'
        );
    }
}

/**
 * Setup event listeners for account dashboard
 */
function setupEventListeners(): void {
    const logoutBtn = id('logout-btn') as HTMLButtonElement;
    const changePasswordBtn = id('change-password-btn') as HTMLButtonElement;
    const passwordDialog = id('password-dialog')!;
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
            location.href = '/account/login';
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

    id("verified-close")!.addEventListener("click", closeVerifiedDialog);
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
    const dialogError = id('dialog-error')!;
    const submitButton = id('change-password-btn') as HTMLButtonElement;

    if (!currentPassword || !newPassword || !confirmPassword) {
        await showDialogError(dialogError, 'Заполните все поля');
        return;
    }

    if (newPassword !== confirmPassword) {
        await showDialogError(dialogError, 'Пароли не совпадают');
        return;
    }

    if (newPassword.length < 6) {
        await showDialogError(dialogError, 'Пароль должен быть как минимум 8 символов длины');
        return;
    }

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Изменение...';
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
            await showDialogError(dialogError, 'Пароль изменен успешно!', 'success');
            setTimeout(() => {
                closePasswordDialog();
            }, 2000);
        } else {
            await showDialogError(dialogError, data.error || 'Не удалось сменить пароль');
        }
    } catch (error) {
        await showDialogError(dialogError, 'Неизвестная ошибка');
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Сменить пароль';
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