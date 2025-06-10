import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  SafeCard,
  SafeTypography,
  SafeButton,
  SafeIconButton,
  SafeDrawer,
  SafeList,
  SafeListItem,
  SafeListItemPrefix,
} from "../components/SafeMTW";
import { useAuthContext } from "../contexts/AuthContext";
import {
  menuItems as configMenuItems,
  filterMenuItemsByRole,
} from "../config/menuConfig";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthContext();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

  // Filter menu items by user role
  const filteredMenuItems = user?.role
    ? filterMenuItemsByRole(user.role, configMenuItems)
    : [];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <SafeCard className="sticky top-0 z-10 rounded-none">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <SafeIconButton
              variant="text"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <span className="text-2xl">☰</span>
            </SafeIconButton>
            <SafeTypography variant="h5">Real Estate AI</SafeTypography>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <SafeTypography variant="small">
                {user.firstName} {user.lastName}
                {user.role && (
                  <span className="ml-2 text-gray-500">
                    ({user.role.replace("_", " ")})
                  </span>
                )}
              </SafeTypography>
            )}
          </div>
        </div>
      </SafeCard>

      <div className="flex">
        {/* Sidebar */}
        <SafeDrawer
          open={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          className="bg-white"
        >
          <SafeList>
            {filteredMenuItems.map((item) => (
              <SafeListItem
                key={item.path}
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
              >
                <SafeListItemPrefix>
                  {item.icon ? (
                    <item.icon className="h-5 w-5 text-blue-500" />
                  ) : (
                    <span className="text-xl">?</span>
                  )}
                </SafeListItemPrefix>
                {item.label}
              </SafeListItem>
            ))}
          </SafeList>
        </SafeDrawer>

        {/* Main Content */}
        <div className="flex-1 p-4">{children}</div>
      </div>
    </div>
  );
};
