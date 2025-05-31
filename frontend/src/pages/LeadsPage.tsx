import React, { useState, useEffect, useRef } from "react";
import {
  SafeSpinner as Spinner,
  SafeTypography as Typography,
  SafeButton as Button,
  SafeCard as Card,
  SafeCardHeader as CardHeader,
  SafeCardBody as CardBody,
  SafeDialog as Dialog,
  SafeDialogHeader as DialogHeader,
  SafeDialogBody as DialogBody,
  SafeDialogFooter as DialogFooter,
  SafeInput as Input,
  SafeSelect as Select,
  SafeOption as Option,
  SafeAlert as Alert,
} from "../components/SafeMTW";
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowUpTrayIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { useNavigate } from "react-router-dom";
import api from '../services/api';
import { useForm, Controller } from "react-hook-form";
import { FaSms, FaPhone, FaWhatsapp, FaTelegramPlane, FaEdit, FaSave } from 'react-icons/fa';

interface Lead {
  id: number;
  name: string;
  email: string;
  phone: string;
  status: string;
  created_at: string;
}

type SortField = "name" | "email" | "status" | "created_at";
type SortDirection = "asc" | "desc";

export const LeadsPage: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<SortField>("created_at");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const itemsPerPage = 10;
  const navigate = useNavigate();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadResponse, setUploadResponse] = useState(null);
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [addLeadOpen, setAddLeadOpen] = useState(false);
  const [addLeadLoading, setAddLeadLoading] = useState(false);
  const [addLeadError, setAddLeadError] = useState("");
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [leadToDelete, setLeadToDelete] = useState<Lead | null>(null);
  const [editingRowId, setEditingRowId] = useState<number | null>(null);
  const [rowEdits, setRowEdits] = useState<Partial<Lead>>({});

  const { register, handleSubmit, reset, setValue, formState: { errors }, control } = useForm({
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      status: "new",
      notes: "",
    },
  });

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      console.log('Fetching leads...');
      console.log('Token:', token);
      console.log('API URL:', api.defaults.baseURL, '/leads/');
      const response = await api.get('/leads/');
      console.log('Leads API response:', response);
      setLeads(response.data);
      setError("");
    } catch (e: any) {
      console.error('Error fetching leads:', e);
      if (e.response) {
        console.error('Error response data:', e.response.data);
        console.error('Error response status:', e.response.status);
        console.error('Error response headers:', e.response.headers);
      }
      setError("Failed to fetch leads. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const filteredLeads = leads
    .filter((lead) => {
      const matchesSearch =
        lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.phone.includes(searchTerm);
      const matchesStatus = statusFilter === "all" || lead.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      const modifier = sortDirection === "asc" ? 1 : -1;
      return aValue > bValue ? modifier : -modifier;
    });

  const totalPages = Math.ceil(filteredLeads.length / itemsPerPage);
  const paginatedLeads = filteredLeads.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const statusOptions = [
    { value: "all", label: "All Statuses" },
    { value: "new", label: "New" },
    { value: "contacted", label: "Contacted" },
    { value: "qualified", label: "Qualified" },
    { value: "lost", label: "Lost" },
  ];

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
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
    setUploadResponse(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const result = await api.post('/leads/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setUploadResponse(result.data);
      setFile(null);
      fetchLeads();
    } catch (e: any) {
      setUploadError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setUploading(false);
    }
  };

  const handleCreate = () => {
    setEditingRowId(null);
    reset();
    setAddLeadError("");
    setAddLeadOpen(true);
  };

  const startEditRow = (lead: Lead) => {
    setEditingRowId(lead.id);
    setRowEdits({ ...lead });
  };

  const cancelEditRow = () => {
    setEditingRowId(null);
    setRowEdits({});
  };

  const handleRowEditChange = (field: keyof Lead, value: string) => {
    setRowEdits((prev) => ({ ...prev, [field]: value }));
  };

  const saveRowEdit = async (lead: Lead) => {
    try {
      await api.put(`/leads/edit/${lead.id}`, rowEdits);
      setSuccessMessage("Lead updated successfully!");
      setEditingRowId(null);
      setRowEdits({});
      fetchLeads();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to save lead');
    }
  };

  const handleDelete = (lead: Lead) => {
    setLeadToDelete(lead);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!leadToDelete) return;
    try {
      await api.delete(`/api/v1/leads/${leadToDelete.id}`);
      setSuccessMessage("Lead deleted successfully!");
      fetchLeads();
    } catch (err) {
      setSuccessMessage("Failed to delete lead");
    } finally {
      setDeleteDialogOpen(false);
      setLeadToDelete(null);
    }
  };

  const closeDialog = () => {
    setAddLeadOpen(false);
    setAddLeadError("");
    setEditingRowId(null);
    setRowEdits({});
    reset();
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/leads/template', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'lead_upload_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading template:', error);
    }
  };

  // Type guard for error object
  function isValidationError(error: unknown): error is { detail: { msg: string }[] } {
    return typeof error === 'object' && error !== null && Array.isArray((error as any).detail);
  }

  const handleSms = async (lead: Lead) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await api.post(`/communication/send/${lead.id}/`, {
        message: `Hello ${lead.name}, this is a test SMS from Real Estate AI!`,
        channel: 'sms',
      });
      setSuccessMessage(`SMS sent to ${lead.phone}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || `Failed to send SMS to ${lead.phone}`);
    }
  };

  const handleCall = async (lead: Lead) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await api.post(`/communication/send/${lead.id}/`, {
        message: `Hello ${lead.name}, this is a test call from Real Estate AI!`,
        channel: 'call',
      });
      setSuccessMessage(`Call to ${lead.phone} ended`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || `Failed to make call to ${lead.phone}`);
    }
  };

  const handleWhatsapp = async (lead: Lead) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await api.post(`/communication/send/${lead.id}/`, {
        message: `Hello ${lead.name}, this is a test WhatsApp message from Real Estate AI!`,
        channel: 'whatsapp',
      });
      setSuccessMessage(`WhatsApp sent to ${lead.phone}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || `Failed to send WhatsApp to ${lead.phone}`);
    }
  };

  const handleTelegram = async (lead: Lead) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await api.post(`/communication/send/${lead.id}/`, {
        message: `Hello ${lead.name}, this is a test Telegram message from Real Estate AI!`,
        channel: 'telegram',
      });
      setSuccessMessage(`Telegram sent to ${lead.phone}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || `Failed to send Telegram to ${lead.phone}`);
    }
  };

  const onAddLeadSubmit = async (data: any) => {
    setAddLeadLoading(true);
    setAddLeadError("");
    try {
      const payload = {
        ...data,
        name: `${data.first_name} ${data.last_name}`.trim(),
      };
      await api.post('/leads/new/', payload);
      setSuccessMessage("Lead added successfully!");
      setAddLeadOpen(false);
      reset();
      fetchLeads();
    } catch (err: any) {
      setAddLeadError(err?.response?.data?.detail || "Failed to save lead");
    } finally {
      setAddLeadLoading(false);
    }
  };

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Typography variant="h6" color="red">
          {typeof error === 'string'
            ? error
            : (typeof error === 'object' && error !== null && 'msg' in error)
              ? (error as any).msg
              : (typeof error === 'object' && error !== null && 'detail' in error)
                ? (error as any).detail
                : JSON.stringify(error)}
        </Typography>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {successMessage && (
        <div className="mb-4 text-green-600">{successMessage}</div>
      )}
      {error && (
        <div className="mb-4 text-red-600">{error}</div>
      )}
      <div className="flex items-center justify-between">
        <Typography variant="h4" color="blue-gray">
          Leads
        </Typography>
        <div className="flex items-center space-x-4">
          <Button
            variant="filled"
            color="blue"
            onClick={() => fileInputRef.current?.click()}
            type="button"
          >
            <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
            Upload Leads
          </Button>
          <input
            type="file"
            accept=".csv,.xlsx"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <Button
            variant="filled"
            color="blue"
            onClick={handleCreate}
            type="button"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Lead
          </Button>
          <Button onClick={handleDownloadTemplate}>Download Template</Button>
        </div>
      </div>

      {file && (
        <div className="mb-4 p-4 bg-blue-gray-50 rounded-lg flex flex-col gap-2">
          <Typography variant="small" color="blue-gray">Selected file: {file.name}</Typography>
          <div className="flex gap-2">
            <Button color="blue" onClick={handleUpload} disabled={uploading} type="button">{uploading ? "Uploading..." : "Upload"}</Button>
            <Button color="red" variant="text" onClick={() => setFile(null)} type="button">Cancel</Button>
          </div>
          {uploadError && <Typography variant="small" color="red">{uploadError}</Typography>}
          {uploadResponse && <Typography variant="small" color="green">Upload complete!</Typography>}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4">
        <div className="w-full md:w-72">
          <Input
            type="text"
            placeholder="Search leads..."
            value={searchTerm}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
            icon={<MagnifyingGlassIcon className="h-5 w-5" />}
          />
        </div>
        <div className="w-full md:w-72">
          <Select
            value={statusFilter}
            onChange={(value: any) => setStatusFilter(value as string)}
            label="Filter by Status"
          >
            {statusOptions.map((option) => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <Typography variant="h6" color="white">
            Lead List
          </Typography>
        </CardHeader>
        <CardBody>
        <div className="overflow-x-auto">
  <table className="w-full min-w-max table-auto text-left">
    <thead>
      <tr>
        <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer" onClick={() => handleSort("name")}>
          <div className="flex items-center">
            <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
              Name
            </Typography>
            {sortField === "name" && (sortDirection === "asc" ? <ChevronUpIcon className="h-4 w-4 ml-1" /> : <ChevronDownIcon className="h-4 w-4 ml-1" />)}
          </div>
        </th>
        <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer" onClick={() => handleSort("email")}>
          <div className="flex items-center">
            <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
              Email
            </Typography>
            {sortField === "email" && (sortDirection === "asc" ? <ChevronUpIcon className="h-4 w-4 ml-1" /> : <ChevronDownIcon className="h-4 w-4 ml-1" />)}
          </div>
        </th>
        <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
          <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
            Phone
          </Typography>
        </th>
        <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer" onClick={() => handleSort("status")}>
          <div className="flex items-center">
            <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
              Status
            </Typography>
            {sortField === "status" && (sortDirection === "asc" ? <ChevronUpIcon className="h-4 w-4 ml-1" /> : <ChevronDownIcon className="h-4 w-4 ml-1" />)}
          </div>
        </th>
        <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
          <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
            Communicate
          </Typography>
        </th>
        <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 text-center">
          <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
            Actions
          </Typography>
        </th>
      </tr>
    </thead>
    <tbody>
      {paginatedLeads.map((lead) => (
        <tr key={lead.id}>
          <td className="p-4">
            {editingRowId === lead.id ? (
              <Input
                value={rowEdits.name || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleRowEditChange('name', e.target.value)}
                className="w-full"
              />
            ) : (
              <Typography variant="small" color="blue-gray" className="font-normal">
                {lead.name}
              </Typography>
            )}
          </td>
          <td className="p-4">
            {editingRowId === lead.id ? (
              <Input
                value={rowEdits.email || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleRowEditChange('email', e.target.value)}
                className="w-full"
              />
            ) : (
              <Typography variant="small" color="blue-gray" className="font-normal">
                {lead.email}
              </Typography>
            )}
          </td>
          <td className="p-4">
            {editingRowId === lead.id ? (
              <Input
                value={rowEdits.phone || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleRowEditChange('phone', e.target.value)}
                className="w-full"
              />
            ) : (
              <Typography variant="small" color="blue-gray" className="font-normal">
                {lead.phone}
              </Typography>
            )}
          </td>
          <td className="p-4">
            {editingRowId === lead.id ? (
              <Select
                value={rowEdits.status || ''}
                onChange={(e: string | undefined) => handleRowEditChange('status', e || '')}
                className="w-full"
              >
                <Option value="new">New</Option>
                <Option value="contacted">Contacted</Option>
                <Option value="qualified">Qualified</Option>
                <Option value="lost">Lost</Option>
              </Select>
            ) : (
              <Typography variant="small" color="blue-gray" className="font-normal">
                {lead.status}
              </Typography>
            )}
          </td>
          <td className="p-4">
            <div className="grid grid-cols-4 gap-2">
              <button type="button" onClick={() => handleSms(lead)} title="Send SMS" className="p-1">
                <FaSms className="text-blue-500 hover:text-blue-700" />
              </button>
              <button type="button" onClick={() => handleCall(lead)} title="Call" className="p-1">
                <FaPhone className="text-green-500 hover:text-green-700" />
              </button>
              <button type="button" onClick={() => handleWhatsapp(lead)} title="WhatsApp" className="p-1">
                <FaWhatsapp className="text-green-600 hover:text-green-800" />
              </button>
              <button type="button" onClick={() => handleTelegram(lead)} title="Telegram" className="p-1">
                <FaTelegramPlane className="text-blue-400 hover:text-blue-600" />
              </button>
            </div>
          </td>
          <td className="p-4 text-center">
            <div className="grid grid-cols-2 gap-2 justify-center">
              {editingRowId === lead.id ? (
                <Button variant="text" color="green" size="sm" onClick={() => saveRowEdit(lead)} type="button">
                  <FaSave />
                </Button>
              ) : (
                <Button variant="text" color="blue" size="sm" onClick={() => startEditRow(lead)} type="button">
                  <FaEdit />
                </Button>
              )}
              <Button variant="text" color="red" size="sm" onClick={() => handleDelete(lead)} type="button">
                Delete
              </Button>
            </div>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</div>


          {totalPages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-blue-gray-50">
              <Typography
                variant="small"
                color="blue-gray"
                className="font-normal"
              >
                Page {currentPage} of {totalPages}
              </Typography>
              <div className="flex gap-2">
                <Button
                  variant="text"
                  color="blue"
                  size="sm"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(currentPage - 1)}
                  type="button"
                >
                  Previous
                </Button>
                <Button
                  variant="text"
                  color="blue"
                  size="sm"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(currentPage + 1)}
                  type="button"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      <Dialog open={addLeadOpen} handler={closeDialog} size="sm">
        <DialogHeader className="pb-3">
          <Typography variant="h5" color="blue-gray">
            Add Lead
          </Typography>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(onAddLeadSubmit)} autoComplete="off" className="w-full">
            <DialogBody className="flex flex-col gap-4">
              {/* First Name */}
              <Controller
                name="first_name"
                control={control}
                rules={{ required: "First name is required" }}
                render={({ field, fieldState }) => (
                  <div className="w-full">
                    <Input
                      {...field}
                      placeholder="Enter first name"
                      error={!!fieldState.error}
                      aria-invalid={!!fieldState.error}
                      aria-describedby="first-name-error"
                      id="lead-first-name"
                      autoFocus
                      className="w-full"
                      containerProps={{ className: "min-w-[100px]" }}
                    />
                    {fieldState.error && (
                      <Typography color="red" variant="small" id="first-name-error" className="mt-1">
                        {fieldState.error.message}
                      </Typography>
                    )}
                  </div>
                )}
              />

              {/* Last Name */}
              <Controller
                name="last_name"
                control={control}
                rules={{ required: "Last name is required" }}
                render={({ field, fieldState }) => (
                  <div className="w-full">
                    <Input
                      {...field}
                      placeholder="Enter last name"
                      error={!!fieldState.error}
                      aria-invalid={!!fieldState.error}
                      aria-describedby="last-name-error"
                      id="lead-last-name"
                      className="w-full"
                      containerProps={{ className: "min-w-[100px]" }}
                    />
                    {fieldState.error && (
                      <Typography color="red" variant="small" id="last-name-error" className="mt-1">
                        {fieldState.error.message}
                      </Typography>
                    )}
                  </div>
                )}
              />

              {/* Email */}
              <Controller
                name="email"
                control={control}
                rules={{
                  required: "Email is required",
                  pattern: {
                    value: /^[^@\s]+@[^@\s]+\.[^@\s]+$/,
                    message: "Invalid email address",
                  },
                }}
                render={({ field, fieldState }) => (
                  <div className="w-full">
                    <Input
                      {...field}
                      placeholder="Enter email address"
                      type="email"
                      error={!!fieldState.error}
                      aria-invalid={!!fieldState.error}
                      aria-describedby="email-error"
                      id="lead-email"
                      className="w-full"
                      containerProps={{ className: "min-w-[100px]" }}
                    />
                    {fieldState.error && (
                      <Typography color="red" variant="small" id="email-error" className="mt-1">
                        {fieldState.error.message}
                      </Typography>
                    )}
                  </div>
                )}
              />

              {/* Phone */}
              <Controller
                name="phone"
                control={control}
                rules={{
                  required: "Phone is required",
                  pattern: {
                    value: /^\d{10,15}$/,
                    message: "Phone must be 10-15 digits",
                  },
                }}
                render={({ field, fieldState }) => (
                  <div className="w-full">
                    <Input
                      {...field}
                      placeholder="Enter phone number"
                      error={!!fieldState.error}
                      aria-invalid={!!fieldState.error}
                      aria-describedby="phone-error"
                      id="lead-phone"
                      className="w-full"
                      containerProps={{ className: "min-w-[100px]" }}
                    />
                    {fieldState.error && (
                      <Typography color="red" variant="small" id="phone-error" className="mt-1">
                        {fieldState.error.message}
                      </Typography>
                    )}
                  </div>
                )}
              />

              {/* Status */}
              <Controller
                name="status"
                control={control}
                rules={{ required: "Status is required" }}
                render={({ field, fieldState }) => (
                  <div className="w-full">
                    <select
                      {...field}
                      id="lead-status"
                      className={`w-full border rounded px-3 py-2 ${fieldState.error ? 'border-red-500' : 'border-gray-300'}`}
                      aria-invalid={!!fieldState.error}
                    >
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="qualified">Qualified</option>
                      <option value="lost">Lost</option>
                    </select>
                    {fieldState.error && (
                      <Typography color="red" variant="small" id="status-error" className="mt-1">
                        {fieldState.error.message}
                      </Typography>
                    )}
                  </div>
                )}
              />

              {/* Notes (optional) */}
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <div className="w-full">
                    <Input
                      {...field}
                      placeholder="Add notes (optional)"
                      id="lead-notes"
                      multiline
                      rows={2}
                      className="w-full"
                      containerProps={{ className: "min-w-[100px]" }}
                    />
                  </div>
                )}
              />

              {/* Error rendering */}
              {addLeadError && (
                isValidationError(addLeadError) ? (
                  addLeadError.detail.map((e: { msg: string }, i: number) => (
                    <Typography key={i} color="red" variant="small" className="mt-2">
                      {e.msg}
                    </Typography>
                  ))
                ) : (
                  <Typography color="red" variant="small" className="mt-2">
                    {typeof addLeadError === 'string' ? addLeadError : 'Failed to save lead'}
                  </Typography>
                )
              )}
            </DialogBody>
            <DialogFooter className="gap-2 pt-4">
              <Button 
                color="red" 
                variant="text" 
                onClick={closeDialog} 
                type="button"
                className="mr-2"
              >
                Cancel
              </Button>
              <Button 
                color="blue" 
                type="submit" 
                loading={addLeadLoading} 
                disabled={addLeadLoading}
                className="ml-2"
              >
                {addLeadLoading ? "Saving..." : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </DialogBody>
      </Dialog>

      <Dialog open={deleteDialogOpen} handler={() => setDeleteDialogOpen(false)} size="xs">
        <DialogHeader>Delete Lead</DialogHeader>
        <DialogBody>
          Are you sure you want to delete this lead?
        </DialogBody>
        <DialogFooter className="gap-2">
          <Button color="blue-gray" variant="text" onClick={() => setDeleteDialogOpen(false)} type="button">
            Cancel
          </Button>
          <Button color="red" onClick={confirmDelete} type="button">
            Delete
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
}; 