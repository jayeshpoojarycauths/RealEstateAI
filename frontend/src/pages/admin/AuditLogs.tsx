import React, { useState } from "react";
import {
  SafeCard,
  SafeCardHeader,
  SafeCardBody,
  SafeTypography,
  SafeInput,
  SafeSelect,
  SafeOption,
  SafeButton,
} from "../../components/SafeMTW";
import { useQuery } from "@tanstack/react-query";
import { auditLogService } from "src/services/auditLogService";
import { AuditLog } from "src/types/auditLog";

export const AuditLogs: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [resourceFilter, setResourceFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading, error } = useQuery({
    queryKey: [
      "auditLogs",
      {
        search: searchTerm,
        action: actionFilter,
        resourceType: resourceFilter,
        page,
        limit,
      },
    ],
    queryFn: () =>
      auditLogService.getAll({
        search: searchTerm,
        action: actionFilter !== "all" ? actionFilter : undefined,
        resourceType: resourceFilter !== "all" ? resourceFilter : undefined,
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

  if (error) {
    return <div>Error loading audit logs: {(error as Error).message}</div>;
  }

  const { items: auditLogs = [], total, totalPages } = data || {};

  return (
    <div className="p-4">
      <SafeCard>
        <SafeCardHeader color="blue" className="mb-4 grid h-28 place-items-center">
          <SafeTypography variant="h3" color="white">
            Audit Logs
          </SafeTypography>
        </SafeCardHeader>
        <SafeCardBody className="overflow-x-auto px-0 pt-0 pb-2">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-4 p-4">
            <SafeInput
              label="Search"
              value={searchTerm}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
              className="w-64"
            />
            <SafeSelect
              value={actionFilter}
              onChange={(value: string | undefined) => setActionFilter(value as string)}
              className="w-48"
              label="Action"
            >
              <SafeOption value="all">All</SafeOption>
              <SafeOption value="create">Create</SafeOption>
              <SafeOption value="update">Update</SafeOption>
              <SafeOption value="delete">Delete</SafeOption>
              <SafeOption value="login">Login</SafeOption>
              <SafeOption value="logout">Logout</SafeOption>
            </SafeSelect>
            <SafeSelect
              value={resourceFilter}
              onChange={(value: string | undefined) => setResourceFilter(value as string)}
              className="w-48"
              label="Resource"
            >
              <SafeOption value="all">All</SafeOption>
              <SafeOption value="user">User</SafeOption>
              <SafeOption value="property">Property</SafeOption>
              <SafeOption value="customer">Customer</SafeOption>
              <SafeOption value="system">System</SafeOption>
            </SafeSelect>
          </div>

          {/* Audit Logs Table */}
          <table className="w-full min-w-[640px] table-auto">
            <thead>
              <tr>
                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                  <SafeTypography
                    variant="small"
                    className="text-[11px] font-medium uppercase text-blue-gray-400"
                  >
                    Timestamp
                  </SafeTypography>
                </th>
                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                  <SafeTypography
                    variant="small"
                    className="text-[11px] font-medium uppercase text-blue-gray-400"
                  >
                    User
                  </SafeTypography>
                </th>
                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                  <SafeTypography
                    variant="small"
                    className="text-[11px] font-medium uppercase text-blue-gray-400"
                  >
                    Action
                  </SafeTypography>
                </th>
                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                  <SafeTypography
                    variant="small"
                    className="text-[11px] font-medium uppercase text-blue-gray-400"
                  >
                    Resource
                  </SafeTypography>
                </th>
                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                  <SafeTypography
                    variant="small"
                    className="text-[11px] font-medium uppercase text-blue-gray-400"
                  >
                    Details
                  </SafeTypography>
                </th>
                <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                  <SafeTypography
                    variant="small"
                    className="text-[11px] font-medium uppercase text-blue-gray-400"
                  >
                    IP Address
                  </SafeTypography>
                </th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log: AuditLog) => (
                <tr key={log.id}>
                  <td className="py-3 px-6 border-b border-blue-gray-50">
                    <SafeTypography
                      variant="small"
                      color="blue-gray"
                      className="font-normal"
                    >
                      {formatDate(log.timestamp)}
                    </SafeTypography>
                  </td>
                  <td className="py-3 px-6 border-b border-blue-gray-50">
                    <SafeTypography
                      variant="small"
                      color="blue-gray"
                      className="font-normal"
                    >
                      {log.user.email}
                      <br />
                      <span className="text-xs text-blue-gray-400">
                        {log.user.role}
                      </span>
                    </SafeTypography>
                  </td>
                  <td className="py-3 px-6 border-b border-blue-gray-50">
                    <SafeTypography
                      variant="small"
                      color="blue-gray"
                      className="font-normal"
                    >
                      {log.action.charAt(0).toUpperCase() + log.action.slice(1)}
                    </SafeTypography>
                  </td>
                  <td className="py-3 px-6 border-b border-blue-gray-50">
                    <SafeTypography
                      variant="small"
                      color="blue-gray"
                      className="font-normal"
                    >
                      {log.resourceType.charAt(0).toUpperCase() + log.resourceType.slice(1)}
                    </SafeTypography>
                  </td>
                  <td className="py-3 px-6 border-b border-blue-gray-50">
                    <SafeTypography
                      variant="small"
                      color="blue-gray"
                      className="font-normal"
                    >
                      {log.details}
                    </SafeTypography>
                  </td>
                  <td className="py-3 px-6 border-b border-blue-gray-50">
                    <SafeTypography
                      variant="small"
                      color="blue-gray"
                      className="font-normal"
                    >
                      {log.ipAddress}
                    </SafeTypography>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* Pagination */}
          <div className="flex justify-between items-center mt-4">
            <SafeButton
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              variant="outlined"
            >
              Previous
            </SafeButton>
            <SafeTypography variant="small" className="mx-2">
              Page {page} of {totalPages || 1}
            </SafeTypography>
            <SafeButton
              onClick={() => setPage((p) => (totalPages && p < totalPages ? p + 1 : p))}
              disabled={!totalPages || page === totalPages}
              variant="outlined"
            >
              Next
            </SafeButton>
          </div>
        </SafeCardBody>
      </SafeCard>
    </div>
  );
};
