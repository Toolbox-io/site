import { TioInput } from "../common/components";
import { id } from "../common/utils";

id('submit')!.addEventListener("click", async (e: Event) => {
    e.preventDefault();
    const email = (id("email") as TioInput).value;
    const res = await fetch('/api/auth/request-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    });
    const data = await res.json();
    id('reset-request-message')!.textContent =
        data.success ?
            'Проверьте ваш email, там код сброса' :
            'Ошибка при отправке кода.';
    if (data.success) {
        open("/reset-password");
    }
});