import { CodeInputRow } from "../common/components";
import { id } from "../common/utils";

const codeInput = id("register-code") as CodeInputRow;
const resendBtn = id('resend-btn') as HTMLButtonElement;
const message = id('verify-message')!;

codeInput.addEventListener('complete', async () => {
    const code = codeInput.value;
    if (!/^[0-9]{6}$/.test(code)) {
        message.textContent = 'Enter the 6-digit code.';
        await codeInput.animateError();
        return;
    }
    message.textContent = '';
    try {
        const res = await fetch(`/api/auth/verify?code=${code}`);
        if (res.ok) {
            message.style.color = '#27ae60';
            message.textContent = 'Email подтвержден!';
            await codeInput.animateSuccess();
            location.href = '/account/login';
        } else {
            message.style.color = '#e74c3c';
            const data = await res.json();
            message.textContent = data.detail || 'Неверный код';
            await codeInput.animateError();
        }
    } catch (e) {
        message.style.color = '#e74c3c';
        message.textContent = 'Неизвестная ошибка';
        await codeInput.animateError();
    }
});

resendBtn.onclick = async () => {
    resendBtn.disabled = true;
    resendBtn.textContent = 'Отправка...';
    const params = new URLSearchParams(location.search);
    const email = params.get('email');
    if (!email) {
        message.textContent = 'Нет email';
        return;
    }
    await fetch('/api/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    resendBtn.textContent = 'Отправить заново';
    resendBtn.disabled = false;
    message.style.color = '#27ae60';
    message.textContent = 'Код отправлен заново!';
};