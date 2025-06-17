import {Utils} from "../common.js";
import id = Utils.id;
import query = Utils.query;

(() => {
    const loginForm = id("loginForm");
    const username_field = id("username") as HTMLInputElement;
    const password_field = id("password") as HTMLInputElement;
    const submitButton = query(".auth-button") as HTMLButtonElement;
    const errorMessage = id("error-message");

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = username_field.value;
        const password = password_field.value;

        // Clear previous messages
        errorMessage.style.display = 'none';
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({username, password})
            });

            const data = await response.json();

            if (response.ok) {
                // Store token
                localStorage.setItem('authToken', data.access_token);

                // Dispatch custom event to update header
                window.dispatchEvent(new Event('authStateChanged'));

                // Show success message
                errorMessage.textContent = 'Login successful! Redirecting...';
                errorMessage.className = 'success-message';
                errorMessage.style.display = 'block';

                // Redirect to account page
                setTimeout(() => {
                    window.location.href = '/account';
                }, 1000);
            } else {
                // Show error message
                errorMessage.textContent = data.detail || 'Login failed';
                errorMessage.className = 'error-message';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            errorMessage.textContent = 'Network error. Please try again.';
            errorMessage.className = 'error-message';
            errorMessage.style.display = 'block';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Login';
        }
    });
})()