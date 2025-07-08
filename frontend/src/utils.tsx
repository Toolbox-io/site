import {useState, useCallback, useEffect} from "react";

// Хранилище состояний и слушателей
const store: Record<string, any> = {};
const listeners: Record<string, ((state: any) => void)[]> = {};

export function useGlobalState<T>(
    key: string,
    initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
    // Получаем текущее состояние из хранилища
    const [state, _setState] = useState<T>(store[key] as T || initialValue);

    // Функция обновления состояния
    const setState = useCallback((stateOrSetter: T | ((prev: T) => T)) => {
        let next: T;

        if (typeof stateOrSetter === 'function') {
            next = (stateOrSetter as (prev: T) => T)(store[key] as T);
        } else {
            next = stateOrSetter;
        }

        // Обновляем состояние у всех подписчиков
        listeners[key]?.forEach((l) => l(next));
        store[key] = next;
    }, []);

    useEffect(() => {
        // При первом вызове сохраняем начальное состояние
        if (!store[key]) {
            store[key] = initialValue;
        }

        // Создаем массив слушателей, если его еще нет
        if (!listeners[key]) {
            listeners[key] = [];
        }

        // Регистрируем слушателя
        const listener = (state: T) => _setState(state);
        listeners[key].push(listener);

        // Очищаем слушателя при размонтировании компонента
        return () => {
            const index = listeners[key]?.indexOf(listener);
            if (index !== undefined && index !== -1) {
                listeners[key].splice(index, 1);
            }
        };
    }, [key]);

    return [state, setState];
}
