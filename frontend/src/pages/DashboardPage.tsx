import React, { useEffect, useState } from "react";
import {
  SafeCard as Card,
  SafeCardBody as CardBody,
  SafeCardHeader as CardHeader,
  SafeTypography as Typography,
  SafeButton as Button,
} from "../components/SafeMTW";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";
import api from "../services/api";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";

const statIcons = {
  leads: UserGroupIcon,
  projects: BuildingOfficeIcon,
  revenue: CurrencyDollarIcon,
  conversion: ChartBarIcon,
};

const reportEndpoints = {
  Daily: "/reports/daily",
  Weekly: "/reports/weekly",
  Monthly: "/reports/monthly",
  Quarterly: "/reports/quarterly",
};

// Mock data for demonstration
const recentLeads = [
  {
    name: 'Sarah Mitchell',
    email: 'sarah@techcorp.com',
    company: 'TechCorp Inc.',
    status: 'Qualified',
    source: 'Website',
    value: 15000,
    date: '5/10/2024',
  },
  {
    name: 'Michael Johnson',
    email: 'mike@startup.io',
    company: 'Startup.io',
    status: 'Contacted',
    source: 'Email',
    value: 8500,
    date: '5/09/2024',
  },
  {
    name: 'Emily Smith',
    email: 'emily@designco.com',
    company: 'DesignCo',
    status: 'New',
    source: 'Social',
    value: 12000,
    date: '5/08/2024',
  },
];

const recentActivity = [
  {
    message: 'New lead Sarah Mitchell added from TechCorp Inc.',
    time: '2 hours ago',
  },
  {
    message: 'Project Website Redesign completed successfully',
    time: '4 hours ago',
  },
  {
    message: 'Email campaign sent to 45 qualified leads',
    time: '6 hours ago',
  },
  {
    message: 'Meeting scheduled with Michael Johnson',
    time: 'Yesterday',
  },
];

const quickActions = [
  {
    title: 'Add New Lead',
    description: 'Create a new lead entry',
    icon: UserGroupIcon,
  },
  {
    title: 'New Project',
    description: 'Start a new project',
    icon: BuildingOfficeIcon,
  },
  {
    title: 'Send Campaign',
    description: 'Launch outreach campaign',
    icon: ChartBarIcon,
  },
  {
    title: 'View Analytics',
    description: 'Check performance metrics',
    icon: CurrencyDollarIcon,
  },
];

export const DashboardPage: React.FC = () => {
  const {
    getButtonProps,
    getCardProps,
    getCardBodyProps,
    getCardHeaderProps,
    getTypographyProps,
  } = useMaterialTailwind();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");
  const [reportSuccess, setReportSuccess] = useState("");

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await api.get("/stats/stats");
        setStats(response.data);
      } catch (e: any) {
        setError(
          e?.response?.data?.detail || "Failed to fetch dashboard stats",
        );
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const handleReportSelect = async (type: string) => {
    setReportLoading(true);
    setReportError("");
    setReportSuccess("");
    try {
      const endpoint = reportEndpoints[type as keyof typeof reportEndpoints];
      const response = await api.get(endpoint);
      setReportSuccess(`${type} report generated!`);
      // Optionally, handle the report data (download, show modal, etc.)
    } catch (e: any) {
      setReportError(
        e?.response?.data?.detail || `Failed to generate ${type} report`,
      );
    } finally {
      setReportLoading(false);
    }
  };

  const statCards = stats
    ? [
        {
          title: "Total Leads",
          value: stats.lead_stats?.total_leads ?? "-",
          change: stats.lead_stats?.change ?? "",
          icon: UserGroupIcon,
          color: "blue",
        },
        {
          title: "Active Projects",
          value: stats.project_stats?.active_projects ?? "-",
          change: stats.project_stats?.change ?? "",
          icon: BuildingOfficeIcon,
          color: "green",
        },
        {
          title: "Revenue",
          value: stats.project_stats?.revenue
            ? `$${stats.project_stats.revenue.toLocaleString()}`
            : "-",
          change: stats.project_stats?.revenue_change ?? "",
          icon: CurrencyDollarIcon,
          color: "amber",
        },
        {
          title: "Conversion Rate",
          value: stats.lead_stats?.conversion_rate
            ? `${stats.lead_stats.conversion_rate}%`
            : "-",
          change: stats.lead_stats?.conversion_rate_change ?? "",
          icon: ChartBarIcon,
          color: "purple",
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <Typography variant="h4" color="blue-gray" {...getTypographyProps()}>
          Dashboard
        </Typography>
        <div className="w-auto">
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <Button
                variant="filled"
                color="blue"
                className="flex items-center gap-2 px-4 py-2 whitespace-nowrap"
                {...getButtonProps()}
                disabled={reportLoading}
              >
                <ChartBarIcon className="h-5 w-5" />
                {reportLoading ? "Generating..." : "Generate Report"}
              </Button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content
              className="bg-white border border-blue-gray-100 rounded-lg shadow-lg py-2 min-w-[12rem] z-50"
              align="end"
            >
              {Object.keys(reportEndpoints).map((type) => (
                <DropdownMenu.Item
                  key={type}
                  className="px-4 py-2 text-blue-gray-700 hover:bg-blue-100 cursor-pointer rounded transition-colors text-base"
                  onSelect={() => handleReportSelect(type)}
                >
                  {type} Report
                </DropdownMenu.Item>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      </div>

      {reportError && (
        <div className="text-red-600 font-medium">{reportError}</div>
      )}
      {reportSuccess && (
        <div className="text-green-600 font-medium">{reportSuccess}</div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <span className="text-blue-gray-400 text-lg">
            Loading dashboard...
          </span>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-40">
          <span className="text-red-600 text-lg">{error}</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.title} {...getCardProps()}>
                <CardBody {...getCardBodyProps()}>
                  <div className="flex items-center justify-between">
                    <div>
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                        {...getTypographyProps()}
                      >
                        {stat.title}
                      </Typography>
                      <Typography
                        variant="h4"
                        color="blue-gray"
                        {...getTypographyProps()}
                      >
                        {stat.value}
                      </Typography>
                    </div>
                    <Icon className={`h-8 w-8 text-${stat.color}-400`} />
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>
      )}

      {/* Main Content: Recent Leads & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Leads Table */}
        <Card className="col-span-2" {...getCardProps()}>
          <CardHeader {...getCardHeaderProps()}>
            <div className="flex items-center justify-between">
              <Typography variant="h6" {...getTypographyProps()}>
                Recent Leads
              </Typography>
              <div className="flex gap-2">
                <Button variant="outlined" color="blue" {...getButtonProps()}>
                  Export
                </Button>
                <Button variant="filled" color="blue" {...getButtonProps()}>
                  + Add Lead
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <table className="min-w-full text-left">
              <thead>
                <tr>
                  <th>Lead</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Source</th>
                  <th>Value</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {recentLeads.map((lead, idx) => (
                  <tr key={idx} className="border-t">
                    <td>
                      <div className="font-semibold">{lead.name}</div>
                      <div className="text-xs text-gray-500">{lead.email}</div>
                    </td>
                    <td>{lead.company}</td>
                    <td>
                      <span className="inline-block px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs">
                        {lead.status}
                      </span>
                    </td>
                    <td>{lead.source}</td>
                    <td>${lead.value.toLocaleString()}</td>
                    <td>{lead.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>

        {/* Recent Activity Feed */}
        <Card {...getCardProps()}>
          <CardHeader {...getCardHeaderProps()}>
            <Typography variant="h6" {...getTypographyProps()}>
              Recent Activity
            </Typography>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <ul className="space-y-4">
              {recentActivity.map((activity, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-400 inline-block" />
                  <div>
                    <div className="text-sm">{activity.message}</div>
                    <div className="text-xs text-gray-400">{activity.time}</div>
                  </div>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card {...getCardProps()}>
        <CardHeader {...getCardHeaderProps()}>
          <Typography variant="h6" {...getTypographyProps()}>
            Quick Actions
          </Typography>
        </CardHeader>
        <CardBody {...getCardBodyProps()}>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, idx) => {
              const Icon = action.icon;
              return (
                <Button
                  key={idx}
                  variant="outlined"
                  color="blue"
                  className="flex flex-col items-start gap-2 p-4 h-full w-full"
                  {...getButtonProps()}
                >
                  <Icon className="h-6 w-6 mb-2 text-blue-400" />
                  <span className="font-semibold">{action.title}</span>
                  <span className="text-xs text-gray-500">{action.description}</span>
                </Button>
              );
            })}
          </div>
        </CardBody>
      </Card>
    </div>
  );
};
