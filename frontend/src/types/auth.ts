import { Role } from "./roles";

// Role utility functions
export const isPlatformAdmin = (role: Role) => role === Role.PLATFORM_ADMIN;
export const isSuperAdmin = (role: Role) => role === Role.SUPERADMIN;
export const isAdmin = (role: Role) => role === Role.ADMIN;
export const isManager = (role: Role) => role === Role.MANAGER;
export const isAgent = (role: Role) => role === Role.AGENT;
export const isAnalyst = (role: Role) => role === Role.ANALYST;
export const isAuditor = (role: Role) => role === Role.AUDITOR;
export const isCustomer = (role: Role) => role === Role.CUSTOMER;
export const isGuest = (role: Role) => role === Role.GUEST;

// Role hierarchy for permission checks
export const roleHierarchy: Record<Role, Role[]> = {
  [Role.ADMIN]: [Role.ADMIN, Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.AGENT]: [Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.CUSTOMER]: [Role.CUSTOMER, Role.GUEST],
  [Role.GUEST]: [Role.GUEST]
};

// Check if a role has permission to perform actions for another role
export const hasPermission = (userRole: Role, targetRole: Role): boolean => {
  return roleHierarchy[userRole]?.includes(targetRole) ?? false;
};

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: Role;
  isActive: boolean;
  isSuperuser: boolean;
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
export { Role };

