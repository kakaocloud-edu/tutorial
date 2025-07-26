// localStorage 헬퍼 함수들
export const storage = {
    get<T>(key: string, defaultValue: T): T {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn(`localStorage 읽기 실패 [${key}]:`, error);
            return defaultValue;
        }
    },

    set<T>(key: string, value: T): boolean {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.warn(`localStorage 저장 실패 [${key}]:`, error);
            return false;
        }
    },

    remove(key: string): boolean {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn(`localStorage 삭제 실패 [${key}]:`, error);
            return false;
        }
    },

    clear(): boolean {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.warn('localStorage 전체 삭제 실패:', error);
            return false;
        }
    }
};
