import React, { createContext, useContext, useState, useCallback } from 'react';
import { Alert } from '@material-tailwind/react';
import { AnimatePresence, motion } from 'framer-motion';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  showToast: (type: ToastType, message: string) => void;
  hideToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((type: ToastType, message: string) => {
    const id = Math.random().toString(36).substring(7);
    setToasts((prev) => [...prev, { id, type, message }]);

    // Auto-hide after 5 seconds
    setTimeout(() => {
      hideToast(id);
    }, 5000);
  }, []);

  const hideToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const getToastColor = (type: ToastType) => {
    switch (type) {
      case 'success':
        return 'green';
      case 'error':
        return 'red';
      case 'warning':
        return 'amber';
      case 'info':
        return 'blue';
      default:
        return 'blue';
    }
  };

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 50, scale: 0.3 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
              className="mb-2"
            >
              <Alert
                color={getToastColor(toast.type)}
                className="min-w-[300px]"
                dismissible
                onClose={() => hideToast(toast.id)}
              >
                {toast.message}
              </Alert>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}; 