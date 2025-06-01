import React, { useState, useRef } from "react";
import {
  SafeCard as Card,
  SafeCardHeader as CardHeader,
  SafeCardBody as CardBody,
  SafeButton as Button,
  SafeTypography as Typography,
  SafeAlert as Alert,
  SafeInput as Input,
  SafeSelect as Select,
  SafeOption as Option,
} from "../components/SafeMTW";
import {
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";
import api from "../services/api";
import * as RadixSelect from "@radix-ui/react-select";
import { CheckIcon, ChevronDownIcon } from "@heroicons/react/24/outline";

// Custom dropdown component using Radix UI
const CustomDropdown: React.FC<{
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  label: string;
}> = ({ value, onChange, options, label }) => (
  <div>
    <label className="block text-blue-gray-700 font-medium mb-2">{label}</label>
    <RadixSelect.Root value={value} onValueChange={onChange}>
      <RadixSelect.Trigger className="w-full px-4 py-3 border border-blue-gray-200 rounded-lg bg-white text-blue-gray-700 flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
        <RadixSelect.Value />
        <RadixSelect.Icon>
          <ChevronDownIcon className="h-5 w-5 text-blue-gray-400" />
        </RadixSelect.Icon>
      </RadixSelect.Trigger>
      <RadixSelect.Portal>
        <RadixSelect.Content className="z-50 bg-white border border-blue-gray-200 rounded-lg shadow-lg">
          <RadixSelect.Viewport className="p-2">
            {options.map((opt) => (
              <RadixSelect.Item
                key={opt.value}
                value={opt.value}
                className="flex items-center px-4 py-2 rounded-md cursor-pointer text-blue-gray-700 hover:bg-blue-100 focus:bg-blue-200 focus:outline-none"
              >
                <RadixSelect.ItemText>{opt.label}</RadixSelect.ItemText>
                <RadixSelect.ItemIndicator className="ml-auto">
                  <CheckIcon className="h-4 w-4 text-blue-500" />
                </RadixSelect.ItemIndicator>
              </RadixSelect.Item>
            ))}
          </RadixSelect.Viewport>
        </RadixSelect.Content>
      </RadixSelect.Portal>
    </RadixSelect.Root>
  </div>
);

export const LeadsImportExportPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [exportFilters, setExportFilters] = useState({
    status: "all",
    dateRange: "all",
  });
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.name.match(/\.(csv|xlsx)$/)) {
        setUploadError("Please select a CSV or Excel file");
        return;
      }
      setFile(selectedFile);
      setUploadError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setUploadError("");
    setUploadSuccess("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const result = await api.post("/leads/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadSuccess("Leads imported successfully!");
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (e: any) {
      setUploadError(e?.response?.data?.detail || "Failed to import leads");
    } finally {
      setUploading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    setExportError("");
    try {
      const response = await api.get("/leads/export", {
        params: exportFilters,
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "leads_export.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e: any) {
      setExportError(e?.response?.data?.detail || "Failed to export leads");
    } finally {
      setExporting(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get("/leads/template", {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "lead_upload_template.xlsx");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error: unknown) {
      console.error("Error downloading template:", error);
    }
  };

  return (
    <div className="space-y-6">
      <Typography variant="h4" color="blue-gray">
        Import/Export Leads
      </Typography>

      {/* Import Section */}
      <Card>
        <CardHeader>
          <Typography variant="h6" color="white">
            Import Leads
          </Typography>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Button
                variant="filled"
                color="blue"
                onClick={() => fileInputRef.current?.click()}
                type="button"
              >
                <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
                Select File
              </Button>
              <input
                type="file"
                accept=".csv,.xlsx"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
              <Button
                variant="text"
                color="blue"
                onClick={handleDownloadTemplate}
                type="button"
              >
                Download Template
              </Button>
            </div>

            {file && (
              <div className="p-4 bg-blue-gray-50 rounded-lg">
                <Typography variant="small" color="blue-gray">
                  Selected file: {file.name}
                </Typography>
                <div className="flex gap-2 mt-2">
                  <Button
                    color="blue"
                    onClick={handleUpload}
                    disabled={uploading}
                    type="button"
                  >
                    {uploading ? "Uploading..." : "Upload"}
                  </Button>
                  <Button
                    color="red"
                    variant="text"
                    onClick={() => setFile(null)}
                    type="button"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {uploadError && (
              <Alert color="red" className="mt-2">
                {uploadError}
              </Alert>
            )}
            {uploadSuccess && (
              <Alert color="green" className="mt-2">
                {uploadSuccess}
              </Alert>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Export Section */}
      <Card>
        <CardHeader>
          <Typography variant="h6" color="white">
            Export Leads
          </Typography>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <CustomDropdown
                label="Filter by Status"
                value={exportFilters.status}
                onChange={(value) =>
                  setExportFilters((prev) => ({ ...prev, status: value }))
                }
                options={[
                  { value: "all", label: "All Statuses" },
                  { value: "new", label: "New" },
                  { value: "contacted", label: "Contacted" },
                  { value: "qualified", label: "Qualified" },
                  { value: "lost", label: "Lost" },
                ]}
              />
              <CustomDropdown
                label="Date Range"
                value={exportFilters.dateRange}
                onChange={(value) =>
                  setExportFilters((prev) => ({ ...prev, dateRange: value }))
                }
                options={[
                  { value: "all", label: "All Time" },
                  { value: "today", label: "Today" },
                  { value: "week", label: "This Week" },
                  { value: "month", label: "This Month" },
                  { value: "year", label: "This Year" },
                ]}
              />
            </div>

            <Button
              variant="filled"
              color="blue"
              onClick={handleExport}
              disabled={exporting}
              type="button"
            >
              <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
              {exporting ? "Exporting..." : "Export Leads"}
            </Button>

            {exportError && (
              <Alert color="red" className="mt-2">
                {exportError}
              </Alert>
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default LeadsImportExportPage;
