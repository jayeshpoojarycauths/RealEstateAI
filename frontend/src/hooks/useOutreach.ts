import { useState } from "react";
import axios from "axios";
import api from "../services/api";
import config from "../config";

interface Lead {
  name: string;
  email?: string;
  phone?: string;
  source: string;
  notes?: string;
}

interface OutreachParams {
  channel: "email" | "sms";
  leads: Lead[];
}

export function useOutreach() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<any[]>([]);

  const uploadLeads = async (formData: FormData): Promise<Lead[]> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await axios.post("/api/v1/leads/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to upload leads";
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const sendOutreach = async (params: OutreachParams): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      await axios.post("/api/v1/outreach/send", params);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to send outreach";
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchOutreachLogs = async () => {
    try {
      setIsLoading(true);
      const response = await api.get(`${config.apiUrl}/v1/outreach/logs/`);
      setLogs(response.data);
    } catch (error) {
      console.error("Error fetching outreach logs:", error);
      setError("Failed to load outreach logs");
    } finally {
      setIsLoading(false);
    }
  };

  return {
    uploadLeads,
    sendOutreach,
    fetchOutreachLogs,
    logs,
    isLoading,
    error,
  };
}
