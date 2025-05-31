import React, { useEffect, useState } from 'react';
import { Card, CardBody, CardHeader, Typography } from '@material-tailwind/react';
import { useAuth } from '../../contexts/AuthContext';
import { LeadQualityResponse, LeadQualityMetric } from '../../types/analytics';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import api from '../../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

interface LeadQualityChartProps {
  className?: string;
}

export const LeadQualityChart: React.FC<LeadQualityChartProps> = ({ className }) => {
  const [data, setData] = useState<LeadQualityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { getAuthHeader } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/api/v1/stats/lead-quality');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching lead quality data:', error);
        throw new Error('Failed to fetch lead quality data');
      }
    };

    fetchData();
  }, [getAuthHeader]);

  if (error) {
    return (
      <Card className={className} placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
        <CardBody placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
          <Typography color="red" placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
            {error}
          </Typography>
        </CardBody>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className={className} placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
        <CardBody placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
          <Typography placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
            Loading...
          </Typography>
        </CardBody>
      </Card>
    );
  }

  const chartData = data.source_distribution.map((metric: LeadQualityMetric) => ({
    name: metric.name,
    value: metric.value,
  }));

  return (
    <Card className={className} placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
      <CardHeader
        variant="gradient"
        color="blue"
        className="mb-4 p-6"
        placeholder={undefined}
        onPointerEnterCapture={undefined}
        onPointerLeaveCapture={undefined}
        onResize={undefined}
        onResizeCapture={undefined}
      >
        <Typography variant="h6" color="white" placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
          Lead Quality Distribution
        </Typography>
      </CardHeader>
      <CardBody placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <Typography variant="small" color="gray" className="mt-4 text-center" placeholder={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} onResize={undefined} onResizeCapture={undefined}>
          Total Leads: {data.total_leads}
        </Typography>
      </CardBody>
    </Card>
  );
}; 