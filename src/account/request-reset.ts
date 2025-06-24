import {Components, Utils} from "../common.js";
import id = Utils.id;
import TioInput = Components.TioInput;

(() => {
    id('submit').addEventListener("click", async e => {
        e.preventDefault();
        const email = (id("email") as TioInput).value;
        const res = await fetch('/request-reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        });
        const data = await res.json();
        id('reset-request-message')!.textContent = data.success ? 'Check your email for a reset link.' : 'Error sending reset link.';
    });
})();