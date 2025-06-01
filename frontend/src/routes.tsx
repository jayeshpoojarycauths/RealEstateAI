import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Role } from './types/auth';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Properties } from './pages/Properties';
import { Customers } from './pages/Customers';
import { Settings } from './pages/Settings';
import { AuditLogs } from './pages/AuditLogs';
import { Analytics } from './pages/Analytics';
import { UserManagement } from './pages/admin/UserManagement';
import { TenantManagement } from './pages/platform/TenantManagement';
import { SystemSettings } from './pages/platform/SystemSettings';
import { Unauthorized } from './pages/Unauthorized';
import { NotFound } from './pages/NotFound';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/unauthorized" element={<Unauthorized />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/properties"
        element={
          <ProtectedRoute>
            <Properties />
          </ProtectedRoute>
        }
      />
      <Route
        path="/customers"
        element={
          <ProtectedRoute>
            <Customers />
          </ProtectedRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <ProtectedRoute requiredRoles={[Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN, Role.ANALYST]}>
            <Analytics />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute requiredRoles={[Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN]}>
            <Settings />
          </ProtectedRoute>
        }
      />

      {/* Admin routes */}
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute requiredRoles={[Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN]}>
            <UserManagement />
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit-logs"
        element={
          <ProtectedRoute requiredRoles={[Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.AUDITOR]}>
            <AuditLogs />
          </ProtectedRoute>
        }
      />

      {/* Platform admin routes */}
      <Route
        path="/platform/tenants"
        element={
          <ProtectedRoute requiredRoles={[Role.PLATFORM_ADMIN]}>
            <TenantManagement />
          </ProtectedRoute>
        }
      />
      <Route
        path="/platform/settings"
        element={
          <ProtectedRoute requiredRoles={[Role.PLATFORM_ADMIN]}>
            <SystemSettings />
          </ProtectedRoute>
        }
      />

      {/* Default routes */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}; 