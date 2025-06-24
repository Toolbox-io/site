import { Utils } from "../common.js";
var id = Utils.id;
(() => {
    const submit = id("submit");
    const newPassword = id("new-password");
    const confirmPassword = id("confirm-password");
    const message = id("reset-password-message");
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token') || '';
    if (!(await fetch("/check-reset", {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
    })).ok) {
    }
    submit.addEventListener("click", async (e) => {
        e.preventDefault();
        if (newPassword.value != confirmPassword.value) {
            message.textContent = "Passwords don't match";
            return;
        }
        const res = await fetch('/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: token,
                new_password: newPassword.value
            })
        });
        const data = await res.json();
        message.textContent = data.success ? 'Password reset successful!' : 'Error resetting password.';
    });
})();
