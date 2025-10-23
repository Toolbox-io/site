import { marked } from "marked";
import { TioHeader } from "./components";
import hljs from "highlight.js";
import xml from "highlight.js/lib/languages/xml";

export type MarkdownHeader = { [key: string]: string }

export function getMarkdownHeader(markdown: string): MarkdownHeader {
    const headerRegex = /---\n((?:[^:\n]+:[^:\n]+\n)+)---/;
    const match = markdown.match(headerRegex);

    if (!match) return {};

    const headerContent = match[1];
    const lines = headerContent.split('\n');
    const properties: { [key: string]: string } = {};

    for (const line of lines) {
        const [key, value] = line.split(':').map(part => part.trim());
        properties[key] = value;
    }

    return properties;
}

export function getElementY(querySelector: string): number {
    return scrollY + query(querySelector).getBoundingClientRect().top;
}

export function smoothScroll(element: string, duration: number): void {
    const startingY = scrollY;
    const elementY = getElementY(element);
    // If element is close to page's bottom then window will scroll only to some position above the element.
    const targetY = document.body.scrollHeight - elementY < innerHeight ? document.body.scrollHeight - innerHeight : elementY;
    const diff = targetY - startingY;
    // Easing function: easeInOutCubic
    // From: https://gist.github.com/gre/1650294
    const easing = function (t: number): number {
        return t < .5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
    };
    let start: number;

    if (!diff) return;

    // Bootstrap our animation - it will get called right before next frame shall be rendered.
    requestAnimationFrame(function step(timestamp) {
        if (!start) start = timestamp;
        // Elapsed miliseconds since start of scrolling.
        const time = timestamp - start;
        // Get percent of completion in range [0, 1].
        let percent = Math.min(time / duration, 1);
        // Apply the easing.
        // It can cause bad-looking slow frames in browser performance tool, so be careful.
        percent = easing(percent);

        scrollTo(0, startingY + diff * percent);

        // Proceed with animation as long as we wanted it to.
        if (time < duration) {
            requestAnimationFrame(step);
        }
    });
}

export function delay(millis: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, millis));
}

export type Tab = 0 | 1 | 2

export async function switchTab(tab: Tab) {
    switch (tab) {
        case 0: open("/", "_self"); break;
        case 1: open(`/download`, "_self"); break;
        case 2: open(`/guides`, "_self"); break;
    }
}

export function setUpTabs() {
    const header = query("tio-header") as TioHeader;
    header.tabs[0].addEventListener("click", () => switchTab(0));
    header.tabs[1].addEventListener("click", () => switchTab(1));
    header.tabs[2].addEventListener("click", () => switchTab(2));
}

export async function loadMarkdown(file: string, element: HTMLElement = document.body): Promise<any> {
    if (file === "" || !file.endsWith(".md")) {
        throw new SyntaxError(`Invalid file ${file}`)
    }

    let text = await (await fetch(file)).text();
    const header = getMarkdownHeader(text);
    text = text.replace(/^---(.|\n)*?^---/gm, '');
    text = text.replace(
        /^([\t ]*)> \[!(IMPORTANT|TIP|NOTE|WARNING)]\n((\s*>.*)*)/gm,
        `$1> [!$2]\n$1>\n$3`
    );
    element.innerHTML = await marked.parse(text);

    // apply styles
    element.querySelectorAll("blockquote > p:first-child").forEach(
        (element: Element) => {
            const match: null | RegExpMatchArray = element.innerHTML.match(/^\[!(IMPORTANT|TIP|WARNING|NOTE)]$/);
            if (match != null) {
                const label = match[1].toLowerCase();

                element.classList.add(label);
                if (label === "tip") {
                    element.innerHTML = "Совет";
                } else if (label === "important") {
                    element.innerHTML = "Важно";
                } else if (label === "note") {
                    element.innerHTML = "Примечание";
                } else if (label === "warning") {
                    element.innerHTML = "Внимание";
                }

                const icon = document.createElement("span");
                icon.classList.add("material-symbols");
                if (label === "tip") {
                    icon.textContent = "lightbulb_2";
                } else if (label === "important") {
                    icon.textContent = "feedback";
                } else if (label === "note") {
                    icon.textContent = "info";
                } else if (label === "warning") {
                    icon.textContent = "warning";
                }

                element.insertAdjacentElement("afterbegin", icon);
            }
        }
    );

    element.querySelectorAll("img").forEach(
        (element: HTMLImageElement) => {
            element.loading = "lazy";
            element.addEventListener("load", () => {
                element.classList.add("loaded");
            });
        }
    );

    element.querySelectorAll("table").forEach((el) => {
        const div = document.createElement("div");
        el.insertAdjacentElement("beforebegin", div);
        div.appendChild(el);
    });

    hljs.highlightAll();

    return header
}

export function changeUrl(newUrl: string) {
    history.pushState({}, "", newUrl);
}

export function id(id: string): HTMLElement | undefined {
    return document.getElementById(id)!
}

export function query(query: string, element: Element | Document = document) {
    return element.querySelector(query)! as HTMLElement;
}

export function decodeErrorMessage(message: string): string {
    const regex = /^code (\d+):(.*)$/g;
    const match = regex.exec(message);

    if (match) {
        const code = Number(match[1])
        const decoded_message = match[2]

        switch (code) {
            // code 1 doesn't exist
            case 2: return "Имя должно быть не меньше 3 символа";
            case 3: return "Имя должно быть не больше 50 символов";
            case 4: return "Имя может содержать только буквы, цифры, нижние подчеркивания и тире";
            case 5: return "Email должен быть не больше 254 символов";
            case 6: return "Имя не может быть пустым";
            // code 7 doesn't exist
            case 8: return "Пароль не может быть пустым";
            case 9: return "Пароль должен быть не меньше 8 символов";
            case 10: return "Пароль должен быть не больше 128 символов";
            case 11: return "Пароль слишком частый, попробуйте сделать его посложнее";
            case 12: return "Пароль должен содержать буквы, цифвы и специальные символы";
            // end of codes
        }

        return decoded_message
    }

    return message
}

hljs.registerLanguage("xml", xml);