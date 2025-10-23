import $ from "jquery";

let _applied = false

export class TioHeader extends HTMLElement {
    static observedAttributes = ["tab"];
    private readonly internals;

    get tabs(): HTMLDivElement[] {
        return Array.from(this.shadowRoot!!.querySelector("#tabs")!!.children) as HTMLDivElement[];
    }

    // TODO account icon
    constructor() {
        super();
        const shadow = this.attachShadow({mode: "open"});
        // noinspection CssUnknownTarget
        shadow.innerHTML = `
            <style>@import url(/css/components/header.scss);</style>
            <div class="icon appicon"></div>
            <div class="title">Toolbox.io</div>
            <div class="separator"></div>
            <div id="tabs">
                <div class="tab" id="home">Главная</div>
                <div class="tab" id="download">Скачать</div>
                <div class="tab" id="guides">Гайды</div>
            </div>
            <md-icon-button id="auth-link">account_circle</md-icon-button>
        `;
        this.shadowRoot!!.querySelector(".icon.appicon")!!.addEventListener("click", () => {
            open("/", "_self");
        });
        
        // Add auth link functionality
        const authLink = this.shadowRoot!!.querySelector("#auth-link") as HTMLElement;
        authLink.addEventListener("click", () => {
            const token = localStorage.getItem('authToken');
            if (token) {
                open("/account", "_self");
            } else {
                open("/account/login", "_self");
            }
        });
        
        this.internals = this.attachInternals();
        try {
            $(window).on('scroll', () => {
                if ($(window).scrollTop()!! + $(window).height()!! >= 0 && $(window).scrollTop() !== 0) {
                    this.internals.states.add("scrolled");
                } else {
                    this.internals.states.delete("scrolled");
                }
            });
        } catch (e) {
            console.log(e);
        }
    }

    // noinspection JSUnusedGlobalSymbols
    attributeChangedCallback(name: string, oldValue: string, newValue: string) {
        switch (name) {
            case "tab": {
                const tabs = this.shadowRoot!!.querySelector("#tabs")!!.children;
                tabs[Number(oldValue)].classList.remove("selected");
                tabs[Number(newValue)].classList.add("selected");
            }
        }
    }
}
export class TioFooter extends HTMLElement {
    constructor() {
        super();
        const shadow = this.attachShadow({mode: "open"});
        // noinspection CssUnknownTarget
        shadow.innerHTML = `
            <style>@import url(/css/components/footer.scss);</style>
            <div class="footer_column">
                <div class="footer_title">Toolbox.io</div>
                <a href="/" draggable="false">Главная</a>
                <a href="/guides" draggable="false">Гайды</a>
                <a href="/compatibility" draggable="false">Совместимость</a>
                <a href="/download" draggable="false">Скачать</a>
            </div>
            <div class="footer_column">
                <div class="footer_title">Документы</div>
                <a href="/privacy" draggable="false">Политика конфиденциальности</a>
                <a href="https://github.com/Toolbox-io/Toolbox-io/tree/main/LICENSE" draggable="false">Лицензия</a>
            </div>
            <div class="footer_column">
                <div class="footer_title">Ресурсы</div>
                <a href="https://github.com/Toolbox-io/Toolbox-io" draggable="false">Репозиторий на GitHub</a>
                <a href="https://github.com/orgs/Toolbox-io/projects/1" draggable="false">Проект на GitHub</a>
            </div>
        `;
        shadow.querySelectorAll(".footer_column a").forEach((el) => {
            const a = el as HTMLAnchorElement;
            const regex = /^(?!\/)(.+?)\/*$/;
            if (a.href.replace(regex, "$1/") === location.href.replace(regex, "$1/")) {
                a.classList.add("selected");
                a.addEventListener("click", (e) => e.preventDefault());
            }
        });
    }
}

export class TioInput extends HTMLElement {
    static observedAttributes = ['type', 'label', 'name', 'value', 'required'];
    private input: HTMLInputElement;
    private readonly toggleBtn: HTMLButtonElement | null = null;
    private readonly icon: HTMLElement | null = null;

    constructor() {
        super();
        const shadow = this.attachShadow({mode: "open"});
        const type = this.getAttribute('type') || 'text';
        const label = this.getAttribute('label') || '';
        const name = this.getAttribute('name') || '';
        const value = this.getAttribute('value') || '';
        const required = this.hasAttribute('required');

        shadow.innerHTML = `
            <style>@import url(/css/components/input.scss);</style>
            <div class="input-group">
              <input type="${type}" name="${name}" ${required ? 'required' : ''} value="${value}" placeholder="${label}">
              ${type === 'password' ? `
              <button type="button" class="toggle-password" tabindex="-1" aria-label="Show password">
                <span class="material-symbols filled">visibility</span>
              </button>` : ''}
            </div>
        `;
        this.input = shadow.querySelector('input')!;
        if (type === 'password') {
            this.toggleBtn = shadow.querySelector('.toggle-password');
            this.icon = this.toggleBtn?.querySelector('.material-symbols.filled') || null;
            if (this.toggleBtn && this.icon) {
                this.toggleBtn.addEventListener('click', () => {
                    if (this.input.type === 'password') {
                        this.input.type = 'text';
                        this.icon!.textContent = 'visibility_off';
                    } else {
                        this.input.type = 'password';
                        this.icon!.textContent = 'visibility';
                    }
                });
            }
        }
    }
    // noinspection JSUnusedGlobalSymbols
    attributeChangedCallback(name: string, _oldValue: string, newValue: string) {
        if (!this.shadowRoot) return;
        if (name === 'type') {
            this.input.type = newValue;
        } else if (name === 'label') {
            const labelEl = this.shadowRoot.querySelector('label');
            if (labelEl) labelEl.textContent = newValue;
        } else if (name === 'name') {
            this.input.name = newValue;
        } else if (name === 'value') {
            this.input.value = newValue;
        } else if (name === 'required') {
            if (this.hasAttribute('required')) this.input.setAttribute('required', '');
            else this.input.removeAttribute('required');
        }
    }
    // noinspection JSUnusedGlobalSymbols
    get value() { return this.input.value; }
    set value(val: string) { this.input.value = val; }
}

export class CodeInputRow extends HTMLElement {
    private inputs: HTMLInputElement[];
    constructor() {
        super();
        const shadow = this.attachShadow({mode: "open"});
        shadow.innerHTML = `
            <style>@import url(/css/components/code-input.scss);</style>
            <div class="code-input-row">
                <input class="code-digit-input" id="code-0" type="text" maxlength="1" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" />
                <input class="code-digit-input" id="code-1" type="text" maxlength="1" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" />
                <input class="code-digit-input" id="code-2" type="text" maxlength="1" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" />
                <input class="code-digit-input" id="code-3" type="text" maxlength="1" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" />
                <input class="code-digit-input" id="code-4" type="text" maxlength="1" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" />
                <input class="code-digit-input" id="code-5" type="text" maxlength="1" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" />
            </div>
        `;
        this.inputs = Array.from(shadow.querySelectorAll('input')) as HTMLInputElement[];
        this.inputs.forEach((input, idx) => {
            input.addEventListener('input', () => {
                // Only allow one digit, and only 0-9
                let v = input.value.replace(/[^0-9]/g, '');
                if (v.length > 1) v = v[0];
                input.value = v;
                if (v && idx < 5) this.inputs[idx+1].focus();
                // Autosubmit: fire 'complete' event when all 6 digits are filled
                if (this.value.length === 6 && /^[0-9]{6}$/.test(this.value)) {
                    this.dispatchEvent(new CustomEvent('complete', {bubbles: true, composed: true}));
                }
            });
            input.addEventListener('keydown', (e: KeyboardEvent) => {
                if (e.key === 'Backspace') {
                    if (!input.value && idx > 0) {
                        this.inputs[idx-1].focus();
                    } else {
                        input.value = '';
                    }
                }
            });
            input.addEventListener('paste', (e: ClipboardEvent) => {
                const data = e.clipboardData?.getData('text') || '';
                if (/^[0-9]{6}$/.test(data)) {
                    e.preventDefault();
                    for (let i = 0; i < 6; ++i) {
                        this.inputs[i].value = data[i];
                    }
                    this.inputs[5].focus();
                    this.dispatchEvent(new CustomEvent('complete', {bubbles: true, composed: true}));
                }
            });
        });
    }
    connectedCallback() {
        // Autofocus the first input when the component is added to the DOM
        setTimeout(() => this.inputs[0].focus(), 0);
    }
    get value() {
        return this.inputs.map(input => input.value).join('');
    }
    set value(val: string) {
        for (let i = 0; i < 6; ++i) {
            this.inputs[i].value = val[i] || '';
        }
    }
    private setColor(color: string) {
        this.inputs.forEach(input => {
            (input as HTMLElement).style.backgroundColor = color;
            (input as HTMLElement).style.transition = 'background 0.3s';
        });
    }
    private shake() {
        const row = this.shadowRoot!.querySelector('.code-input-row')! as HTMLElement;
        row.classList.remove('shake');
        void row.offsetWidth;
        row.classList.add('shake');
    }
    async animateSuccess() {
        this.setColor('#99ff99');
        await new Promise(r => setTimeout(r, 900));
        this.setColor('');
    }
    async animateError() {
        this.setColor('#ff5757');
        this.shake();
        await new Promise(r => setTimeout(r, 400));
        this.setColor('');
    }
}

if (!_applied) {
    customElements.define("tio-header", TioHeader);
    customElements.define("tio-footer", TioFooter);
    customElements.define("tio-input", TioInput);
    customElements.define("code-input-row", CodeInputRow);
    _applied = true
}