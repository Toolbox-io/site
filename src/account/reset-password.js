"use strict";
const urlParams = new URLSearchParams(window.location.search);
document.getElementById('token').value = urlParams.get('token') || '';
document.getElementById('reset-password-form').onsubmit = async function (e) {
    e.preventDefault();
    const form = this;
    const new_password = form.elements.namedItem('new_password').value;
    const token = form.elements.namedItem('token').value;
    const res = await fetch('/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password })
    });
    const data = await res.json();
    document.getElementById('reset-password-message').textContent = data.success ? 'Password reset successful!' : 'Error resetting password.';
};
