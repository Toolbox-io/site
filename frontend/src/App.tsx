import React from 'react';
import {Header, IconButton} from "./components.tsx";

export default function App() {
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
                        <div className="feature" id="applocker">
                            <div className="feature-header">
                                <span className="material-symbols outlined feature-icon">phonelink_lock</span>
                                <div className="feature-title">Блокировка приложений</div>
                                <IconButton icon="close" onClick={() => {}} />
                            </div>
                            <div className="feature-description">
                                Защищает ваши приложения от несанкционированного доступа, показывая злоумышленнику
                                фальшивое сообщение о сбое.
                            </div>

                            <div className="feature-long-description textcenter">
                                <div className="side centermargin">
                                    <div className="text">
                                        <p>
                                            Когда вы пытаетесь открыть защищённое приложение, оно закроется
                                            и вы увидите сообщение об ошибке.
                                            На самом деле, никакой ошибки нет, это нужно, чтобы запутать
                                            мошенника.
                                        </p>
                                        <p>
                                            Чтобы разблокировать приложение, нужно использовать выбранный способ
                                            разблокировки. По умолчанию, это долгое нажатие кнопки <b>О
                                            приложении</b>. Но Вы всегда можете это изменить через настройки
                                            Блокировки приложений.
                                        </p>
                                        <p>
                                            Вы можете прочитать, как пользоваться этой функцией
                                            <a href="guides/how_to_lock_apps" draggable="false">здесь</a>.
                                        </p>
                                    </div>
                                    <div id="video_container">
                                        <video autoPlay muted loop height="480" width="216" id="demo">
                                            <source src="/res/demo.webm" type="video/webm"/>
                                        </video>
                                        <div className="tip">Нажмите, чтобы увеличить</div>
                                    </div>
                                </div>
                                <div id="video_dialog" className="dialog"></div>
                            </div>
                        </div>
                        <div className="feature" id="unlock_protection">
                            <div className="feature-header">
                                <span className="material-symbols filled feature-icon">lock</span>
                                <div className="feature-title">Защита блокировки</div>
                                {/* <md-icon-button className="feature-close">close</md-icon-button> */}
                            </div>
                            <div className="feature-description">
                                Выполняет действия, если кто-то много раз попытался разблокировать ваш телефон.
                            </div>
                            <div className="feature-long-description">
                                <div className="centermargin textcenter textstyling">
                                    <p>
                                        Если кто-то пытается разблокировать ваше устройство, но у него не получается
                                        с нескольких попыток, можно выполнить следующие действия:
                                    </p>
                                    <h4>Сигнализация</h4>
                                    <p>
                                        Устройство возпроизведёт звук сигнализации (при желании его можно
                                        изменить) на 100% громкости. Любые попытки изменить громкость будут
                                        предотвращены.
                                    </p>
                                    <h4>Фотография злоумышленника</h4>
                                    <p>
                                        Устройство сделает снимок злоумышленника с фронтальной камеры.
                                    </p>
                                    <p>
                                        Вы можете прочитать, как пользоваться этой функцией
                                        <a href="guides/how_to_use_unlock_protection" draggable="false">здесь</a>.
                                    </p>
                                    <hr/>
                                    <p>
                                        Обратите внимание, что для работы этой функции требуется разрешение
                                        администратора устройства.
                                        Это необходимо для обнаружения неудачных попыток разблокировки и выполнения
                                        требуемых действий.
                                    </p>
                                    <p>
                                        Это приложение НИКОГДА не использует КАКИЕ-ЛИБО разрешения без вашего
                                        согласия, они используются ТОЛЬКО для перечисленных целей.
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="feature" id="donttouchmyphone">
                            <div className="feature-header">
                                <span className="material-symbols filled feature-icon">do_not_touch</span>
                                <div className="feature-title">Не трогайте мой телефон</div>
                                {/* <md-icon-button className="feature-close">close</md-icon-button> */}
                            </div>
                            <div className="feature-description">
                                Защитите ваш телефон от несанкционированных прикосновений!
                            </div>
                            <div className="feature-long-description">
                                <div className="centermargin textcenter">
                                    <p>
                                        Эта функция поможет Вам защитить ваш телефон от физических прикосновений (например,
                                        когда кто-нибудь возьмет ваш телефон в руки).
                                    </p>
                                    <p>
                                        При попытке прикосновения будут выполнены те же действия, что и при срабатывании
                                        Защиты блокировки.
                                    </p>
                                    <p>
                                        Использовать очень просто: Вы нажимаете кнопку в разделе, и после этого любое
                                        прикосновение к вашему телефону будет записано. Когда Вы захотите выключить эту
                                        защиту, просто нажмите "Стоп" и защита отключится.
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="feature" id="tiles">
                            <div className="feature-header">
                                <span className="material-symbols filled feature-icon">apps</span>
                                <div className="feature-title">Плитки</div>
                                {/* <md-icon-button className="feature-close">close</md-icon-button> */}
                            </div>
                            <div className="feature-description">
                                Полезные плитки для быстрых настроек
                            </div>

                            <div className="feature-long-description">
                                <div className="centermargin textcenter">
                                    Плитки — это кнопки в <b><i>быстрых настройках</i></b> вашего устройства
                                    (меню, которое открывается свайпом вниз от верхней части экрана).
                                    <h3>Сон</h3>
                                    При отключении отключает режим сна до повторного включения.
                                    <div className="warning">
                                        <span className="material-symbols filled warning-icon">warning</span>
                                        Будьте осторожны, так как если вы забудете его включить, это может привести к разрядке аккумулятора.
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="feature" id="shortcuts">
                            <div className="feature-header">
                                <span className="material-symbols filled feature-icon">shortcut</span>
                                <div className="feature-title">Ярлыки</div>
                                {/* <md-icon-button className="feature-close">close</md-icon-button> */}
                            </div>
                            <div className="feature-description">
                                Полезные ярлыки для скрытых приложений на устройстве
                            </div>
                            <div className="feature-long-description">
                                <div className="centermargin textcenter">
                                    Эта функция поможет вам быстро получить доступ практически к любой части вашего устройства
                                    (например, к скрытым приложениям, системным настройкам или другим приложениям).
                                    <h3>Файлы</h3>
                                    Встроенное приложение <b><i>Файлы</i></b> скрыто на большинстве устройств. Но если вы хотите
                                    получить к нему доступ, вы можете сделать это в этом приложении! Просто перейдите в
                                    <b>«Ярлыки»</b> и нажмите <b>«Добавить»</b> под кнопкой <b><i>«Файлы»</i></b>, а затем
                                    подтвердите добавление ярлыка.
                                </div>
                            </div>
                        </div>
                        <div className="feature" id="appmanager">
                            <div className="feature-header">
                                <span className="material-symbols filled feature-icon">apps</span>
                                <div className="feature-title">Менеджер приложений</div>
                                {/* <md-icon-button className="feature-close">close</md-icon-button> */}
                            </div>
                            <div className="feature-description">
                                Удобно управляйте вашими приложениями
                            </div>
                            <div className="feature-long-description">
                                <div className="centermargin textcenter">
                                    Эта функция позволяет:

                                    <ul>
                                        <li>
                                            делиться APK-файлом приложения, чтобы сделать резервную копию
                                            или отправить друзьям;
                                        </li>
                                        <li>
                                            блокировать его с помощью Блокировки приложений, чтобы защитить
                                            конфиденциальную информацию;
                                        </li>
                                        <li>
                                            получать дополнительную техническую информацию;
                                        </li>
                                        <li>
                                            легко находить нужное приложение с помощью поиска по ключевым словам.
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        {/*TODO notification history description*/}
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
                            className="noeffect">
                            {/* <md-filled-button id="progress_btn">Открыть проект</md-filled-button> */}
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
                        <a href="https://github.com/Toolbox-io/Toolbox-io/issues/new" draggable="false">GitHub</a>.
                    </p>
                    <div className="center">
                        {/*<md-filled-button id="issues_btn">Открыть проблемы</md-filled-button>*/}
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
                            {/*<md-filled-button id="download_btn">Скачать Toolbox.io</md-filled-button>*/}
                        </a>
                    </div>
                </div>
            </div>
            {/*<tio-footer></tio-footer>*/}
            <div id="card_dialog" className="dialog"></div>
        </>
    )
};