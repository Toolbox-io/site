// noinspection JSUnusedLocalSymbols

import {Utils} from "../../common.js";

import delay = Utils.delay;
import loadMarkdown = Utils.loadMarkdown;
import setUpTabs = Utils.setUpTabs;
import changeUrl = Utils.changeUrl;

export type GuideHeader = {
    "DisplayName": string,
    "Icon": string
}

export type GuideEntry = {
    name: string,
    header: GuideHeader
}

export type GuideJSON = GuideEntry[];

await (async () => {
    let _currentPage: 0 | 1 = 0;

    function sizeElements() {
        let biggestElement: HTMLDivElement | null = null
        const wrapper = document.getElementsByClassName("wrapper")[0] as HTMLDivElement;
        Array.from(wrapper.children).forEach((element) => {
            if (biggestElement !== null && biggestElement.getBoundingClientRect().height < element.getBoundingClientRect().height) {
                biggestElement = element as HTMLDivElement;
            }
            if (biggestElement === null) {
                biggestElement = element as HTMLDivElement;
            }
            console.log(element);
        });
        if (biggestElement !== null) {
            wrapper.style.height = `${(biggestElement as HTMLDivElement).getBoundingClientRect().height}px`
        }
    }

    async function switchPage(page: 0 | 1) {
        const wrapper = document.getElementsByClassName("wrapper")[0] as HTMLDivElement;

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

    async function fetchGuidesList(): Promise<GuideJSON> {
        const response = await fetch("/guides/list");
        if (!response.ok) throw new Error("Failed to fetch guides list");
        return await response.json();
    }

    setUpTabs();
    sizeElements();

    const guides = document.getElementById("guides_list") as HTMLDivElement;

    document.getElementById("guide_back")!!.addEventListener("click", async () => {
        await switchPage(0);
        document.getElementById("guide")!!.innerHTML = "";
        changeUrl("/guides");
    });

    window.addEventListener("popstate", async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const selectedGuide = urlParams.get('guide');
        if (selectedGuide !== null) {
            try {
                await loadMarkdown(selectedGuide, document.getElementById("guide")!!);
            } catch (e) {
                await loadMarkdown("ERROR.md", document.getElementById("guide")!!);
            }
            await switchPage(1);
        } else {
            // If no guide param, go back to the list view
            await switchPage(0);
            document.getElementById("guide")!!.innerHTML = "";
        }
    });

    // Render guides list
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
            changeUrl(`/guides/?guide=${entry.name}`);

            await loadMarkdown(entry.name, document.getElementById("guide")!!);
            await switchPage(1);
        });
        sizeElements();
    }

    // Load the guide
    const urlParams = new URLSearchParams(window.location.search);
    const selectedGuide = urlParams.get('guide');
    if (selectedGuide !== null) {
        try {
            await loadMarkdown(selectedGuide, document.getElementById("guide")!!);
        } catch (e) {
            await loadMarkdown("ERROR.md", document.getElementById("guide")!!);
        }
        await switchPage(1);
    }
})()