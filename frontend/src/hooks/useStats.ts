import { useState } from "react";
import { api } from "../services/api";
import { config } from "../config";

interface PriceTrend {
  date: string;
  avg_price: number;
  count: number;
}

interface LeadQualityMetric {
  name: string;
  value: number;
}

interface LeadQuality {
  total_leads: number;
  source_distribution: Array<{ name: string; value: number }>;
  conversion_rates: Array<{ name: string; value: number }>;
}

export function useStats() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getPriceTrends = async (
    startDate?: string,
    endDate?: string,
    location?: string,
    propertyType?: string,
  ) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get(
        `${config.apiUrl}/v1/stats/price-trends/`,
        {
          params: {
            start_date: startDate,
            end_date: endDate,
            location,
            property_type: propertyType,
          },
        },
      );
      return response.data as PriceTrend[];
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch price trends";
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const getLeadQuality = async (startDate?: string, endDate?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get(
        `${config.apiUrl}/v1/stats/lead-quality/`,
        {
          params: {
            start_date: startDate,
            end_date: endDate,
          },
        },
      );
      return response.data as LeadQuality;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch lead quality";
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    getPriceTrends,
    getLeadQuality,
    isLoading,
    error,
  };
}
