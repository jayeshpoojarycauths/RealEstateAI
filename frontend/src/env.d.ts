/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_AUTH_TOKEN_KEY: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_ENABLE_NOTIFICATIONS: string;
  readonly VITE_GOOGLE_MAPS_API_KEY: string;
  readonly VITE_DEV_MODE: string;
  readonly VITE_ENABLE_MOCK_DATA: string;
  readonly VITE_ALLOWED_ORIGINS: string;
  readonly VITE_API_RATE_LIMIT: string;
  readonly VITE_API_RATE_WINDOW: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
