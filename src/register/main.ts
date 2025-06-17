import {Utils} from "../common.js";
import id = Utils.id;
import query = Utils.query;

(() => {
    const username_field = id("username") as HTMLInputElement;
    const password_field = id("password") as HTMLInputElement;
    const confirm_password_field = id("confirm-password") as HTMLInputElement;
    const email_field = id("email") as HTMLInputElement;
    const submitButton = query(".auth-button") as HTMLButtonElement;
    const errorMessage = id("error-message");

    id('registerForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = username_field.value;
        const email = email_field.value;
        const password = password_field.value;
        const confirmPassword = confirm_password_field.value;

        // Clear previous messages
        errorMessage.style.display = 'none';

        // Validate passwords match
        if (password !== confirmPassword) {
            errorMessage.textContent = 'Passwords do not match';
            errorMessage.style.display = 'block';
            return;
        }

        // Validate password length
        if (password.length < 6) {
            errorMessage.textContent = 'Password must be at least 6 characters long';
            errorMessage.style.display = 'block';
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Registering...';

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Show success message
                errorMessage.textContent = 'Registration successful! Redirecting to login...';
                errorMessage.className = 'success-message';
                errorMessage.style.display = 'block';

                // Redirect to login page
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                // Show error message
                errorMessage.textContent = data.detail || 'Registration failed';
                errorMessage.className = 'error-message';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            errorMessage.textContent = 'Network error. Please try again.';
            errorMessage.className = 'error-message';
            errorMessage.style.display = 'block';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Register';
        }
    });
})();