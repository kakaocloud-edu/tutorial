import { useState, useEffect } from 'react';

interface StoredData<T> {
    value: T;
    expiry: number;
}

function useExpiringState<T>(
    key: string, 
    defaultValue: T, 
    ttl: number = 24 * 60 * 60 * 1000 // 24시간
): [T, (value: T) => void] {
    const [state, setState] = useState<T>(() => {
        try {
            const item = localStorage.getItem(key);
            if (item) {
                const storedData: StoredData<T> = JSON.parse(item);
                if (Date.now() > storedData.expiry) {
                    localStorage.removeItem(key);
                    return defaultValue;
                }
                return storedData.value;
            }
        } catch (error) {
            console.warn(`만료 상태 읽기 실패:`, error);
        }
        return defaultValue;
    });

    useEffect(() => {
        try {
            const dataToStore: StoredData<T> = {
                value: state,
                expiry: Date.now() + ttl
            };
            localStorage.setItem(key, JSON.stringify(dataToStore));
        } catch (error) {
            console.warn(`만료 상태 저장 실패:`, error);
        }
    }, [key, state, ttl]);

    return [state, setState];
}

export default useExpiringState;
