import React from 'react';
import { Card, CardBody } from '@material-tailwind/react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', color = 'blue' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClasses[size]} border-4 border-gray-200 border-t-${color}-500 rounded-full animate-spin`}
      />
    </div>
  );
};

interface LoadingCardProps {
  rows?: number;
}

export const LoadingCard: React.FC<LoadingCardProps> = ({ rows = 3 }) => {
  return (
    <Card className="w-full">
      <CardBody>
        <div className="space-y-4">
          {Array.from({ length: rows }).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

interface LoadingTableProps {
  columns: number;
  rows: number;
}

export const LoadingTable: React.FC<LoadingTableProps> = ({ columns, rows }) => {
  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr>
            {Array.from({ length: columns }).map((_, index) => (
              <th key={index} className="p-4">
                <div className="h-4 bg-gray-200 rounded animate-pulse" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="p-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

interface LoadingOverlayProps {
  show: boolean;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ show, message = 'Loading...' }) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-700">{message}</p>
      </div>
    </div>
  );
}; 