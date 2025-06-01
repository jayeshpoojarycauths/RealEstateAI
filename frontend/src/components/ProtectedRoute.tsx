import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Role, hasAnyRoleAccess } from "../constants/roles"; // remove ROLES until actually used
import { logger } from "../utils/logger";

/**
 * Props for the ProtectedRoute component
 * @property {React.ReactNode} children - Child components to render if access is granted
 * @property {Role[]} [requiredRoles] - Optional array of roles that can access this route
 * @property {boolean} [requireAuth] - Whether authentication is required (defaults to true)
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: Role[];
  requireAuth?: boolean;
}

/**
 * ProtectedRoute component for handling authentication and role-based access control
 *
 * @param children - The component to render if access is granted
 * @param requiredRoles - Optional array of roles that can access this route
 * @param requireAuth - Whether authentication is required (defaults to true)
 *
 * @example
 * // Route accessible only to admins
 * <ProtectedRoute requiredRoles={[ROLES.ADMIN]}>
 *   <AdminDashboard />
 * </ProtectedRoute>
 *
 * @example
 * // Route accessible to both admins and agents
 * <ProtectedRoute requiredRoles={[ROLES.ADMIN, ROLES.AGENT]}>
 *   <AgentDashboard />
 * </ProtectedRoute>
 *
 * @example
 * // Public route that doesn't require authentication
 * <ProtectedRoute requireAuth={false}>
 *   <PublicPage />
 * </ProtectedRoute>
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
  requireAuth = true,
}) => {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // If authentication is not required, render the children
  if (!requireAuth) {
    return <>{children}</>;
  }

  // If user is not authenticated, redirect to login
  if (!user) {
    logger.info("User not authenticated, redirecting to login", {
      path: location.pathname,
    });
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If no specific roles are required, render the children
  if (!requiredRoles) {
    return <>{children}</>;
  }

  // Check if user has any of the required roles
  const hasAccess = hasAnyRoleAccess(user.role as Role, requiredRoles);

  // If user doesn't have access, redirect to unauthorized page
  if (!hasAccess) {
    logger.warn("User does not have required roles", {
      path: location.pathname,
      userRole: user?.role,
      requiredRoles,
    });
    return <Navigate to="/unauthorized" replace />;
  }

  // User has access, render the children
  return <>{children}</>;
};
