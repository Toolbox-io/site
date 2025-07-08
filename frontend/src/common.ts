import { marked } from "marked";
import hljs from 'highlight.js';
import xml from 'highlight.js/lib/languages/xml';

// noinspection JSUnusedGlobalSymbols
export var exports = {}

export namespace Utils {
    import _query = Utils.query;
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

    export function getElementY(query: string): number {
        return scrollY + _query(query).getBoundingClientRect().top;
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

    export async function loadMarkdown(file: string, element: HTMLElement = document.body): Promise<any> {
        if (file === "" || !file.endsWith(".md")) {
            throw new SyntaxError(`Invalid file ${file}`)
        }

        let text = await (await fetch(file)).text();
        console.log(text);
        const header = getMarkdownHeader(text);
        text = text.replace(/^---(.|\n)*?^---/gm, '');
        console.log(text);
        text = text.replace(
            /^([\t ]*)> \[!(IMPORTANT|TIP|NOTE|WARNING)]\n((\s*>.*)*)/gm,
            `$1> [!$2]\n$1>\n$3`
        );
        console.log(text);
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

    export function id(id: string) {
        return document.getElementById(id)!!
    }

    // noinspection JSUnusedGlobalSymbols
    export function query(query: string) {
        return document.querySelector(query)!! as HTMLElement;
    }

    hljs.registerLanguage("xml", xml);
}

// noinspection JSUnusedGlobalSymbols
export namespace Cookies {
    // noinspection JSUnusedGlobalSymbols
    export function get(name: string): string | null {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            const result = parts.pop()?.split(';').shift();
            if (result === undefined) {
                return null;
            } else {
                return decodeURIComponent(result);
            }
        }
        return null;
    }

    // noinspection JSUnusedGlobalSymbols
    export function set(name: string, value: string, expiresDays: number = 7): void {
        const date = new Date();
        date.setTime(date.getTime() + (expiresDays * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${encodeURIComponent(value)};${expires};path=/`;
    }

    // noinspection JSUnusedGlobalSymbols
    export function deleteCookie(name: string): void {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }

    // noinspection JSUnusedGlobalSymbols
    export function getAll(): { [key: string]: string } {
        const cookies: { [key: string]: string } = {};
        const cookieArray = document.cookie.split(';');
        for (let i = 0; i < cookieArray.length; i++) {
            const cookiePair = cookieArray[i].split('=');
            if (cookiePair.length === 2) {
                cookies[cookiePair[0].trim()] = decodeURIComponent(cookiePair[1].trim());
            }
        }
        return cookies;
    }
}

// hover fix
(() => {
    let hasHoverClass = false;
    const container = document.body;
    let lastTouchTime = 0;

    function enableHover() {
        // filter emulated events coming from touch events
        // @ts-ignore
        if (new Date() - lastTouchTime < 500) return;
        if (hasHoverClass) return;

        container.className += ' hasHover';
        hasHoverClass = true;
    }

    function disableHover() {
        if (!hasHoverClass) return;

        container.className = container.className.replace(' hasHover', '');
        hasHoverClass = false;
    }

    function updateLastTouchTime() {
        // @ts-ignore
        lastTouchTime = new Date();
    }

    document.addEventListener('touchstart', updateLastTouchTime, true);
    document.addEventListener('touchstart', disableHover, true);
    document.addEventListener('mousemove', enableHover, true);
    enableHover();
})();

addEventListener("load", async () => {
    document.body.classList.add("loaded");
    await Utils.delay(500);
    document.body.classList.add("full_loaded");
});