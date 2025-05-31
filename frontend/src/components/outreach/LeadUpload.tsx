import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Alert,
} from "@material-tailwind/react";
import { ArrowUpTrayIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useOutreach } from '@/hooks/useOutreach';
import { useMaterialTailwind } from "@/hooks/useMaterialTailwind";

interface Lead {
  name: string;
  email?: string;
  phone?: string;
  source: string;
  notes?: string;
}

export function LeadUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [channel, setChannel] = useState<'email' | 'sms'>('email');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const { uploadLeads, sendOutreach } = useOutreach();
  const { getButtonProps, getCardProps, getCardHeaderProps, getCardBodyProps, getTypographyProps } = useMaterialTailwind();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Validate file type
    if (!selectedFile.name.match(/\.(csv|xlsx)$/)) {
      setError('Please select a CSV or Excel file');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setSuccess(null);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await uploadLeads(formData);
      setLeads(response);
      setSuccess('File uploaded successfully. Preview the leads below.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
      setLeads([]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendOutreach = async () => {
    if (!leads.length) return;

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      await sendOutreach({
        channel,
        leads,
      });
      setSuccess('Outreach messages sent successfully');
      // Reset form after successful send
      setFile(null);
      setLeads([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send outreach');
    } finally {
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setLeads([]);
    setError(null);
    setSuccess(null);
  };

  return (
    <Card className="w-full" {...getCardProps()}>
      <CardHeader
        variant="gradient"
        color="blue"
        className="mb-4 grid h-28 place-items-center"
        {...getCardHeaderProps()}
      >
        <Typography variant="h3" color="white" className="text-center" {...getTypographyProps()}>
          Lead Upload & Outreach
        </Typography>
      </CardHeader>
      <CardBody className="flex flex-col gap-4" {...getCardBodyProps()}>
        <div className="flex flex-col gap-6">
          {/* File Upload Section */}
          <div className="flex flex-col gap-2">
            <Typography variant="h6" className="font-medium" {...getTypographyProps()}>
              Upload CSV/Excel File
            </Typography>
            <div className="flex items-center gap-4">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="flex items-center gap-2 cursor-pointer"
              >
                <Button
                  variant="outlined"
                  className="flex items-center gap-2"
                  disabled={isUploading}
                  {...getButtonProps()}
                >
                  <ArrowUpTrayIcon className="h-5 w-5" />
                  {isUploading ? 'Uploading...' : 'Choose File'}
                </Button>
                {file && (
                  <div className="flex items-center gap-2">
                    <Typography className="text-sm" {...getTypographyProps()}>{file.name}</Typography>
                    <Button
                      variant="text"
                      color="red"
                      onClick={clearFile}
                      {...getButtonProps()}
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </Button>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Alerts */}
          {error && (
            <Alert color="red" className="mt-2" {...getTypographyProps()}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert color="green" className="mt-2" {...getTypographyProps()}>
              {success}
            </Alert>
          )}

          {/* Preview and Outreach Section */}
          {leads.length > 0 && (
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <Typography variant="h6" className="font-medium" {...getTypographyProps()}>
                  Outreach Channel
                </Typography>
                <div className="w-full">
                  <select
                    value={channel}
                    onChange={(e) => setChannel(e.target.value as 'email' | 'sms')}
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="email">Email</option>
                    <option value="sms">SMS</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <Typography variant="h6" className="font-medium" {...getTypographyProps()}>
                  Preview ({leads.length} leads)
                </Typography>
                <div className="max-h-60 overflow-y-auto">
                  <table className="w-full">
                    <thead>
                      <tr>
                        <th className="text-left p-2">Name</th>
                        <th className="text-left p-2">Email</th>
                        <th className="text-left p-2">Phone</th>
                        <th className="text-left p-2">Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {leads.map((lead, index) => (
                        <tr key={index} className="border-t">
                          <td className="p-2">{lead.name}</td>
                          <td className="p-2">{lead.email || '-'}</td>
                          <td className="p-2">{lead.phone || '-'}</td>
                          <td className="p-2">{lead.source}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <Button
                color="blue"
                onClick={handleSendOutreach}
                disabled={isUploading}
                className="mt-4"
                {...getButtonProps()}
              >
                {isUploading ? 'Sending...' : 'Send Outreach'}
              </Button>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
} 