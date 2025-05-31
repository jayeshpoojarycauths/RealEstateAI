export enum ProjectType {
    RESIDENTIAL = "residential",
    COMMERCIAL = "commercial",
    LAND = "land",
    RENTAL = "rental"
}

export enum ProjectStatus {
    PLANNING = "planning",
    IN_PROGRESS = "in_progress",
    COMPLETED = "completed",
    ON_HOLD = "on_hold",
    CANCELLED = "cancelled"
}

export interface Project {
    id: number;
    name: string;
    description: string;
    type: ProjectType;
    status: ProjectStatus;
    location: string;
    total_units: number;
    price_range: string;
    amenities: string[];
    completion_date?: string;
    customer_id: number;
    created_at: string;
    updated_at: string;
}

export interface ProjectCreate {
    name: string;
    description?: string;
    type: ProjectType;
    status: ProjectStatus;
    location: string;
    total_units?: number;
    price_range?: string;
    amenities?: string[];
    completion_date?: string;
}

export interface ProjectUpdate {
    name?: string;
    description?: string;
    type?: ProjectType;
    status?: ProjectStatus;
    location?: string;
    total_units?: number;
    price_range?: string;
    amenities?: string[];
    completion_date?: string;
}

export interface ProjectStats {
    total_leads: number;
    active_leads: number;
    converted_leads: number;
    conversion_rate: number;
}

export interface LeadTrend {
    date: string;
    count: number;
}

export interface StatusDistribution {
    status: string;
    count: number;
}

export interface ProjectAnalytics {
    lead_trends: LeadTrend[];
    status_distribution: StatusDistribution[];
} 