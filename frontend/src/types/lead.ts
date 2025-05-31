export enum LeadStatus {
    NEW = "new",
    CONTACTED = "contacted",
    QUALIFIED = "qualified",
    CONVERTED = "converted",
    LOST = "lost"
}

export enum LeadSource {
    WEBSITE = "website",
    REFERRAL = "referral",
    SOCIAL_MEDIA = "social_media",
    DIRECT = "direct"
}

export interface Lead {
    id: number;
    name: string;
    email: string;
    phone: string;
    status: LeadStatus;
    source: LeadSource;
    notes: string;
    assigned_to?: number;
    created_at: string;
    updated_at: string;
}

export interface LeadCreate {
    name: string;
    email: string;
    phone: string;
    status: LeadStatus;
    source: LeadSource;
    notes?: string;
    assigned_to?: number;
}

export interface LeadUpdate {
    name?: string;
    email?: string;
    phone?: string;
    status?: LeadStatus;
    source?: LeadSource;
    notes?: string;
    assigned_to?: number;
}

export interface LeadFilter {
    status?: LeadStatus;
    source?: LeadSource;
    search?: string;
    date_range?: [string, string];
}

export interface LeadStats {
    total_leads: number;
    new_leads: number;
    contacted_leads: number;
    qualified_leads: number;
    converted_leads: number;
    conversion_rate: number;
}

export interface LeadTrend {
    date: string;
    count: number;
}

export interface SourceDistribution {
    source: string;
    count: number;
}

export interface LeadAnalytics {
    lead_trends: LeadTrend[];
    source_distribution: SourceDistribution[];
} 