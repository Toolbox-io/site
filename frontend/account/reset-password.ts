// Get token from URL
import {Components, Utils} from "../common.js";
import id = Utils.id;
import TioInput = Components.TioInput;

(async () => {
    const submit = id("submit");
    const newPassword = id("new-password") as TioInput;
    const confirmPassword = id("confirm-password") as TioInput;
    const message = id("reset-password-message");

    const urlParams = new URLSearchParams(location.search);
    const token = urlParams.get('token') || '';

    if (
        !(
            await fetch(
                "/check-reset",
                {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token })
                }
            )
        ).ok
    ) {
        location.replace("/error/403or401")
    }

    submit.addEventListener("click", async e => {
        e.preventDefault();

        if (newPassword.value != confirmPassword.value) {
            message.textContent = "Passwords don't match";
            return;
        }

        const res = await fetch('/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(
                {
                    token: token,
                    new_password: newPassword.value
                }
            )
        });
        const data = await res.json();
        message.textContent = data.success ? 'Password reset successful!' : 'Error resetting password.';
    });
})()
