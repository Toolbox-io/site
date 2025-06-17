// Account page functionality
import {Utils} from "../common.js";
import id = Utils.id;
import delay = Utils.delay;

class AccountManager {
    private readonly passwordDialog = id("password-dialog");
    private readonly loading = id("loading");
    private readonly errorMessage = id("error-message");
    private readonly usernameDisplay = id("username-display");
    private readonly emailDisplay = id("email-display");
    private readonly createdAtDisplay = id("created-at-display");
    private readonly userInfo = id("user-info");
    private readonly logoutBtn = id("logout-btn");
    private readonly changePasswordBtn = id("change-password-btn");
    private readonly cancelBtn = id("cancel-btn");
    private readonly passwordForm = id("password-form") as HTMLFormElement;
    private readonly currentPassword = id("current-password") as HTMLInputElement;
    private readonly newPassword = id("new-password") as HTMLInputElement;
    private readonly confirmPassword = id("confirm-password") as HTMLInputElement;
    private readonly dialogError = id("dialog-error");
    private readonly submitButton = document.querySelector('.dialog-button:not(.secondary)') as HTMLButtonElement;

    private readonly token: string | null;

    constructor() {
        this.token = localStorage.getItem('authToken');
        this.init();
    }

    private async init(): Promise<void> {
        if (!this.token) {
            window.location.href = '/login';
            return;
        }

        await this.loadUserInfo();
        this.setupEventListeners();
    }

    private async loadUserInfo(): Promise<void> {
        try {
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                
                this.usernameDisplay.textContent = user.username;
                this.emailDisplay.textContent = user.email;
                this.createdAtDisplay.textContent = new Date(user.created_at).toLocaleDateString();
                
                this.loading.style.display = 'none';
                this.userInfo.style.display = 'block';
            } else {
                // Token is invalid, redirect to login
                localStorage.removeItem('authToken');
                window.location.href = '/login';
            }
        } catch (error) {
            this.errorMessage.textContent = 'Failed to load account information';
            this.errorMessage.style.display = 'block';
            this.loading.style.display = 'none';
        }
    }

    private setupEventListeners(): void {
        // Logout functionality
        this.logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('authToken');
            window.dispatchEvent(new Event('authStateChanged'));
            window.location.href = '/';
        });

        // Password change dialog
        this.changePasswordBtn.addEventListener('click', () => {
            this.openPasswordDialog();
        });

        this.cancelBtn.addEventListener('click', () => {
            this.closePasswordDialog();
        });

        // Close dialog when clicking outside
        this.passwordDialog.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.closePasswordDialog();
            }
        });

        // Password change form submission
        this.passwordForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handlePasswordChange();
        });
    }

    private async closePasswordDialog() {
        this.passwordDialog.style.opacity = "0";
        await delay(500);
        this.passwordDialog.style.display = 'none';
        this.passwordForm.reset();
        this.dialogError.style.display = 'none';
    }

    private async openPasswordDialog() {
        this.passwordDialog.style.display = 'flex';
        await delay(1);
        this.passwordDialog.style.opacity = "1";
    }

    private async handlePasswordChange(): Promise<void> {
        const currentPassword = this.currentPassword.value;
        const newPassword = this.newPassword.value;
        const confirmPassword = this.confirmPassword.value;
        
        // Clear previous error
        this.dialogError.style.display = 'none';
        
        // Validate passwords match
        if (newPassword !== confirmPassword) {
            this.dialogError.textContent = 'New passwords do not match';
            this.dialogError.style.display = 'block';
            return;
        }
        
        // Validate password length
        if (newPassword.length < 6) {
            this.dialogError.textContent = 'New password must be at least 6 characters long';
            this.dialogError.style.display = 'block';
            return;
        }
        
        this.submitButton.disabled = true;
        this.submitButton.textContent = 'Changing...';
        
        try {
            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show success message
                this.dialogError.textContent = 'Password changed successfully!';
                this.dialogError.className = 'success-message';
                this.dialogError.style.display = 'block';
                
                // Close dialog after 2 seconds
                setTimeout(() => {
                    this.closePasswordDialog();
                    this.dialogError.className = 'error-message';
                }, 2000);
            } else {
                this.dialogError.textContent = data.detail || 'Failed to change password';
                this.dialogError.style.display = 'block';
            }
        } catch (error) {
            this.dialogError.textContent = 'Network error. Please try again.';
            this.dialogError.style.display = 'block';
        } finally {
            this.submitButton.disabled = false;
            this.submitButton.textContent = 'Change Password';
        }
    }
}

// Initialize account manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AccountManager();
}); 