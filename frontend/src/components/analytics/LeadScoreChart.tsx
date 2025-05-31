import React, { useEffect, useState } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    TooltipProps
} from 'recharts';
import { Card, CardHeader, CardBody, Typography } from '@material-tailwind/react';
import axios, { AxiosError } from 'axios';
import { useAuth } from '../../hooks/useAuth';
import { config } from '../../config';
import { api } from '../../services/api';

interface ScoreBucket {
    range: string;
    count: number;
}

interface LeadScoreDistribution {
    total_leads: number;
    buckets: ScoreBucket[];
}

interface ChartDataPoint {
    name: string;
    count: number;
    percentage: string;
}

interface LeadScoreChartProps {
    startDate?: string;
    endDate?: string;
    className?: string;
    title?: string;
    showTotalLeads?: boolean;
}

const defaultEventHandlers = {
    onPointerEnterCapture: () => {},
    onPointerLeaveCapture: () => {},
    onResize: () => {},
    onResizeCapture: () => {},
    placeholder: undefined
};

const LeadScoreChart: React.FC<LeadScoreChartProps> = ({
    startDate,
    endDate,
    className = '',
    title = 'Lead Score Distribution',
    showTotalLeads = true
}) => {
    const [data, setData] = useState<LeadScoreDistribution | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { getAuthHeaders } = useAuth();

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                const params = new URLSearchParams();
                if (startDate) params.append('start_date', startDate);
                if (endDate) params.append('end_date', endDate);

                const response = await api.get<LeadScoreDistribution>(
                    `${config.apiUrl}/v1/stats/lead-score/?${params.toString()}`,
                    { 
                        headers: getAuthHeaders(),
                        withCredentials: true 
                    }
                );

                setData(response.data);
            } catch (err) {
                const error = err as AxiosError;
                setError('Failed to fetch lead score data');
                console.error('Error fetching lead scores:', error.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [startDate, endDate, getAuthHeaders]);

    if (loading) {
        return (
            <Card className={`w-full ${className}`} {...defaultEventHandlers}>
                <CardBody {...defaultEventHandlers}>
                    <Typography {...defaultEventHandlers}>
                        Loading lead score distribution...
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

    if (!data) {
        return null;
    }

    const chartData: ChartDataPoint[] = data.buckets.map(bucket => ({
        name: bucket.range,
        count: bucket.count,
        percentage: ((bucket.count / data.total_leads) * 100).toFixed(1)
    }));

    const formatTooltip = (value: number, name: string): [string, string] => {
        const dataPoint = chartData.find(d => d.count === value);
        return [`${value} (${dataPoint?.percentage ?? '0'}%)`, name];
    };

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
                {showTotalLeads && (
                    <Typography color="white" className="font-normal" {...defaultEventHandlers}>
                        Total Leads: {data.total_leads}
                    </Typography>
                )}
            </CardHeader>
            <CardBody {...defaultEventHandlers}>
                <div className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={chartData}
                            margin={{
                                top: 5,
                                right: 30,
                                left: 20,
                                bottom: 5,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                                dataKey="name"
                                tick={{ fontSize: 12 }}
                            />
                            <YAxis
                                tick={{ fontSize: 12 }}
                            />
                            <Tooltip formatter={formatTooltip} />
                            <Legend />
                            <Bar
                                dataKey="count"
                                name="Number of Leads"
                                fill="#2563eb"
                                radius={[4, 4, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardBody>
        </Card>
    );
};

export default LeadScoreChart; 