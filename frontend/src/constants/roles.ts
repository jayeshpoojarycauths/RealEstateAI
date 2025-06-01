/**
 * User roles in the application
 * These roles are used for access control and permissions
 */
export const ROLES = {
    ADMIN: 'admin',
    AGENT: 'agent',
    CUSTOMER: 'customer',
} as const;

export type Role = typeof ROLES[keyof typeof ROLES];

/**
 * Role hierarchy for access control
 * Higher roles inherit permissions from lower roles
 */
export const ROLE_HIERARCHY: Record<Role, Role[]> = {
    [ROLES.ADMIN]: [ROLES.ADMIN, ROLES.AGENT, ROLES.CUSTOMER],
    [ROLES.AGENT]: [ROLES.AGENT, ROLES.CUSTOMER],
    [ROLES.CUSTOMER]: [ROLES.CUSTOMER],
};

/**
 * Check if a user has access to a specific role
 * @param userRole - The user's role
 * @param requiredRole - The role required for access
 * @returns boolean indicating if the user has access
 */
export const hasRoleAccess = (userRole: Role, requiredRole: Role): boolean => {
    return ROLE_HIERARCHY[userRole]?.includes(requiredRole) || false;
};

/**
 * Check if a user has access to any of the required roles
 * @param userRole - The user's role
 * @param requiredRoles - Array of roles that grant access
 * @returns boolean indicating if the user has access
 */
export const hasAnyRoleAccess = (userRole: Role, requiredRoles: Role[]): boolean => {
    return requiredRoles.some((role) => hasRoleAccess(userRole, role));
}; 