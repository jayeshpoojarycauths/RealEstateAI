import React, { useState } from 'react';
import {
    Card,
    CardHeader,
    CardBody,
    Typography,
    Input,
    Select,
    Option,
    Button,
} from '@material-tailwind/react';
import { useQuery } from '@tanstack/react-query';
import { logger } from '../../../utils/logger';
import { auditLogService, AuditLog } from '../../../services/auditLogService';

export const AuditLogs: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [actionFilter, setActionFilter] = useState<string>('all');
    const [resourceFilter, setResourceFilter] = useState<string>('all');
    const [page, setPage] = useState(1);
    const limit = 10;

    const { data, isLoading } = useQuery({
        queryKey: ['auditLogs', { search: searchTerm, action: actionFilter, resource: resourceFilter, page, limit }],
        queryFn: () => auditLogService.getAll({
            search: searchTerm,
            action: actionFilter !== 'all' ? actionFilter : undefined,
            resource: resourceFilter !== 'all' ? resourceFilter : undefined,
            page,
            limit,
        }),
    });

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString();
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    const { items: auditLogs = [], total, totalPages } = data || {};

    return (
        <div className="p-4">
            <Card>
                <CardHeader
                    variant="gradient"
                    color="blue"
                    className="mb-4 grid h-28 place-items-center"
                >
                    <Typography variant="h3" color="white">
                        Audit Logs
                    </Typography>
                </CardHeader>
                <CardBody className="overflow-x-auto px-0 pt-0 pb-2">
                    {/* Filters */}
                    <div className="flex flex-wrap gap-4 mb-4 p-4">
                        <Input
                            label="Search"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-64"
                        />
                        <Select
                            label="Action"
                            value={actionFilter}
                            onChange={(value) => setActionFilter(value as string)}
                            className="w-48"
                        >
                            <Option value="all">All</Option>
                            <Option value="create">Create</Option>
                            <Option value="update">Update</Option>
                            <Option value="delete">Delete</Option>
                            <Option value="login">Login</Option>
                            <Option value="logout">Logout</Option>
                        </Select>
                        <Select
                            label="Resource"
                            value={resourceFilter}
                            onChange={(value) => setResourceFilter(value as string)}
                            className="w-48"
                        >
                            <Option value="all">All</Option>
                            <Option value="user">User</Option>
                            <Option value="property">Property</Option>
                            <Option value="customer">Customer</Option>
                            <Option value="system">System</Option>
                        </Select>
                    </div>

                    {/* Audit Logs Table */}
                    <table className="w-full min-w-[640px] table-auto">
                        <thead>
                            <tr>
                                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                    <Typography
                                        variant="small"
                                        className="text-[11px] font-medium uppercase text-blue-gray-400"
                                    >
                                        Timestamp
                                    </Typography>
                                </th>
                                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                    <Typography
                                        variant="small"
                                        className="text-[11px] font-medium uppercase text-blue-gray-400"
                                    >
                                        User
                                    </Typography>
                                </th>
                                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                    <Typography
                                        variant="small"
                                        className="text-[11px] font-medium uppercase text-blue-gray-400"
                                    >
                                        Action
                                    </Typography>
                                </th>
                                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                    <Typography
                                        variant="small"
                                        className="text-[11px] font-medium uppercase text-blue-gray-400"
                                    >
                                        Resource
                                    </Typography>
                                </th>
                                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                    <Typography
                                        variant="small"
                                        className="text-[11px] font-medium uppercase text-blue-gray-400"
                                    >
                                        Details
                                    </Typography>
                                </th>
                                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                    <Typography
                                        variant="small"
                                        className="text-[11px] font-medium uppercase text-blue-gray-400"
                                    >
                                        IP Address
                                    </Typography>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {auditLogs.map((log) => (
                                <tr key={log.id}>
                                    <td className="py-3 px-6 border-b border-blue-gray-50">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {formatDate(log.timestamp)}
                                        </Typography>
                                    </td>
                                    <td className="py-3 px-6 border-b border-blue-gray-50">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {log.user.email}
                                            <br />
                                            <span className="text-xs text-blue-gray-400">
                                                {log.user.role}
                                            </span>
                                        </Typography>
                                    </td>
                                    <td className="py-3 px-6 border-b border-blue-gray-50">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {log.action.charAt(0).toUpperCase() + log.action.slice(1)}
                                        </Typography>
                                    </td>
                                    <td className="py-3 px-6 border-b border-blue-gray-50">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {log.resource.charAt(0).toUpperCase() + log.resource.slice(1)}
                                        </Typography>
                                    </td>
                                    <td className="py-3 px-6 border-b border-blue-gray-50">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {log.details}
                                        </Typography>
                                    </td>
                                    <td className="py-3 px-6 border-b border-blue-gray-50">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {log.ipAddress}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {/* Pagination */}
                    <div className="flex items-center justify-between p-4">
                        <Typography variant="small" color="blue-gray">
                            Showing {auditLogs.length} of {total} entries
                        </Typography>
                        <div className="flex gap-2">
                            <Button
                                size="sm"
                                variant="outlined"
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >
                                Previous
                            </Button>
                            <Button
                                size="sm"
                                variant="outlined"
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                            >
                                Next
                            </Button>
                        </div>
                    </div>
                </CardBody>
            </Card>
        </div>
    );
}; 