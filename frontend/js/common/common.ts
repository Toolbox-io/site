import { delay } from "./utils";
import "./components";

// hover fix
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


addEventListener("load", async () => {
    document.body.classList.add("loaded");
    await delay(500);
    document.body.classList.add("full_loaded");
});