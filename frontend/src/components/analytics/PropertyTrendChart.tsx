import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from "recharts";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
} from "@material-tailwind/react";
import api from "../../services/api";
import { useAuth } from "../../hooks/useAuth";
import { format } from "date-fns";

interface PriceTrendPoint {
  date: string;
  avg_price: number;
  count: number;
}

interface PropertyTrendChartProps {
  propertyType?: string;
  location?: string;
  startDate?: string;
  endDate?: string;
  className?: string;
  title?: string;
}

const defaultEventHandlers = {
  onPointerEnterCapture: () => {},
  onPointerLeaveCapture: () => {},
  onResize: () => {},
  onResizeCapture: () => {},
  placeholder: undefined,
};

const PropertyTrendChart: React.FC<PropertyTrendChartProps> = ({
  propertyType,
  location,
  startDate,
  endDate,
  className = "",
  title = "Property Price Trends",
}) => {
  const [data, setData] = useState<PriceTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = new URLSearchParams();
        if (startDate) params.append("start_date", startDate);
        if (endDate) params.append("end_date", endDate);
        if (propertyType) params.append("property_type", propertyType);
        if (location) params.append("location", location);

        const response = await api.get<PriceTrendPoint[]>(
          "/api/v1/stats/price-trends",
        );
        setData(response.data);
      } catch (error) {
        console.error("Error fetching property trend data:", error);
        setError("Failed to fetch property trend data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, propertyType, location, getAuthHeaders]);

  const formatPrice = (value: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading) {
    return (
      <Card className={`w-full ${className}`} {...defaultEventHandlers}>
        <CardBody {...defaultEventHandlers}>
          <Typography {...defaultEventHandlers}>
            Loading property trends...
          </Typography>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`w-full ${className}`} {...defaultEventHandlers}>
        <CardBody {...defaultEventHandlers}>
          <Typography color="red" {...defaultEventHandlers}>
            {error}
          </Typography>
        </CardBody>
      </Card>
    );
  }

  if (!data.length) {
    return (
      <Card className={`w-full ${className}`} {...defaultEventHandlers}>
        <CardBody {...defaultEventHandlers}>
          <Typography {...defaultEventHandlers}>
            No data available for the selected filters
          </Typography>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card className={`w-full ${className}`} {...defaultEventHandlers}>
      <CardHeader
        variant="gradient"
        color="blue"
        className="mb-4 p-6"
        {...defaultEventHandlers}
      >
        <Typography variant="h6" color="white" {...defaultEventHandlers}>
          {title}
        </Typography>
      </CardHeader>
      <CardBody {...defaultEventHandlers}>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => format(new Date(value), "MMM dd")}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12 }}
                tickFormatter={formatPrice}
                label={{
                  value: "Average Price",
                  angle: -90,
                  position: "insideLeft",
                  style: { textAnchor: "middle" },
                }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12 }}
                label={{
                  value: "Number of Properties",
                  angle: 90,
                  position: "insideRight",
                  style: { textAnchor: "middle" },
                }}
              />
              <Tooltip
                formatter={(value: number, name: string) => [
                  name === "avg_price" ? formatPrice(value) : value.toString(),
                  name === "avg_price"
                    ? "Average Price"
                    : "Number of Properties",
                ]}
                labelFormatter={(label) =>
                  format(new Date(label), "MMM dd, yyyy")
                }
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="avg_price"
                name="Average Price"
                stroke="#2563eb"
                activeDot={{ r: 8 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="count"
                name="Number of Properties"
                stroke="#93c5fd"
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardBody>
    </Card>
  );
};

export default PropertyTrendChart;
