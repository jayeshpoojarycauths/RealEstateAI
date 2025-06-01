export enum Role {
  PLATFORM_ADMIN = 'platform_admin',
  SUPERADMIN = 'superadmin',
  ADMIN = 'admin',
  MANAGER = 'manager',
  AGENT = 'agent',
  ANALYST = 'analyst',
  AUDITOR = 'auditor',
}

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

// Role-based access control types
export interface RoleBasedAccess {
  requiredRoles: Role[];
  checkAccess: (userRole: Role) => boolean;
}

// Create a role-based access control object
export const createRoleAccess = (roles: Role[]): RoleBasedAccess => ({
  requiredRoles: roles,
  checkAccess: (userRole: Role) => roles.some(role => hasPermission(userRole, role)),
}); 