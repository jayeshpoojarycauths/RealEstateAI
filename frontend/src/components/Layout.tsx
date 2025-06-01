import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Card,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemPrefix,
} from '@material-tailwind/react';
import { useAuthContext } from '../contexts/AuthContext';
import { Role, isPlatformAdmin } from '../types/auth';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthContext();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

  const menuItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: '📊',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN, Role.MANAGER, Role.AGENT, Role.ANALYST],
    },
    {
      label: 'Properties',
      path: '/properties',
      icon: '🏠',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN, Role.MANAGER, Role.AGENT],
    },
    {
      label: 'Customers',
      path: '/customers',
      icon: '👥',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN, Role.MANAGER, Role.AGENT],
    },
    {
      label: 'Analytics',
      path: '/analytics',
      icon: '📈',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN, Role.ANALYST],
    },
    {
      label: 'User Management',
      path: '/admin/users',
      icon: '👤',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN],
    },
    {
      label: 'Audit Logs',
      path: '/audit-logs',
      icon: '📝',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.AUDITOR],
    },
    {
      label: 'Settings',
      path: '/settings',
      icon: '⚙️',
      roles: [Role.PLATFORM_ADMIN, Role.SUPERADMIN, Role.ADMIN],
    },
    // Platform admin only menu items
    ...(isPlatformAdmin(user?.role as Role)
      ? [
          {
            label: 'Tenants',
            path: '/platform/tenants',
            icon: '🏢',
            roles: [Role.PLATFORM_ADMIN],
          },
          {
            label: 'System Settings',
            path: '/platform/settings',
            icon: '🔧',
            roles: [Role.PLATFORM_ADMIN],
          },
        ]
      : []),
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <Card className="sticky top-0 z-10 rounded-none">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <IconButton
              variant="text"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <span className="text-2xl">☰</span>
            </IconButton>
            <Typography variant="h5">Real Estate AI</Typography>
          </div>
          <div className="flex items-center gap-4">
            <Typography variant="small">
              {user?.firstName} {user?.lastName}
              {user?.role && (
                <span className="ml-2 text-gray-500">
                  ({user.role.replace('_', ' ')})
                </span>
              )}
            </Typography>
            <Button
              variant="text"
              color="red"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </div>
        </div>
      </Card>

      <div className="flex">
        {/* Sidebar */}
        <Drawer
          open={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          className="bg-white"
        >
          <List>
            {menuItems
              .filter((item) => item.roles.includes(user?.role as Role))
              .map((item) => (
                <ListItem
                  key={item.path}
                  selected={location.pathname === item.path}
                  onClick={() => navigate(item.path)}
                >
                  <ListItemPrefix>
                    <span className="text-xl">{item.icon}</span>
                  </ListItemPrefix>
                  {item.label}
                </ListItem>
              ))}
          </List>
        </Drawer>

        {/* Main Content */}
        <div className="flex-1 p-4">
          {children}
        </div>
      </div>
    </div>
  );
}; 