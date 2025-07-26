import { useState, useEffect } from 'react';

function usePersistedState<T>(key: string, defaultValue: T): [T, (value: T) => void] {
    const [state, setState] = useState<T>(() => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn(`localStorage에서 ${key} 읽기 실패:`, error);
            return defaultValue;
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem(key, JSON.stringify(state));
        } catch (error) {
            console.warn(`localStorage에 ${key} 저장 실패:`, error);
        }
    }, [key, state]);

    return [state, setState];
}

export default usePersistedState;
