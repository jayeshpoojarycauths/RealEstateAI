import { Role } from './roles';

// Role utility functions
export const isPlatformAdmin = (role: Role) => role === Role.PLATFORM_ADMIN;
export const isSuperAdmin = (role: Role) => role === Role.SUPERADMIN;
export const isAdmin = (role: Role) => role === Role.ADMIN;
export const isManager = (role: Role) => role === Role.MANAGER;
export const isAgent = (role: Role) => role === Role.AGENT;
export const isAnalyst = (role: Role) => role === Role.ANALYST;
export const isAuditor = (role: Role) => role === Role.AUDITOR;

// Role hierarchy for permission checks
export const roleHierarchy: Record<Role, Role[]> = {
  [Role.PLATFORM_ADMIN]: Object.values(Role),
  [Role.SUPERADMIN]: [Role.SUPERADMIN, Role.ADMIN, Role.MANAGER, Role.AGENT, Role.ANALYST, Role.AUDITOR],
  [Role.ADMIN]: [Role.ADMIN, Role.MANAGER, Role.AGENT, Role.ANALYST],
  [Role.MANAGER]: [Role.MANAGER, Role.AGENT],
  [Role.AGENT]: [Role.AGENT],
  [Role.ANALYST]: [Role.ANALYST],
  [Role.AUDITOR]: [Role.AUDITOR],
};

// Check if a role has permission to perform actions for another role
export const hasPermission = (userRole: Role, targetRole: Role): boolean => {
  return roleHierarchy[userRole]?.includes(targetRole) ?? false;
};

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  phone?: string;
  avatar?: string;
  isEmailVerified: boolean;
  tenantId?: string; // Added for multitenant support
  createdAt: string;
  updatedAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  tenantId?: string; // Added for multitenant support
}

export interface RegisterData extends LoginCredentials {
  firstName: string;
  lastName: string;
  phone?: string;
  tenantId?: string; // Added for multitenant support
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginDto {
  email: string;
  password: string;
  tenantId?: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  tenantId?: string;
}

export interface PasswordResetDto {
  token: string;
  password: string;
}

export interface EmailVerificationDto {
  token: string;
}

export interface ResendVerificationDto {
  email: string;
} 