export const STORAGE_KEYS = {
    KAKAO_ACCESS_KEY: 'kakao-access-key',
    KAKAO_SECRET_KEY: 'kakao-secret-key',
    USER_PREFERENCES: 'user-preferences',
    S3_ACCESS_KEY: 's3-access-key',        
    S3_SECRET_KEY: 's3-secret-key'    
} as const;

export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];
