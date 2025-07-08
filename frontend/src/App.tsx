import React, { useRef, useState } from 'react';
import {Header, IconButton, Footer, Button} from "./components.js";

export default function App() {
    // State for video scaling
    const [videoScaled, setVideoScaled] = useState(false);
    const [videoRect, setVideoRect] = useState<{left: number, top: number, width: number, height: number} | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const dialogRef = useRef<HTMLDivElement>(null);

    // State for expanded feature card
    const [expandedFeature, setExpandedFeature] = useState<string | null>(null);

    // Feature list for mapping
    const features = [
        {
            id: "applocker",
            icon: <span className="material-symbols outlined feature-icon">phonelink_lock</span>,
            title: "Блокировка приложений",
            description: "Защищает ваши приложения от несанкционированного доступа, показывая злоумышленнику фальшивое сообщение о сбое.",
            long: (
                <div className="side centermargin">
                    <div className="text">
                        <p>Когда вы пытаетесь открыть защищённое приложение, оно закроется и вы увидите сообщение об ошибке. На самом деле, никакой ошибки нет, это нужно, чтобы запутать мошенника.</p>
                        <p>Чтобы разблокировать приложение, нужно использовать выбранный способ разблокировки. По умолчанию, это долгое нажатие кнопки <b>О приложении</b>. Но Вы всегда можете это изменить через настройки Блокировки приложений.</p>
                        <p>Вы можете прочитать, как пользоваться этой функцией <a href="guides/how_to_lock_apps" draggable="false">здесь</a>.</p>
                    </div>
                    <div id="video_container">
                        <video
                            autoPlay
                            muted
                            loop
                            height="480"
                            width="216"
                            id="demo"
                            ref={videoRef}
                            style={videoScaled && videoRect ? {
                                position: 'fixed',
                                left: videoRect.left,
                                top: videoRect.top,
                                width: videoRect.width,
                                height: videoRect.height,
                                zIndex: 1003,
                                transform: `scale(${window.innerWidth <= 375 ? 1.4 : 1.5})`,
                                transition: 'left 0.5s, top 0.5s, transform 0.5s',
                            } : {}}
                            onClick={() => {
                                if (!videoScaled && videoRef.current) {
                                    const rect = videoRef.current.getBoundingClientRect();
                                    setVideoRect({
                                        left: rect.x,
                                        top: rect.y - 10,
                                        width: rect.width,
                                        height: rect.height
                                    });
                                    setVideoScaled(true);
                                    setTimeout(() => {
                                        if (videoRef.current) {
                                            videoRef.current.controls = true;
                                        }
                                    }, 500);
                                }
                            }}
                        >
                            <source src="/res/demo.webm" type="video/webm"/>
                        </video>
                        <div className="tip">Нажмите, чтобы увеличить</div>
                        {videoScaled && (
                            <div
                                ref={dialogRef}
                                id="video_dialog"
                                className="dialog open"
                                style={{position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', zIndex: 1002}}
                                onClick={() => {
                                    setVideoScaled(false);
                                    setTimeout(() => {
                                        if (videoRef.current) {
                                            videoRef.current.controls = false;
                                        }
                                    }, 500);
                                }}
                            />
                        )}
                    </div>
                </div>
            )
        },
        {
            id: "unlock_protection",
            icon: <span className="material-symbols filled feature-icon">lock</span>,
            title: "Защита блокировки",
            description: "Выполняет действия, если кто-то много раз попытался разблокировать ваш телефон.",
            long: (
                <div className="centermargin textcenter textstyling">
                    <p>Если кто-то пытается разблокировать ваше устройство, но у него не получается с нескольких попыток, можно выполнить следующие действия:</p>
                    <h4>Сигнализация</h4>
                    <p>Устройство возпроизведёт звук сигнализации (при желании его можно изменить) на 100% громкости. Любые попытки изменить громкость будут предотвращены.</p>
                    <h4>Фотография злоумышленника</h4>
                    <p>Устройство сделает снимок злоумышленника с фронтальной камеры.</p>
                    <p>Вы можете прочитать, как пользоваться этой функцией <a href="guides/how_to_use_unlock_protection" draggable="false">здесь</a>.</p>
                    <hr/>
                    <p>Обратите внимание, что для работы этой функции требуется разрешение администратора устройства. Это необходимо для обнаружения неудачных попыток разблокировки и выполнения требуемых действий.</p>
                    <p>Это приложение НИКОГДА не использует КАКИЕ-ЛИБО разрешения без вашего согласия, они используются ТОЛЬКО для перечисленных целей.</p>
                </div>
            )
        },
        {
            id: "donttouchmyphone",
            icon: <span className="material-symbols filled feature-icon">do_not_touch</span>,
            title: "Не трогайте мой телефон",
            description: "Защитите ваш телефон от несанкционированных прикосновений!",
            long: (
                <div className="centermargin textcenter">
                    <p>Эта функция поможет Вам защитить ваш телефон от физических прикосновений (например, когда кто-нибудь возьмет ваш телефон в руки).</p>
                    <p>При попытке прикосновения будут выполнены те же действия, что и при срабатывании Защиты блокировки.</p>
                    <p>Использовать очень просто: Вы нажимаете кнопку в разделе, и после этого любое прикосновение к вашему телефону будет записано. Когда Вы захотите выключить эту защиту, просто нажмите "Стоп" и защита отключится.</p>
                </div>
            )
        },
        {
            id: "tiles",
            icon: <span className="material-symbols filled feature-icon">apps</span>,
            title: "Плитки",
            description: "Полезные плитки для быстрых настроек",
            long: (
                <div className="centermargin textcenter">
                    Плитки — это кнопки в <b><i>быстрых настройках</i></b> вашего устройства (меню, которое открывается свайпом вниз от верхней части экрана).
                    <h3>Сон</h3>
                    При отключении отключает режим сна до повторного включения.
                    <div className="warning">
                        <span className="material-symbols filled warning-icon">warning</span>
                        Будьте осторожны, так как если вы забудете его включить, это может привести к разрядке аккумулятора.
                    </div>
                </div>
            )
        },
        {
            id: "shortcuts",
            icon: <span className="material-symbols filled feature-icon">shortcut</span>,
            title: "Ярлыки",
            description: "Полезные ярлыки для скрытых приложений на устройстве",
            long: (
                <div className="centermargin textcenter">
                    Эта функция поможет вам быстро получить доступ практически к любой части вашего устройства (например, к скрытым приложениям, системным настройкам или другим приложениям).
                    <h3>Файлы</h3>
                    Встроенное приложение <b><i>Файлы</i></b> скрыто на большинстве устройств. Но если вы хотите получить к нему доступ, вы можете сделать это в этом приложении! Просто перейдите в <b>«Ярлыки»</b> и нажмите <b>«Добавить»</b> под кнопкой <b><i>«Файлы»</i></b>, а затем подтвердите добавление ярлыка.
                </div>
            )
        },
        {
            id: "appmanager",
            icon: <span className="material-symbols filled feature-icon">apps</span>,
            title: "Менеджер приложений",
            description: "Удобно управляйте вашими приложениями",
            long: (
                <div className="centermargin textcenter">
                    Эта функция позволяет:
                    <ul>
                        <li>делиться APK-файлом приложения, чтобы сделать резервную копию или отправить друзьям;</li>
                        <li>блокировать его с помощью Блокировки приложений, чтобы защитить конфиденциальную информацию;</li>
                        <li>получать дополнительную техническую информацию;</li>
                        <li>легко находить нужное приложение с помощью поиска по ключевым словам.</li>
                    </ul>
                </div>
            )
        }
    ];

    return (
        <>
            <Header />
            <div className="wrapper">
                <div id="main" className="automargin">
                    <h1 id="headline">Все нужное — в одном приложении</h1>
                    <p>
                        Toolbox.io — это надежный инструмент, который помогает защитить ваши приложения и данные
                        на Android от несанкционированного доступа. Он предлагает множество функций, которые делают
                        вашу жизнь более безопасной и комфортной.
                    </p>
                    <h2>Возможности</h2>
                    <div id="features">
                        {features.map(feature => (
                            <div
                                key={feature.id}
                                className={`feature${expandedFeature === feature.id ? ' expanded' : ''}`}
                                id={feature.id}
                                onClick={() => setExpandedFeature(feature.id)}
                                style={{ cursor: expandedFeature ? 'default' : 'pointer' }}
                            >
                                <div className="feature-header">
                                    {feature.icon}
                                    <div className="feature-title">{feature.title}</div>
                                    <IconButton icon="close" onClick={e => {
                                        e.stopPropagation();
                                        setExpandedFeature(null);
                                    }} />
                                </div>
                                <div className="feature-description" style={{ display: expandedFeature === feature.id ? 'none' : undefined }}>
                                    {feature.description}
                                </div>
                                <div className="feature-long-description textcenter" style={{ display: expandedFeature === feature.id ? 'block' : 'none', opacity: expandedFeature === feature.id ? 1 : 0 }}>
                                    {feature.long}
                                </div>
                            </div>
                        ))}
                    </div>
                    <h2>Прогресс</h2>
                    <p>
                        Весь прогресс программы есть в проекте на GitHub.
                        Вы можете проверить прогресс, нажав на кнопку ниже.
                    </p>
                    <div className="center topmargin">
                        <a
                            href="https://github.com/orgs/Toolbox-io/projects/1"
                            draggable="false"
                            className="noeffect"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <Button>Открыть проект</Button>
                        </a>
                    </div>

                    <h2 id="help_h1" className="h1">
                        <div id="help_h" className="h"></div>
                        Поддержка
                    </h2>
                    <p>
                        Если вам нужна помощь, вы нашли ошибку или хотите предложить новую функцию, не стесняйтесь
                        писать мне на <a href="mailto:denis0001.dev@ya.ru" draggable="false">denis0001.dev@ya.ru</a>. Также вы можете
                        отправить ошибку на
                        <a href="https://github.com/Toolbox-io/Toolbox-io/issues/new" draggable="false" target="_blank" rel="noopener noreferrer">GitHub</a>.
                    </p>
                    <div className="center">
                        <a
                            href="https://github.com/Toolbox-io/Toolbox-io/issues"
                            draggable="false"
                            className="noeffect"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <Button>Открыть проблемы</Button>
                        </a>
                    </div>

                    <h2 id="download_h1" className="h1">
                        <div id="download_h" className="h"></div>
                        Попробуйте приложение
                    </h2>
                    <p>
                        Toolbox.io совместим с Android 7 и выше. Подробнее о совместимости
                        <a href="/compatibility" draggable="false">здесь</a>.
                        Приложение не гарантировано на работу на всех устройтвах, поэтому если видите что-то
                        неожиданное, отправить отчет об ошибке на GitHub.
                    </p>
                    <div className="center topmargin">
                        <a href="/download" draggable="false" className="noeffect">
                            <Button>Скачать Toolbox.io</Button>
                        </a>
                    </div>
                </div>
            </div>
            <Footer />
            <div id="card_dialog" className="dialog" />
        </>
    );
}