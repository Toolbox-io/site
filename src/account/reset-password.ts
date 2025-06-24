// Get token from URL
const urlParams = new URLSearchParams(window.location.search);
(document.getElementById('token') as HTMLInputElement).value = urlParams.get('token') || '';

document.getElementById('reset-password-form')!.onsubmit = async function(e) {
    e.preventDefault();
    const form = this as HTMLFormElement;
    const new_password = (form.elements.namedItem('new_password') as HTMLInputElement).value;
    const token = (form.elements.namedItem('token') as HTMLInputElement).value;
    const res = await fetch('/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password })
    });
    const data = await res.json();
    document.getElementById('reset-password-message')!.textContent = data.success ? 'Password reset successful!' : 'Error resetting password.';
}; 