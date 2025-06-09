import { Role } from '../types/roles';
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
  title: string;
  path: string;
  icon?: string;
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
    title: 'Dashboard',
    path: '/dashboard',
    icon: 'dashboard',
    roles: [Role.ADMIN, Role.AGENT, Role.CUSTOMER, Role.GUEST]
  },
  {
    title: 'Leads',
    path: '/leads',
    icon: 'people',
    roles: [Role.ADMIN, Role.AGENT],
    children: [
      {
        title: 'All Leads',
        path: '/leads',
        roles: [Role.ADMIN, Role.AGENT]
      },
      {
        title: 'My Leads',
        path: '/leads/my',
        roles: [Role.ADMIN, Role.AGENT]
      }
    ]
  },
  {
    title: 'Properties',
    path: '/properties',
    icon: 'home',
    roles: [Role.ADMIN, Role.AGENT, Role.CUSTOMER, Role.GUEST],
    children: [
      {
        title: 'All Properties',
        path: '/properties',
        roles: [Role.ADMIN, Role.AGENT, Role.CUSTOMER, Role.GUEST]
      },
      {
        title: 'My Properties',
        path: '/properties/my',
        roles: [Role.ADMIN, Role.AGENT]
      }
    ]
  },
  {
    title: 'Users',
    path: '/users',
    icon: 'person',
    roles: [Role.ADMIN],
    children: [
      {
        title: 'All Users',
        path: '/users',
        roles: [Role.ADMIN]
      },
      {
        title: 'Agents',
        path: '/users/agents',
        roles: [Role.ADMIN]
      },
      {
        title: 'Customers',
        path: '/users/customers',
        roles: [Role.ADMIN]
      }
    ]
  },
  {
    title: 'Settings',
    path: '/settings',
    icon: 'settings',
    roles: [Role.ADMIN, Role.AGENT],
    children: [
      {
        title: 'Profile',
        path: '/settings/profile',
        roles: [Role.ADMIN, Role.AGENT, Role.CUSTOMER]
      },
      {
        title: 'Account',
        path: '/settings/account',
        roles: [Role.ADMIN, Role.AGENT]
      },
      {
        title: 'System',
        path: '/settings/system',
        roles: [Role.ADMIN]
      }
    ]
  }
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
