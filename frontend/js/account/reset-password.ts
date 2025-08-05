import {Components, Utils} from "../common.js";
import id = Utils.id;
import CodeInputRow = Components.CodeInputRow;

(() => {
    const codeInput = id("reset-code") as CodeInputRow;
    const submit = id("submit") as HTMLButtonElement;
    const newPassword = id("new-password") as HTMLInputElement;
    const confirmPassword = id("confirm-password") as HTMLInputElement;
    const message = id("reset-password-message");

    codeInput.addEventListener('complete', () => submit.click());

    submit.addEventListener("click", async e => {
        e.preventDefault();
        const code = codeInput.value;
        if (newPassword.value != confirmPassword.value) {
            message.textContent = "Passwords don't match";
            await codeInput.animateError();
            return;
        }
        if (!/^[0-9]{6}$/.test(code)) {
            message.textContent = "Enter the 6-digit code from your email.";
            await codeInput.animateError();
            return;
        }
        message.textContent = '';
        submit.disabled = true;
        try {
            const res = await fetch('/api/auth/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: code,
                    new_password: newPassword.value
                })
            });
            const data = await res.json();
            if (res.ok) {
                message.style.color = '#27ae60';
                message.textContent = 'Password reset successful! Redirecting...';
                await codeInput.animateSuccess();
                location.href = '/account/login';
            } else {
                message.style.color = '#e74c3c';
                message.textContent = data.detail || 'Error resetting password.';
                await codeInput.animateError();
            }
        } catch (e) {
            message.style.color = '#e74c3c';
            message.textContent = 'Network error.';
            await codeInput.animateError();
        } finally {
            submit.disabled = false;
        }
    });
})();
