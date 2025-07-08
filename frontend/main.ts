"use strict";

import switchTab = Utils.switchTab;
import {Components, Utils} from "./src/common.js";
import smoothScroll = Utils.smoothScroll;
import delay = Utils.delay;
import TioHeader = Components.TioHeader;

(async () => {
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

    // Scaling video in App Locker
    let videoListenerActive = true;
    let videoX: number | null = null;
    let videoY: number | null = null;
    let videoElement: HTMLVideoElement | null;

    async function scaleVideo() {
        if (videoListenerActive) {
            const dialog = document.getElementById("video_dialog") as HTMLDivElement;
            dialog.classList.add("open");
            const video = document.getElementById("demo") as HTMLVideoElement;
            const rect = video.getBoundingClientRect();
            let x = rect.x;
            const y = rect.y - 10;
            if (document.documentElement.offsetWidth > 500) x -= 10;
            video.style.position = "fixed";
            video.style.left = `${x}px`;
            video.style.top = `${y}px`;
            videoX = x;
            videoY = y;
            video.style.transitionProperty = "left, top, transform";
            video.style.transitionDuration = "0.5s";
            video.style.transitionTimingFunction = "ease-out";
            video.style.zIndex = "1003";
            videoElement = document.createElement("video");
            videoElement.style.width = rect.width + "px";
            videoElement.style.height = rect.height + "px";
            videoElement.style.margin = "10px";
            videoElement.style.marginBottom = "0px";
            videoElement.style.flexShrink = "0";
            video.insertAdjacentElement("beforebegin", videoElement);
            await delay(1);
            video.style.left = `calc(50% - ${rect.width / 2}px)`;
            video.style.top = `calc(50% - ${rect.height / 2}px)`;
            video.style.transform = document.documentElement.offsetWidth <= 375 ? "scale(1.4)" : "scale(1.5)";
            videoListenerActive = false;
            video.removeEventListener("click", scaleVideo)
            await delay(500);
            video.controls = true;
        }
    }

    async function unscaleVideo() {
        const dialog = document.getElementById("video_dialog") as HTMLDivElement;
        dialog.style.opacity = "0";
        const video = document.getElementById("demo") as HTMLVideoElement;
        video.style.left = `${videoX}px`;
        video.style.top = `${videoY}px`;
        video.style.transform = "scale(1)";
        await delay(500);
        dialog.classList.remove("open");
        dialog.style.opacity = "";
        videoListenerActive = true;
        video.controls = false;
        (video.parentElement as HTMLDivElement).removeChild((videoElement as HTMLVideoElement));
        video.style.position = "";
        video.style.zIndex = "";
        video.style.left = "";
        video.style.top = "";
        video.style.transform = "";
        videoX = null;
        videoY = null;
        video.addEventListener("click", scaleVideo);
    }

    document.getElementById("demo")!!.addEventListener("click", scaleVideo);
    document.getElementById("video_dialog")!!.addEventListener("click", unscaleVideo);

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