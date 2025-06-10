import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "./components/common/Toast";
import { AuthProvider } from "./contexts/AuthContext";
import { AppRoutes } from "./routes";
import { Layout } from "./components/Layout";

import { logger } from "./utils/logger";

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

/**
 * Main application component with role-based routing
 *
 * Routes are protected based on user roles:
 * - Public routes: /login, /unauthorized
 * - Admin-only routes: /admin/*
 * - Manager+ routes: /customers
 * - All authenticated users: /dashboard, /properties
 */
function App() {
  logger.info("Application started");

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <Layout>
              <AppRoutes />
            </Layout>
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
