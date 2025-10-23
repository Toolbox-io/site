export function get(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        const result = parts.pop()?.split(';').shift();
        if (result === undefined) {
            return null;
        } else {
            return decodeURIComponent(result);
        }
    }
    return null;
}

export function set(name: string, value: string, expiresDays: number = 7): void {
    const date = new Date();
    date.setTime(date.getTime() + (expiresDays * 24 * 60 * 60 * 1000));
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${encodeURIComponent(value)};${expires};path=/`;
}

export function deleteCookie(name: string): void {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

export function getAll(): { [key: string]: string } {
    const cookies: { [key: string]: string } = {};
    const cookieArray = document.cookie.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
        const cookiePair = cookieArray[i].split('=');
        if (cookiePair.length === 2) {
            cookies[cookiePair[0].trim()] = decodeURIComponent(cookiePair[1].trim());
        }
    }
    return cookies;
}