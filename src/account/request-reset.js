"use strict";
document.getElementById('reset-request-form').onsubmit = async function (e) {
    e.preventDefault();
    const form = this;
    const email = form.elements.namedItem('email').value;
    const res = await fetch('/request-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    const data = await res.json();
    document.getElementById('reset-request-message').textContent = data.success ? 'Check your email for a reset link.' : 'Error sending reset link.';
};
