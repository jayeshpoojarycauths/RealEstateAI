import { User } from './auth';

export interface AuditLog {
  id: string;
  timestamp: string;
  user: User;
  action: string;
  resourceType: string;
  resourceId: string;
  details: string;
  ipAddress: string;
  userAgent: string;
}

export interface AuditLogFilters {
  search?: string;
  action?: string;
  resourceType?: string;
  resourceId?: string;
  userId?: string;
  page?: number;
  limit?: number;
  startDate?: string;
  endDate?: string;
  sortBy?: 'timestamp' | 'action' | 'resourceType';
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
} 