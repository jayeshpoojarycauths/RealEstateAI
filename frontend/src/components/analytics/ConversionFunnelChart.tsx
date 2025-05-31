import React, { useEffect, useState } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import { Card, CardHeader, CardBody, Typography } from '@material-tailwind/react';
import { useAuth } from '../../contexts/AuthContext';
import { ConversionFunnelResponse, ConversionFunnelStage } from '../../types/analytics';
import { api } from '../../services/api';
import { config } from '../../config';

interface ConversionFunnelChartProps {
    className?: string;
}

export const ConversionFunnelChart: React.FC<ConversionFunnelChartProps> = ({ className }) => {
    const [data, setData] = useState<ConversionFunnelResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const { getAuthHeader } = useAuth();
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setIsLoading(true);
                const response = await api.get(`${config.apiUrl}/v1/stats/conversion-funnel/`);
                setData(response.data);
            } catch (error) {
                console.error('Error fetching conversion funnel data:', error);
                setError('Failed to load conversion funnel data');
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, []);

    if (error) {
        return (
            <Card className={className}>
                <CardBody>
                    <Typography color="red">
                        {error}
                    </Typography>
                </CardBody>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card className={className}>
                <CardBody>
                    <Typography>
                        Loading...
                    </Typography>
                </CardBody>
            </Card>
        );
    }

    const chartData = data.stages.map((stage: ConversionFunnelStage) => ({
        name: stage.stage,
        value: stage.count,
        percentage: stage.percentage,
    }));

    return (
        <Card className={className}>
            <CardHeader
                variant="gradient"
                color="blue"
                className="mb-4 p-6"
            >
                <Typography variant="h6" color="white">
                    Lead Conversion Funnel
                </Typography>
            </CardHeader>
            <CardBody>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={chartData}
                            margin={{
                                top: 20,
                                right: 30,
                                left: 20,
                                bottom: 5,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip
                                formatter={(value: number, name: string) => [
                                    `${value} (${chartData.find(d => d.name === name)?.percentage.toFixed(1)}%)`,
                                    name,
                                ]}
                            />
                            <Bar dataKey="value" fill="#8884d8" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                <Typography variant="small" color="gray" className="mt-4 text-center">
                    Total Leads: {data.total_leads}
                </Typography>
            </CardBody>
        </Card>
    );
}; 