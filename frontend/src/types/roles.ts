export enum Role {
  PLATFORM_ADMIN = "platform_admin",
  SUPERADMIN = "superadmin",
  ADMIN = "admin",
  MANAGER = "manager",
  ANALYST = "analyst",
  AUDITOR = "auditor",
  AGENT = "agent",
  CUSTOMER = "customer",
  GUEST = "guest"
}

// Role utility functions
export const isAdmin = (role: Role) => role === Role.ADMIN;
export const isAgent = (role: Role) => role === Role.AGENT;
export const isCustomer = (role: Role) => role === Role.CUSTOMER;
export const isGuest = (role: Role) => role === Role.GUEST;

// Role hierarchy for permission checks
export const roleHierarchy: Record<Role, Role[]> = {
  [Role.PLATFORM_ADMIN]: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN, Role.MANAGER, Role.ANALYST, Role.AUDITOR, Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.SUPERADMIN]: [Role.SUPERADMIN, Role.ADMIN, Role.MANAGER, Role.ANALYST, Role.AUDITOR, Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.ADMIN]: [Role.ADMIN, Role.MANAGER, Role.ANALYST, Role.AUDITOR, Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.MANAGER]: [Role.MANAGER, Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.ANALYST]: [Role.ANALYST, Role.GUEST],
  [Role.AUDITOR]: [Role.AUDITOR, Role.GUEST],
  [Role.AGENT]: [Role.AGENT, Role.CUSTOMER, Role.GUEST],
  [Role.CUSTOMER]: [Role.CUSTOMER, Role.GUEST],
  [Role.GUEST]: [Role.GUEST]
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
  checkAccess: (userRole: Role) =>
    roles.some((role) => hasPermission(userRole, role)),
});

// Role display names
export const roleDisplayNames: Record<Role, string> = {
  [Role.PLATFORM_ADMIN]: "Platform Administrator",
  [Role.SUPERADMIN]: "Super Administrator",
  [Role.ADMIN]: "Administrator",
  [Role.MANAGER]: "Manager",
  [Role.ANALYST]: "Analyst",
  [Role.AUDITOR]: "Auditor",
  [Role.AGENT]: "Agent",
  [Role.CUSTOMER]: "Customer",
  [Role.GUEST]: "Guest"
};
