export interface ConversionFunnelStage {
  stage: string;
  count: number;
  percentage: number;
}

export interface ConversionFunnelResponse {
  total_leads: number;
  stages: ConversionFunnelStage[];
}

export interface LeadQualityMetric {
  name: string;
  value: number;
}

export interface LeadQualityResponse {
  total_leads: number;
  source_distribution: LeadQualityMetric[];
  conversion_rates: LeadQualityMetric[];
}
