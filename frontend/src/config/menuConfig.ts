import { Role } from "../types/auth";
import {
  HomeIcon,
  UserIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  CogIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";

/**
 * Interface for menu items
 * @property {string} path - The route path
 * @property {string} label - Display label
 * @property {React.ComponentType} icon - Icon component
 * @property {Role[]} roles - Array of roles that can access this item
 * @property {MenuItem[]} [children] - Optional submenu items
 */
export interface MenuItem {
  path: string;
  label: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  roles: Role[];
  children?: MenuItem[];
}

/**
 * Menu configuration with role-based access control
 * Each menu item specifies which roles can access it
 * Child items inherit parent role restrictions
 */
export const menuItems: MenuItem[] = [
  {
    path: "/dashboard",
    label: "Dashboard",
    icon: HomeIcon,
    roles: [Role.ADMIN, Role.MANAGER, Role.AGENT],
  },
  {
    path: "/admin",
    label: "Admin",
    icon: CogIcon,
    roles: [Role.ADMIN],
    children: [
      {
        path: "/admin/users",
        label: "User Management",
        icon: UserIcon,
        roles: [Role.ADMIN],
      },
      {
        path: "/admin/audit-logs",
        label: "Audit Logs",
        icon: ChartBarIcon,
        roles: [Role.ADMIN],
      },
    ],
  },
  {
    path: "/properties",
    label: "Properties",
    icon: BuildingOfficeIcon,
    roles: [Role.ADMIN, Role.MANAGER, Role.AGENT],
  },
  {
    path: "/customers",
    label: "Customers",
    icon: UserGroupIcon,
    roles: [Role.ADMIN, Role.MANAGER, Role.AGENT],
  },
];

/**
 * Helper function to check if a user has access to a menu item
 * @param {Role} userRole - The user's role
 * @param {MenuItem} menuItem - The menu item to check
 * @returns {boolean} - Whether the user has access
 */
export const hasMenuAccess = (userRole: Role, menuItem: MenuItem): boolean => {
  if (menuItem.roles.includes(userRole)) {
    return true;
  }
  return false;
};

/**
 * Helper function to filter menu items based on user role
 * @param {Role} userRole - The user's role
 * @param {MenuItem[]} items - Menu items to filter
 * @returns {MenuItem[]} - Filtered menu items
 */
export const filterMenuItemsByRole = (
  userRole: Role,
  items: MenuItem[],
): MenuItem[] => {
  return items
    .filter((item) => hasMenuAccess(userRole, item))
    .map((item) => ({
      ...item,
      children: item.children
        ? filterMenuItemsByRole(userRole, item.children)
        : undefined,
    }));
};
