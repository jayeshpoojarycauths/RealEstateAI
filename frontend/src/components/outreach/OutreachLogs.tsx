import React, { useEffect, useState } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Spinner,
} from "@material-tailwind/react";
import { useOutreach } from "../../hooks/useOutreach";

interface OutreachLog {
  id: number;
  lead_id: number;
  channel: "email" | "sms";
  status: "pending" | "sent" | "failed";
  message: string;
  sent_at: string | null;
  created_at: string;
}

export function OutreachLogs() {
  const [logs, setLogs] = useState<OutreachLog[]>([]);
  const { getOutreachLogs, isLoading, error } = useOutreach();

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getOutreachLogs();
        setLogs(data);
      } catch (err) {
        console.error("Failed to fetch outreach logs:", err);
      }
    };

    fetchLogs();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "sent":
        return "text-green-500";
      case "failed":
        return "text-red-500";
      default:
        return "text-yellow-500";
    }
  };

  return (
    <Card className="w-full">
      <CardHeader
        variant="gradient"
        color="blue"
        className="mb-4 grid h-28 place-items-center"
      >
        <Typography variant="h3" color="white">
          Outreach History
        </Typography>
      </CardHeader>
      <CardBody>
        {isLoading ? (
          <div className="flex justify-center">
            <Spinner className="h-8 w-8" />
          </div>
        ) : error ? (
          <Typography color="red">{error}</Typography>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th>Lead ID</th>
                  <th>Channel</th>
                  <th>Status</th>
                  <th>Message</th>
                  <th>Sent At</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td>{log.lead_id}</td>
                    <td className="capitalize">{log.channel}</td>
                    <td className={getStatusColor(log.status)}>{log.status}</td>
                    <td className="max-w-xs truncate">{log.message}</td>
                    <td>
                      {log.sent_at
                        ? new Date(log.sent_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>{new Date(log.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
