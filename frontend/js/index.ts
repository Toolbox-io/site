"use strict";

import switchTab = Utils.switchTab;
import {Components, Utils} from "./common.js";
import smoothScroll = Utils.smoothScroll;
import delay = Utils.delay;
import TioHeader = Components.TioHeader;

(async () => {
    // Scrolling text functionality
    const scrollingTextElement = document.querySelector(".scrolling_text") as HTMLElement;
    if (scrollingTextElement) {
        const words = ["защиты", "кастомизации", "инструментов"];
        let currentWordIndex = 0;
        
        // Calculate the width of the widest word once
        const tempSpan = document.createElement("span");
        tempSpan.style.position = "absolute";
        tempSpan.style.visibility = "hidden";
        tempSpan.style.whiteSpace = "nowrap";
        tempSpan.style.font = window.getComputedStyle(scrollingTextElement).font;
        document.body.appendChild(tempSpan);
        
        let maxWidth = 0;
        words.forEach(word => {
            tempSpan.textContent = word;
            const width = tempSpan.offsetWidth;
            if (width > maxWidth) {
                maxWidth = width;
            }
        });
        
        document.body.removeChild(tempSpan);
        
        // Create the permanent scrolling wrapper
        const wrapper = document.createElement("div");
        wrapper.className = "scrolling-wrapper";
        wrapper.style.width = `${maxWidth}px`;
        
        // Replace the original element with the wrapper
        scrollingTextElement.parentNode?.insertBefore(wrapper, scrollingTextElement);
        scrollingTextElement.remove();
        
        // Create the first word element
        const firstWord = document.createElement("span");
        firstWord.textContent = words[0];
        firstWord.className = "scrolling-word";
        firstWord.style.top = "0";
        firstWord.style.transform = "translateY(0)";
        wrapper.appendChild(firstWord);
        
        function updateScrollingText() {
            // Get the current visible word element
            const currentWord = wrapper.querySelector(".scrolling-word") as HTMLElement;
            if (!currentWord) return;
            
            // Create the new word element (below, hidden)
            const newWord = document.createElement("span");
            newWord.textContent = words[(currentWordIndex + 1) % words.length];
            newWord.className = "scrolling-word";
            newWord.style.top = "0";
            newWord.style.transform = "translateY(100%)";
            
            wrapper.appendChild(newWord);
            
            // Start the sliding animation - both words slide up together
            setTimeout(() => {
                currentWord.style.transform = "translateY(-100%)"; // Old word slides up and out
                newWord.style.transform = "translateY(0)";     // New word slides up and into view
            }, 50);
            
            // Clean up old elements and update for next cycle
            setTimeout(() => {
                // Remove the old word element
                if (currentWord.parentNode) {
                    currentWord.parentNode.removeChild(currentWord);
                }
                currentWordIndex = (currentWordIndex + 1) % words.length;
            }, 650);
        }
        
        // Start the rotation
        setInterval(updateScrollingText, 3000);
    }

    // Set up buttons
    const header = document.querySelector("tio-header")!! as TioHeader;

    // Tabs
    header.tabs[0].addEventListener("click", () => {
        smoothScroll("body", 1000);
    });
    header.tabs[1].addEventListener("click", () => switchTab(1));
    header.tabs[2].addEventListener("click", () => switchTab(2));

    // Buttons
    document.getElementById("issues_btn")!!.addEventListener("click", () => {
        open("https://github.com/Toolbox-io/Toolbox-io/issues", "_self");
    });

    // Features cards
    const features = document.getElementById("features") as HTMLElement;
    const blur = document.getElementById("card_dialog") as HTMLDivElement;
    Array.from(features.children).forEach((item) => {
        const feature = item as HTMLDivElement
        if (!feature.classList.contains("replacement") && feature.classList.length > 0) {
            const replacement = document.createElement("div");
            const desc = feature.querySelector(".feature-description") as HTMLDivElement;
            const longDesc = feature.querySelector(".feature-long-description") as HTMLDivElement;
            const close = feature.querySelector(".feature-close") as HTMLDivElement;
            feature.addEventListener("click", async () => {
                if (!feature.classList.contains("expanded")) {
                    feature.insertAdjacentElement("afterend", replacement);
                    replacement.innerHTML = feature.innerHTML;
                    replacement.classList.add("placeholder", "feature");
                    replacement.id = `${feature.id}_placeholder`;
                    feature.classList.add("noHover");

                    blur.classList.add("open");

                    desc.style.opacity = "0";
                    desc.style.display = "none";

                    longDesc.style.display = "block";
                    longDesc.style.opacity = "1";

                    close.style.display = "block";
                    close.style.opacity = "1";
                    feature.classList.add("expanded");
                }
            })
            close.addEventListener("click", async () => {
                feature.classList.add("closing");
                longDesc.style.opacity = "0";
                close.style.opacity = "0";
                blur.style.opacity = "0";
                feature.style.opacity = "0";
                await delay(500);
                blur.classList.remove("open");
                blur.style.opacity = "";
                longDesc.style.display = "none";
                close.style.display = "none";
                desc.style.display = "block";
                desc.style.opacity = "1";
                feature.style.animation = "";
                feature.style.opacity = "1";
                feature.classList.remove("noHover", "expanded");
                Array.from(features.children).forEach(item2 => {
                    const item3 = item2 as HTMLDivElement;
                    if (item3.classList.length > 0) {
                        item3.style.width = "";
                        item3.style.height = "";
                        item3.style.boxSizing = "";
                    }
                });
                replacement.remove();
                await delay(500);
                feature.classList.remove("closing");
            })
        }
    });
})();