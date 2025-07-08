import {useEffect, useState} from "react";
import {currentTab, switchTab} from "./globalState";

function HeaderLink(
    { id, selected = false, onClick }: {
        id: string,
        selected?: boolean,
        onClick: React.MouseEventHandler<HTMLDivElement>
    }
) {
    return <div
        className={`tab ${selected ? "selected" : ""}`}
        id={id}
        onClick={onClick} />
}

type HeaderItems = {
    id: string,
    title: string,
    onClick?: () => void
}[]

export function Header() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        function handleScroll() {
            setScrolled(
                $(window).scrollTop()!! + $(window).height()!! >= 0 &&
                $(window).scrollTop() !== 0
            )
        }

        addEventListener("scroll", handleScroll);

        return () => {
            window.removeEventListener("scroll", handleScroll);
        }
    }, []);

    const items: HeaderItems = [
        {
            id: "home",
            title: "Главная",
            onClick: () => open("/", "_self")
        },
        {
            id: "download",
            title: "Скачать",
            onClick: () => open(`/download`, "_self")
        },
        {
            id: "guides",
            title: "Гайды",
            onClick: () => open(`/guides`, "_self")
        }
    ]

    return (
        <div className={`react-Header ${scrolled ? "scrolled" : ""}`}>
            <div
                className="icon appicon"
                onClick={() => open("/", "_self")}
            ></div>
            <div className="title">Toolbox.io</div>
            <div className="separator"></div>
            <div id="tabs">
                {
                    items.map(
                        (item, index) =>
                            <HeaderLink
                                id={item.id}
                                selected={index == currentTab}
                                onClick={() => {
                                    switchTab(index);
                                    if (item.onClick) item.onClick()
                                }} />
                    )
                }
            </div>
            <IconButton
                onClick={() => {
                    const token = localStorage.getItem('authToken');
                    if (token) {
                        open("/account", "_self");
                    } else {
                        open("/account/login", "_self");
                    }
                }}
                icon="account_circle" />
        </div>
    )
}

export function IconButton(
    { icon, onClick }: {
        icon: string,
        onClick: React.MouseEventHandler<HTMLDivElement>
    }
) {
    return <div className="react-IconButton" onClick={onClick}>{icon}</div>
}

export function Button(
    { onClick, children }: {
        onClick: React.MouseEventHandler<HTMLDivElement>,
        children: any
    }
) {
    return <div className="react-Button" onClick={onClick}>
        {children}
    </div>
}