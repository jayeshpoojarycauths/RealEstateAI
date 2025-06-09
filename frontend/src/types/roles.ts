export enum Role {
  ADMIN = "admin",
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
  [Role.ADMIN]: [Role.ADMIN, Role.AGENT, Role.CUSTOMER, Role.GUEST],
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
  [Role.ADMIN]: "Administrator",
  [Role.AGENT]: "Agent",
  [Role.CUSTOMER]: "Customer",
  [Role.GUEST]: "Guest"
};
