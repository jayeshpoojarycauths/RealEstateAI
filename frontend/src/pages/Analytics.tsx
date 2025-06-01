import {
  Card,
  CardHeader,
  CardBody,
  Typography,
} from "@material-tailwind/react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../config/api";
import { LoadingSpinner } from "../components/common/LoadingStates";

interface AnalyticsData {
  totalProperties: number;
  activeListings: number;
  totalCustomers: number;
  totalLeads: number;
  monthlyRevenue: number;
  conversionRate: number;
}

export const Analytics = () => {
  const { data: analytics, isLoading } = useQuery<AnalyticsData>({
    queryKey: ["analytics"],
    queryFn: async () => {
      const { data } = await api.get("/analytics");
      return data;
    },
  });

  if (isLoading) {
    return <LoadingSpinner size="lg" />;
  }

  if (error) {
    return (
      <div className="text-center">
        <Typography variant="h6" color="red">
          Failed to load analytics data
        </Typography>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <Typography variant="h4" color="blue-gray">
        Analytics Dashboard
      </Typography>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader color="blue" className="mb-4">
            <Typography variant="h6">Properties Overview</Typography>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              <div>
                <Typography variant="small" color="blue-gray">
                  Total Properties
                </Typography>
                <Typography variant="h4">
                  {analytics?.totalProperties}
                </Typography>
              </div>
              <div>
                <Typography variant="small" color="blue-gray">
                  Active Listings
                </Typography>
                <Typography variant="h4">
                  {analytics?.activeListings}
                </Typography>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader color="green" className="mb-4">
            <Typography variant="h6">Customer Metrics</Typography>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              <div>
                <Typography variant="small" color="blue-gray">
                  Total Customers
                </Typography>
                <Typography variant="h4">
                  {analytics?.totalCustomers}
                </Typography>
              </div>
              <div>
                <Typography variant="small" color="blue-gray">
                  Total Leads
                </Typography>
                <Typography variant="h4">{analytics?.totalLeads}</Typography>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader color="amber" className="mb-4">
            <Typography variant="h6">Performance Metrics</Typography>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              <div>
                <Typography variant="small" color="blue-gray">
                  Monthly Revenue
                </Typography>
                <Typography variant="h4">
                  ${analytics?.monthlyRevenue.toLocaleString()}
                </Typography>
              </div>
              <div>
                <Typography variant="small" color="blue-gray">
                  Conversion Rate
                </Typography>
                <Typography variant="h4">
                  {analytics?.conversionRate?.toFixed(1) || "0.0"}%
                </Typography>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};
