import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import config from '../config';

interface PrivateRouteProps {
  children: React.ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const location = useLocation();
  const { token, requiresMFA } = useAuth();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Only redirect to MFA if enabled
  if (config.ENABLE_MFA && requiresMFA) {
    return <Navigate to="/mfa-verify" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}; 