import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Select,
  Option,
  Input
} from '@material-tailwind/react';
import { DateRangePicker, Range, RangeKeyDict } from 'react-date-range';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';
import PropertyTrendChart from '../../components/analytics/PropertyTrendChart';
import LeadScoreChart from '../../components/analytics/LeadScoreChart';
import ConversionFunnelChart from '../../components/analytics/ConversionFunnelChart';

interface DateRange {
  startDate: Date;
  endDate: Date;
  key: string;
}

const defaultEventHandlers = {
  onPointerEnterCapture: () => {},
  onPointerLeaveCapture: () => {},
  onResize: () => {},
  onResizeCapture: () => {}
};

const AnalyticsDashboard: React.FC = () => {
  // Filter states
  const [dateRange, setDateRange] = useState<DateRange>({
    startDate: new Date(new Date().setMonth(new Date().getMonth() - 6)),
    endDate: new Date(),
    key: 'selection'
  });
  const [propertyType, setPropertyType] = useState<string>('');
  const [location, setLocation] = useState<string>('');

  // Format dates for API
  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  // Handle date range change
  const handleDateRangeChange = (ranges: RangeKeyDict) => {
    const selection = ranges.selection;
    if (selection.startDate && selection.endDate) {
      setDateRange({
        startDate: selection.startDate,
        endDate: selection.endDate,
        key: 'selection'
      });
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <Typography 
          variant="h4" 
          color="blue-gray" 
          className="mb-2"
          {...defaultEventHandlers}
        >
          Analytics Dashboard
        </Typography>
        <Typography 
          variant="paragraph" 
          color="gray"
          {...defaultEventHandlers}
        >
          View and analyze your real estate data
        </Typography>
      </div>

      {/* Filters */}
      <Card className="mb-8" {...defaultEventHandlers}>
        <CardBody {...defaultEventHandlers}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Property Type Filter */}
            <div>
              <Typography 
                variant="small" 
                color="blue-gray" 
                className="mb-2 font-medium"
                {...defaultEventHandlers}
              >
                Property Type
              </Typography>
              <Select
                value={propertyType}
                onChange={(value: string) => setPropertyType(value)}
                {...defaultEventHandlers}
              >
                <Option value="">All Types</Option>
                <Option value="apartment">Apartment</Option>
                <Option value="house">House</Option>
                <Option value="villa">Villa</Option>
                <Option value="plot">Plot</Option>
              </Select>
            </div>

            {/* Location Filter */}
            <div>
              <Typography 
                variant="small" 
                color="blue-gray" 
                className="mb-2 font-medium"
                {...defaultEventHandlers}
              >
                Location
              </Typography>
              <Input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter location"
                crossOrigin={undefined}
                {...defaultEventHandlers}
              />
            </div>

            {/* Date Range Filter */}
            <div>
              <Typography 
                variant="small" 
                color="blue-gray" 
                className="mb-2 font-medium"
                {...defaultEventHandlers}
              >
                Date Range
              </Typography>
              <DateRangePicker
                ranges={[dateRange]}
                onChange={handleDateRangeChange}
                months={1}
                direction="horizontal"
                className="w-full"
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Property Trends */}
        <div className="lg:col-span-2">
          <PropertyTrendChart
            propertyType={propertyType}
            location={location}
            startDate={formatDate(dateRange.startDate)}
            endDate={formatDate(dateRange.endDate)}
          />
        </div>

        {/* Lead Score Distribution */}
        <div>
          <LeadScoreChart
            startDate={formatDate(dateRange.startDate)}
            endDate={formatDate(dateRange.endDate)}
          />
        </div>

        {/* Conversion Funnel */}
        <div>
          <ConversionFunnelChart
            startDate={formatDate(dateRange.startDate)}
            endDate={formatDate(dateRange.endDate)}
          />
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard; 