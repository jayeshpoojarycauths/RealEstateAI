interface Config {
  apiUrl: string;
  authTokenKey: string;
  enableAnalytics: boolean;
  enableNotifications: boolean;
  googleMapsApiKey: string;
  devMode: boolean;
  enableMockData: boolean;
  allowedOrigins: string[];
  apiRateLimit: number;
  apiRateWindow: number;
  ENABLE_MFA: boolean;
}

const config: Config = {
  apiUrl: import.meta.env.VITE_API_URL,
  authTokenKey: import.meta.env.VITE_AUTH_TOKEN_KEY,
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === "true",
  enableNotifications: import.meta.env.VITE_ENABLE_NOTIFICATIONS === "true",
  googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  devMode: import.meta.env.VITE_DEV_MODE === "true",
  enableMockData: import.meta.env.VITE_ENABLE_MOCK_DATA === "true",
  allowedOrigins: import.meta.env.VITE_ALLOWED_ORIGINS?.split(",") || [],
  apiRateLimit: parseInt(import.meta.env.VITE_API_RATE_LIMIT || "100", 10),
  apiRateWindow: parseInt(import.meta.env.VITE_API_RATE_WINDOW || "60000", 10),
  ENABLE_MFA: import.meta.env.VITE_ENABLE_MFA === "true",
};

export default config;
