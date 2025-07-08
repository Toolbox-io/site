import React, { useRef, useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import {useGlobalState} from "./utils.tsx";


function HeaderLink(
    { id, selected = false, onClick, title }: {
        id: string,
        selected?: boolean,
        title: string,
        onClick: React.MouseEventHandler<HTMLDivElement>
    }
) {
    return <div
        className={`tab ${selected ? "selected" : ""}`}
        id={id}
        onClick={onClick}>
        {title}
    </div>
}

type HeaderItems = {
    id: string,
    title: string,
    onClick?: () => void
}[]

export function Header() {
    const [scrolled, setScrolled] = useState(false);
    const [currentTab, switchTab] = useGlobalState("currentTab", 0);

    useEffect(() => {
        function handleScroll() {
            setScrolled(
                window.scrollY + window.innerHeight >= 0 &&
                window.scrollY !== 0
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
                                }}
                                title={item.title}
                                key={index} />
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
    return <div className="react-IconButton material-symbols filled" onClick={onClick}>{icon}</div>
}

export function Button(
    { onClick, children }: {
        onClick?: React.MouseEventHandler<HTMLDivElement>,
        children: any
    }
) {
    return <div className="react-Button" onClick={onClick}>
        {children}
    </div>
}

export function Footer() {
    // The logic for selected link is based on current URL
    const links = [
        { href: '/', label: 'Главная' },
        { href: '/guides', label: 'Гайды' },
        { href: '/compatibility', label: 'Совместимость' },
        { href: '/download', label: 'Скачать' },
    ];
    const docs = [
        { href: '/privacy', label: 'Политика конфиденциальности' },
        { href: 'https://github.com/Toolbox-io/Toolbox-io/tree/main/LICENSE', label: 'Лицензия' },
    ];
    const resources = [
        { href: 'https://github.com/Toolbox-io/Toolbox-io', label: 'Репозиторий на GitHub' },
        { href: 'https://github.com/orgs/Toolbox-io/projects/1', label: 'Проект на GitHub' },
    ];
    const isSelected = (href: string) => {
        // Normalize trailing slashes for comparison
        const normalize = (url: string) => url.replace(/\/$/, '');
        return normalize(window.location.pathname) === normalize(href);
    };
    return (
        <footer className="react-Footer">
            <div className="footer_column">
                <div className="footer_title">Toolbox.io</div>
                {links.map(link => (
                    <a
                        key={link.href}
                        href={link.href}
                        draggable="false"
                        className={isSelected(link.href) ? 'selected' : ''}
                        onClick={e => {
                            if (isSelected(link.href)) e.preventDefault();
                        }}
                    >
                        {link.label}
                    </a>
                ))}
            </div>
            <div className="footer_column">
                <div className="footer_title">Документы</div>
                {docs.map(link => (
                    <a
                        key={link.href}
                        href={link.href}
                        draggable="false"
                        target={link.href.startsWith('http') ? '_blank' : undefined}
                        rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    >
                        {link.label}
                    </a>
                ))}
            </div>
            <div className="footer_column">
                <div className="footer_title">Ресурсы</div>
                {resources.map(link => (
                    <a
                        key={link.href}
                        href={link.href}
                        draggable="false"
                        target="_blank"
                        rel="noopener noreferrer"
                    >{link.label}</a>
                ))}
            </div>
        </footer>
    );
}

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    type?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input({ label, type = 'text', ...props }, ref) {
    const [showPassword, setShowPassword] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    useImperativeHandle(ref, () => inputRef.current!);
    return (
        <div className="input-group">
            <input
                ref={inputRef}
                type={showPassword ? 'text' : type}
                placeholder={label}
                {...props}
            />
            {type === 'password' && (
                <button
                    type="button"
                    className="toggle-password"
                    tabIndex={-1}
                    aria-label="Show password"
                    onClick={() => setShowPassword(v => !v)}
                >
                    <span className="material-symbols filled">
                        {showPassword ? 'visibility_off' : 'visibility'}
                    </span>
                </button>
            )}
        </div>
    );
});

export function CodeInputRow({
    length = 6,
    onComplete,
    ...props
}: {
    length?: number;
    onComplete?: (value: string) => void;
} & React.HTMLAttributes<HTMLDivElement>) {
    const [values, setValues] = useState<string[]>(Array(length).fill(''));
    const inputsRef = useRef<(HTMLInputElement | null)[]>([]);

    useEffect(() => {
        inputsRef.current[0]?.focus();
    }, []);

    useEffect(() => {
        const value = values.join('');
        if (value.length === length && /^\d+$/.test(value)) {
            onComplete?.(value);
        }
    }, [values, length, onComplete]);

    const handleInput = (idx: number, e: React.ChangeEvent<HTMLInputElement>) => {
        let v = e.target.value.replace(/[^0-9]/g, '');
        if (v.length > 1) v = v[0];
        const newValues = [...values];
        newValues[idx] = v;
        setValues(newValues);
        if (v && idx < length - 1) {
            inputsRef.current[idx + 1]?.focus();
        }
    };
    const handleKeyDown = (idx: number, e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Backspace') {
            if (!values[idx] && idx > 0) {
                inputsRef.current[idx - 1]?.focus();
            } else {
                const newValues = [...values];
                newValues[idx] = '';
                setValues(newValues);
            }
        }
    };
    const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
        const data = e.clipboardData.getData('text');
        if (/^\d{6}$/.test(data)) {
            e.preventDefault();
            setValues(data.split(''));
            inputsRef.current[length - 1]?.focus();
            onComplete?.(data);
        }
    };
    return (
        <div className="code-input-row" {...props}>
            {Array.from({ length }).map((_, i) => (
                <input
                    key={i}
                    className="code-digit-input"
                    id={`code-${i}`}
                    type="text"
                    maxLength={1}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    autoComplete="one-time-code"
                    value={values[i]}
                    ref={el => { inputsRef.current[i] = el; }}
                    onChange={e => handleInput(i, e)}
                    onKeyDown={e => handleKeyDown(i, e)}
                    onPaste={handlePaste}
                />
            ))}
        </div>
    );
}