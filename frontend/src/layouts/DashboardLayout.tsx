import React, { useState } from "react";
import { Outlet, useNavigate, useLocation, Link } from "react-router-dom";
import {
  SafeTypography as Typography,
  SafeButton as Button,
  SafeCard as Card,
  SafeCardBody as CardBody,
} from "../components/SafeMTW";
import { Collapse } from "@material-tailwind/react";
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  UserGroupIcon,
  FolderIcon,
  UserCircleIcon,
  ChartBarIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/outline";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";

interface DashboardLayoutProps {
  children?: React.ReactNode;
}

// Add a simple top navbar with a Home link
const Navbar: React.FC = () => (
  <nav className="w-full bg-white border-b border-blue-gray-100 px-6 py-3 flex items-center justify-between shadow-sm z-20">
    <div className="flex items-center gap-4">
      <Link
        to="/dashboard"
        className="text-lg font-semibold text-blue-700 hover:text-blue-900 transition-colors"
      >
        Home
      </Link>
    </div>
  </nav>
);

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
}) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [leadsDropdownOpen, setLeadsDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { getButtonProps, getCardProps, getCardBodyProps, getTypographyProps } =
    useMaterialTailwind();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const navItems = [
    // Leads is now handled as a dropdown
    {
      path: "/projects",
      icon: <FolderIcon className="h-5 w-5" />,
      label: "Projects",
    },
    {
      path: "/stats",
      icon: <ChartBarIcon className="h-5 w-5" />,
      label: "Analytics",
    },
    {
      path: "/profile",
      icon: <UserCircleIcon className="h-5 w-5" />,
      label: "Profile",
    },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-4 border-b">
            <Typography variant="h5" color="blue" {...getTypographyProps()}>
              Real Estate AI
            </Typography>
            <button
              onClick={toggleSidebar}
              className="md:hidden p-2 text-gray-500 hover:text-gray-700"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4">
            <ul className="space-y-2">
              {/* Leads Dropdown */}
              <li>
                <Button
                  variant={
                    location.pathname.startsWith("/leads") ? "filled" : "text"
                  }
                  color={
                    location.pathname.startsWith("/leads")
                      ? "blue"
                      : "blue-gray"
                  }
                  onClick={() => setLeadsDropdownOpen((open) => !open)}
                  className="rounded-lg w-full flex items-center justify-between"
                  {...getButtonProps()}
                >
                  <span className="flex items-center">
                    <UserGroupIcon className="h-5 w-5" />
                    <span className="ml-3">Leads</span>
                  </span>
                  {leadsDropdownOpen ? (
                    <ChevronUpIcon className="h-4 w-4 ml-2" />
                  ) : (
                    <ChevronDownIcon className="h-4 w-4 ml-2" />
                  )}
                </Button>
                <Collapse open={leadsDropdownOpen} className="pl-8">
                  <ul className="space-y-1 mt-2">
                    <li>
                      <Button
                        variant={isActive("/leads") ? "filled" : "text"}
                        color={isActive("/leads") ? "blue" : "blue-gray"}
                        onClick={() => navigate("/leads")}
                        className="rounded-lg w-full text-left"
                        {...getButtonProps()}
                      >
                        Leads Page
                      </Button>
                    </li>
                    <li>
                      <Button
                        variant={isActive("/leads/new") ? "filled" : "text"}
                        color={isActive("/leads/new") ? "blue" : "blue-gray"}
                        onClick={() => navigate("/leads/new")}
                        className="rounded-lg w-full text-left"
                        {...getButtonProps()}
                      >
                        Create New Lead
                      </Button>
                    </li>
                    <li>
                      <Button
                        variant={
                          isActive("/leads/import-export") ? "filled" : "text"
                        }
                        color={
                          isActive("/leads/import-export")
                            ? "blue"
                            : "blue-gray"
                        }
                        onClick={() => navigate("/leads/import-export")}
                        className="rounded-lg w-full text-left"
                        {...getButtonProps()}
                      >
                        Import/Export Leads
                      </Button>
                    </li>
                  </ul>
                </Collapse>
              </li>
              {/* Other nav items */}
              {navItems.map((item) => (
                <li key={item.path}>
                  <Button
                    variant={isActive(item.path) ? "filled" : "text"}
                    color={isActive(item.path) ? "blue" : "blue-gray"}
                    onClick={() => navigate(item.path)}
                    className="rounded-lg w-full flex items-center"
                    {...getButtonProps()}
                  >
                    {item.icon}
                    <span className="ml-3">{item.label}</span>
                  </Button>
                </li>
              ))}
            </ul>
          </nav>

          {/* Logout Button */}
          <div className="p-4 border-t">
            <Button
              variant="text"
              color="red"
              onClick={handleLogout}
              className="rounded-lg w-full flex items-center"
              {...getButtonProps()}
            >
              <XMarkIcon className="h-5 w-5" />
              <span className="ml-3">Logout</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col md:ml-64">
        <Navbar />
        {/* Top Bar */}
        <header className="bg-white shadow-sm">
          <div className="flex items-center justify-between p-4">
            <button
              onClick={toggleSidebar}
              className="md:hidden p-2 text-gray-500 hover:text-gray-700"
            >
              <Bars3Icon className="h-5 w-5" />
            </button>
            <Typography
              variant="h6"
              color="blue-gray"
              {...getTypographyProps()}
            >
              {location.pathname.startsWith("/leads/scraper")
                ? "Leads Scraper"
                : location.pathname.startsWith("/leads")
                  ? "Leads Page"
                  : navItems.find((item) => isActive(item.path))?.label ||
                    "Dashboard"}
            </Typography>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-auto">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
};
