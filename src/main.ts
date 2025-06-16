"use strict";

import switchTab = Utils.switchTab;
import {Components, Cookies, token, Utils} from "./common.js";
import doScrolling = Utils.doScrolling;
import delay = Utils.delay;
import TioHeader = Components.TioHeader;

await (async () => {
    // Set up buttons
    const header = document.querySelector("tio-header")!! as TioHeader;

    // Tabs
    header.tabs[0].addEventListener("click", () => {
        doScrolling("body", 1000);
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
                    const rect = feature.getBoundingClientRect();

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

    // Make "Download" button directly download the file
    try {
        let currentRatelimitRemaining = Cookies.get("release-ratelimitRemaining");
        let currentRatelimitReset = Cookies.get("release-ratelimitReset");
        if (currentRatelimitReset === null) {
            currentRatelimitReset = (Date.now() + 100).toString();
        }
        if (currentRatelimitRemaining === null) {
            currentRatelimitRemaining = "-1";
        }

        let bool = Number(currentRatelimitRemaining) !== 0
        if (!bool) {
            bool = Date.now() > Number(currentRatelimitReset)
        }

        if (bool) {
            const headers: any = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": `Bearer ${token}`
            }
            const prevEtag = Cookies.get("release-etag");
            if (prevEtag !== null) {
                headers["if-none-match"] = prevEtag;
            }

            const response: Response = await fetch(
                "https://api.github.com/repos/Toolbox-io/Toolbox-io/releases/latest",
                {
                    method: "GET",
                    headers: headers
                }
            );
            if (response.ok || response.status === 304) {
                let downloadUrl: string;
                if (response.status === 304) {
                    console.log("304 Not Modified");
                    downloadUrl = Cookies.get("release-download_url")!!;
                } else {
                    const responseJSON: any = await response.json();
                    downloadUrl = responseJSON.assets[0].browser_download_url;
                }
                (
                    document.getElementById("download_url") as HTMLAnchorElement
                ).href = downloadUrl;
                const etag = response.headers.get("etag")
                console.log(etag);
                if (etag !== null) {
                    Cookies.set("release-etag", etag);
                }
                Cookies.set("release-download_url", downloadUrl);
            }
            const ratelimitRemaining = response.headers.get("X-Ratelimit-Remaining")!!;
            const ratelimitReset = response.headers.get("X-Ratelimit-Reset")!!;
            Cookies.set("release-ratelimitRemaining", ratelimitRemaining);
            Cookies.set("release-ratelimitReset", ratelimitReset);
            console.log(`Rate limit remaining: ${ratelimitRemaining}`);
            console.log(`Rate limit reset: ${ratelimitReset}`);
        } else {
            console.warn(`Rate limit exceeded, it will be reset at ${Cookies.get("release-ratelimitReset")}`);
        }
    } catch (e) {
        console.log(e)
    }
})()