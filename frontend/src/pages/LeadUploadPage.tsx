import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Input,
  Spinner,
} from '@material-tailwind/react';
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";

interface UploadResponse {
  success_count: number;
  error_count: number;
  errors?: string[];
}

const defaultEventHandlers = {
  onResize: undefined,
  onResizeCapture: undefined,
  onPointerEnterCapture: undefined,
  onPointerLeaveCapture: undefined
};

export const LeadUploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [response, setResponse] = useState<UploadResponse | null>(null);
  const [error, setError] = useState("");
  const { token } = useAuth();
  const { getButtonProps, getCardProps, getCardBodyProps, getCardHeaderProps, getTypographyProps, getInputProps } = useMaterialTailwind();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== "text/csv") {
        setError("Please select a CSV file");
        return;
      }
      setFile(selectedFile);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError("");
    setResponse(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const result = await api.post<UploadResponse>('/leads/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });
      setResponse(result.data);
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Typography variant="h4" color="blue-gray" {...getTypographyProps()}>
          Upload Leads
        </Typography>
      </div>

      {/* Upload Card */}
      <Card {...getCardProps()}>
        <CardHeader
          variant="gradient"
          color="blue"
          className="mb-4 p-6"
          {...getCardHeaderProps()}
        >
          <Typography variant="h6" color="white" {...getTypographyProps()}>
            Upload CSV File
          </Typography>
        </CardHeader>
        <CardBody {...getCardBodyProps()}>
          <div className="space-y-6">
            <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-blue-gray-200 rounded-lg">
              <ArrowUpTrayIcon className="h-12 w-12 text-blue-gray-400 mb-4" />
              <Typography
                variant="h6"
                color="blue-gray"
                className="mb-2"
                {...getTypographyProps()}
              >
                Drag and drop your CSV file here
              </Typography>
              <Typography
                variant="small"
                color="blue-gray"
                className="mb-4"
                {...getTypographyProps()}
              >
                or click to browse
              </Typography>
              <Input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                {...getInputProps()}
              />
              <label htmlFor="file-upload">
                <Button
                  variant="filled"
                  color="blue"
                  className="cursor-pointer"
                  {...getButtonProps()}
                >
                  Select File
                </Button>
              </label>
            </div>

            {error && (
              <Typography
                variant="small"
                color="red"
                className="font-medium"
                {...getTypographyProps()}
              >
                {error}
              </Typography>
            )}

            {file && (
              <div className="flex items-center justify-between p-4 bg-blue-gray-50 rounded-lg">
                <Typography
                  variant="small"
                  color="blue-gray"
                  {...getTypographyProps()}
                >
                  Selected file: {file.name}
                </Typography>
                <Button
                  variant="filled"
                  color="blue"
                  onClick={handleUpload}
                  disabled={uploading}
                  {...getButtonProps()}
                >
                  {uploading ? (
                    <div className="flex items-center">
                      <Spinner className="h-4 w-4 mr-2" {...defaultEventHandlers} />
                      Uploading...
                    </div>
                  ) : (
                    "Upload"
                  )}
                </Button>
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {response && (
        <div className="mt-6 space-y-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <Typography variant="small" className="font-medium text-green-800" {...getTypographyProps()}>
              Upload Complete: {response.success_count} leads imported successfully
            </Typography>
          </div>
          
          {response.error_count > 0 && (
            <>
              <div className="bg-amber-50 p-4 rounded-lg">
                <Typography variant="small" className="font-medium text-amber-800" {...getTypographyProps()}>
                  {response.error_count} errors occurred during import
                </Typography>
              </div>
              {response.errors && response.errors.length > 0 && (
                <div className="bg-red-50 p-4 rounded-lg">
                  <Typography variant="small" className="font-medium text-red-800" {...getTypographyProps()}>
                    Error Details:
                  </Typography>
                  <ul className="mt-2 list-disc list-inside">
                    {response.errors.map((error, index) => (
                      <li key={index} className="text-red-700">
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default LeadUploadPage; 