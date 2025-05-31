import React from 'react';
import { Card, Typography } from '@material-tailwind/react';
import LeadScoreChart from '@/components/analytics/LeadScoreChart';

interface AnalyticsPageProps {
    className?: string;
}

const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ className = '' }) => {
    return (
        <div className={`p-6 ${className}`}>
            <Typography 
                variant="h4" 
                className="mb-6 text-blue-gray-900"
                placeholder={undefined}
                onResize={undefined}
                onResizeCapture={undefined}
                onPointerEnterCapture={undefined}
                onPointerLeaveCapture={undefined}
            >
                Analytics Dashboard
            </Typography>
            
            <div className="grid grid-cols-1 gap-6">
                <LeadScoreChart />
                
                {/* Add more analytics components here */}
            </div>
        </div>
    );
};

export default AnalyticsPage; 