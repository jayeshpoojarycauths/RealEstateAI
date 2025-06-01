import { apiClient } from './apiClient';
import { API_CONFIG } from '../config/api';
import { AuditLog, AuditLogFilters, PaginatedResponse } from '../types/auditLog';

export const auditLogService = {
    async getAll(filters?: AuditLogFilters): Promise<PaginatedResponse<AuditLog>> {
        return apiClient.get<PaginatedResponse<AuditLog>>(API_CONFIG.endpoints.auditLogs.list, {
            params: filters,
        });
    },

    async getById(id: string): Promise<AuditLog> {
        return apiClient.get<AuditLog>(`${API_CONFIG.endpoints.auditLogs.detail}/${id}`);
    },

    async getByUser(userId: string, filters?: Omit<AuditLogFilters, 'userId'>): Promise<PaginatedResponse<AuditLog>> {
        return apiClient.get<PaginatedResponse<AuditLog>>(`${API_CONFIG.endpoints.auditLogs.byUser}/${userId}`, {
            params: filters,
        });
    },

    async getByResource(resourceType: string, resourceId: string, filters?: Omit<AuditLogFilters, 'resourceType' | 'resourceId'>): Promise<PaginatedResponse<AuditLog>> {
        return apiClient.get<PaginatedResponse<AuditLog>>(`${API_CONFIG.endpoints.auditLogs.byResource}/${resourceType}/${resourceId}`, {
            params: filters,
        });
    },

    async export(filters?: AuditLogFilters): Promise<Blob> {
        const response = await apiClient.get<Blob>(API_CONFIG.endpoints.auditLogs.export, {
            params: filters,
            responseType: 'blob',
        });
        return response;
    },
}; 