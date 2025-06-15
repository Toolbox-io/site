// noinspection JSUnusedLocalSymbols
import { Utils } from "../../common.js";
var delay = Utils.delay;
var loadMarkdown = Utils.loadMarkdown;
var setUpTabs = Utils.setUpTabs;
let _currentPage = 0;
function sizeElements() {
    let biggestElement = null;
    const wrapper = document.getElementsByClassName("wrapper")[0];
    Array.from(wrapper.children).forEach((element) => {
        if (biggestElement !== null && biggestElement.getBoundingClientRect().height < element.getBoundingClientRect().height) {
            biggestElement = element;
        }
        if (biggestElement === null) {
            biggestElement = element;
        }
        console.log(element);
    });
    if (biggestElement !== null) {
        wrapper.style.height = `${biggestElement.getBoundingClientRect().height}px`;
    }
}
async function switchPage(page) {
    const wrapper = document.getElementsByClassName("wrapper")[0];
    const currentPage = wrapper.children[_currentPage];
    const targetPage = wrapper.children[page];
    currentPage.classList.add("page_hiding");
    targetPage.classList.add("notransition");
    targetPage.classList.add("page_showing");
    targetPage.classList.remove("notransition");
    targetPage.classList.remove("page_hidden");
    targetPage.classList.add("page_visible");
    await delay(500);
    currentPage.classList.remove("page_hiding");
    currentPage.classList.add("page_hidden");
    targetPage.classList.remove("page_showing");
    targetPage.classList.remove("page_visible");
    _currentPage = page;
    sizeElements();
}
setUpTabs();
sizeElements();
const guides = document.getElementById("guides_list");
document.getElementById("guide_back").addEventListener("click", async () => {
    await switchPage(0);
    document.getElementById("guide").innerHTML = "";
});
async function fetchGuidesList() {
    const response = await fetch("/guides/list");
    if (!response.ok)
        throw new Error("Failed to fetch guides list");
    return await response.json();
}
async function renderGuidesList() {
    const guidesList = await fetchGuidesList();
    guides.innerHTML = "";
    for (const entry of guidesList) {
        const guide = document.createElement("div");
        guide.classList.add("guide", "toucheffect");
        const icon = document.createElement("span");
        icon.classList.add("material-symbols", "guide_icon");
        icon.textContent = entry.header.Icon || "description";
        guide.appendChild(icon);
        const title = document.createElement("div");
        title.classList.add("guide_title");
        title.textContent = entry.header.DisplayName;
        guide.appendChild(title);
        guides.appendChild(guide);
        guide.addEventListener("click", async () => {
            await loadMarkdown(entry.name, document.getElementById("guide"));
            await switchPage(1);
        });
        sizeElements();
    }
}
renderGuidesList();
const urlParams = new URLSearchParams(window.location.search);
const selectedGuide = urlParams.get('guide');
if (selectedGuide !== null) {
    try {
        await loadMarkdown(selectedGuide, document.getElementById("guide"));
    }
    catch (e) {
        await loadMarkdown("ERROR.md", document.getElementById("guide"));
    }
    await switchPage(1);
}
