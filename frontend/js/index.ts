import { TioHeader } from "./common/components";
import { delay, id, query, smoothScroll, switchTab } from "./common/utils";

async function scrollingText() {
    // Scrolling text functionality
    const wrapper = query("#scrolling-wrapper");
    const words = ["защиты", "кастомизации", "инструментов"];
    let currentWordIndex = 0;
    
    // Calculate the width of the widest word once
    function setWidth() {
        const tempSpan = document.createElement("span");
        tempSpan.style.position = "absolute";
        tempSpan.style.visibility = "hidden";
        tempSpan.style.whiteSpace = "nowrap";
        tempSpan.style.font = window.getComputedStyle(wrapper).font;
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
        wrapper.style.width = `${maxWidth}px`;
    }
    
    // Create the first word element
    const firstWord = document.createElement("span");
    firstWord.textContent = words[0];
    firstWord.className = "scrolling-word";
    firstWord.style.top = "0";
    firstWord.style.transform = "translateY(0)";
    wrapper.appendChild(firstWord);

    while (true) {
        setWidth();
        await delay(3000);
        
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
        
        await delay(50);
        // Start the sliding animation - both words slide up together
        currentWord.style.transform = "translateY(-100%)"; // Old word slides up and out
        newWord.style.transform = "translateY(0)";     // New word slides up and into view

        await delay(600);
        
        // Clean up old elements and update for next cycle
        Array.from(wrapper.children).forEach((item) => {
            if (item != newWord) {
                item.remove();
            }
        });
        currentWordIndex = (currentWordIndex + 1) % words.length;
    }
}

scrollingText(); // no await intentionally

// Set up header
const header = query("tio-header") as TioHeader;
header.tabs[0].addEventListener("click", () => {
    smoothScroll("body", 1000);
});
header.tabs[1].addEventListener("click", () => switchTab(1));
header.tabs[2].addEventListener("click", () => switchTab(2));

// Security items
const securityItems = document.querySelectorAll("#security_block .menu-item");
const securityDetails = document.querySelectorAll("#security_block .detail-item");

securityItems.forEach((item) => {
    const securityItem = item as HTMLDivElement;
    const featureId = securityItem.getAttribute("data-feature");
    
    securityItem.addEventListener("click", () => {
        // Remove active class from all security items
        securityItems.forEach((si) => {
            si.classList.remove("active");
        });
        
        // Add active class to clicked item
        securityItem.classList.add("active");
        
        // Hide all security details
        securityDetails.forEach((detail) => {
            detail.classList.remove("active");
        });
        
        // Show the corresponding detail
        const detailId = `${featureId}-detail`;
        const detailElement = document.getElementById(detailId);
        if (detailElement) {
            detailElement.classList.add("active");
        }
    });
});

// Show first security item by default
if (securityItems.length > 0) {
    const firstItem = securityItems[0] as HTMLDivElement;
    const firstFeatureId = firstItem.getAttribute("data-feature");
    
    firstItem.classList.add("active");
    
    if (firstFeatureId) {
        const firstDetailId = `${firstFeatureId}-detail`;
        const firstDetailElement = document.getElementById(firstDetailId);
        if (firstDetailElement) {
            firstDetailElement.classList.add("active");
        }
    }
}

// Action cards
const actionCards = document.querySelectorAll("#progress_block .menu-item");
const actionDetails = document.querySelectorAll("#progress_block .detail-item");

actionCards.forEach((item) => {
    const actionCard = item as HTMLDivElement;
    const actionId = actionCard.getAttribute("data-action");
    
    actionCard.addEventListener("click", () => {
        // Remove active class from all action cards
        actionCards.forEach((ac) => {
            ac.classList.remove("active");
        });
        
        // Add active class to clicked item
        actionCard.classList.add("active");
        
        // Hide all action details
        actionDetails.forEach((detail) => {
            detail.classList.remove("active");
        });
        
        // Show the corresponding detail
        const detailId = `${actionId}-detail`;
        const detailElement = document.getElementById(detailId);
        if (detailElement) {
            detailElement.classList.add("active");
        }
    });
});

// Show first action card by default
if (actionCards.length > 0) {
    const firstActionCard = actionCards[0] as HTMLDivElement;
    const firstActionId = firstActionCard.getAttribute("data-action");
    
    firstActionCard.classList.add("active");
    
    if (firstActionId) {
        const firstDetailId = `${firstActionId}-detail`;
        const firstDetailElement = document.getElementById(firstDetailId);
        if (firstDetailElement) {
            firstDetailElement.classList.add("active");
        }
    }
}


const fab = id("support-fab");
const container = id("support-iframe-container");
const closeBtn = id("support-iframe-close");
if (fab && container && closeBtn) {
    fab.addEventListener("click", () => {
        container.classList.add("open");
    });
    closeBtn.addEventListener("click", () => {
        container.classList.remove("open");
    });
    // Optional: close on outside click
    document.addEventListener("mousedown", (e) => {
        if (container.classList.contains("open") && !container.contains(e.target as Node) && e.target !== fab) {
            container.classList.remove("open");
        }
    });
}