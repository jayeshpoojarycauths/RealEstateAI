import React, { useEffect, useState } from "react";
import {
  SafeCard as Card,
  SafeCardBody as CardBody,
  SafeCardHeader as CardHeader,
  SafeTypography as Typography,
  SafeButton as Button,
} from "../components/SafeMTW";
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";
import api from '../services/api';
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";

const statIcons = {
  leads: UserGroupIcon,
  projects: BuildingOfficeIcon,
  revenue: CurrencyDollarIcon,
  conversion: ChartBarIcon,
};

const reportEndpoints = {
  Daily: '/reports/daily',
  Weekly: '/reports/weekly',
  Monthly: '/reports/monthly',
  Quarterly: '/reports/quarterly',
};

export const DashboardPage: React.FC = () => {
  const { getButtonProps, getCardProps, getCardBodyProps, getCardHeaderProps, getTypographyProps } = useMaterialTailwind();
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
        const response = await api.get('/stats/stats');
        setStats(response.data);
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to fetch dashboard stats');
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
      setReportError(e?.response?.data?.detail || `Failed to generate ${type} report`);
    } finally {
      setReportLoading(false);
    }
  };

  const statCards = stats ? [
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
      value: stats.project_stats?.revenue ? `$${stats.project_stats.revenue.toLocaleString()}` : "-",
      change: stats.project_stats?.revenue_change ?? "",
      icon: CurrencyDollarIcon,
      color: "amber",
    },
    {
      title: "Conversion Rate",
      value: stats.lead_stats?.conversion_rate ? `${stats.lead_stats.conversion_rate}%` : "-",
      change: stats.lead_stats?.conversion_rate_change ?? "",
      icon: ChartBarIcon,
      color: "purple",
    },
  ] : [];

  return (
    <div className="space-y-6">
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
                {reportLoading ? 'Generating...' : 'Generate Report'}
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


      {reportError && <div className="text-red-600 font-medium">{reportError}</div>}
      {reportSuccess && <div className="text-green-600 font-medium">{reportSuccess}</div>}

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <span className="text-blue-gray-400 text-lg">Loading dashboard...</span>
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
                    <div className="rounded-full bg-blue-50 p-3">
                      <Icon className={`h-6 w-6 text-${stat.color}-500`} />
                    </div>
                  </div>
                  <div className="mt-4">
                    <Typography
                      variant="small"
                      color="green"
                      className="flex items-center gap-1 font-normal"
                      {...getTypographyProps()}
                    >
                      {stat.change}
                    </Typography>
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card {...getCardProps()}>
          <CardHeader
            variant="gradient"
            color="blue"
            className="mb-4 p-6"
            {...getCardHeaderProps()}
          >
            <Typography variant="h6" color="white" {...getTypographyProps()}>
              Recent Leads
            </Typography>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <Typography variant="paragraph" color="blue-gray" {...getTypographyProps()}>
              Content coming soon...
            </Typography>
          </CardBody>
        </Card>

        <Card {...getCardProps()}>
          <CardHeader
            variant="gradient"
            color="blue"
            className="mb-4 p-6"
            {...getCardHeaderProps()}
          >
            <Typography variant="h6" color="white" {...getTypographyProps()}>
              Active Projects
            </Typography>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <Typography variant="paragraph" color="blue-gray" {...getTypographyProps()}>
              Content coming soon...
            </Typography>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}; 