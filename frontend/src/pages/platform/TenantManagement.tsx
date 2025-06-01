import { useState } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Input,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
} from "@material-tailwind/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../config/api";
import { LoadingSpinner } from "../../components/common/LoadingStates";
import { useToast } from "../../components/common/Toast";

interface Tenant {
  id: string;
  name: string;
  domain: string;
  status: "active" | "suspended" | "pending";
  createdAt: string;
  updatedAt: string;
}

interface CreateTenantDto {
  name: string;
  domain: string;
}

const DOMAIN_REGEX = /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,}$/;
const sanitize = (value: string) => value.replace(/[^a-zA-Z0-9-\.]/g, "");

export const TenantManagement = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTenant, setNewTenant] = useState<CreateTenantDto>({
    name: "",
    domain: "",
  });
  const [inputErrors, setInputErrors] = useState<{
    name?: string;
    domain?: string;
  }>({});
  const [fetchError, setFetchError] = useState<string | null>(null);
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const validateInputs = (name: string, domain: string) => {
    const errors: { name?: string; domain?: string } = {};
    const sanitizedDomain = sanitize(domain);
    if (!name.trim()) {
      errors.name = "Tenant name is required.";
    } else if (name.length < 2 || name.length > 50) {
      errors.name = "Tenant name must be 2-50 characters.";
    }
    if (!sanitizedDomain) {
      errors.domain = "Domain is required.";
    } else if (sanitizedDomain.length < 4 || sanitizedDomain.length > 63) {
      errors.domain = "Domain must be 4-63 characters.";
    } else if (!DOMAIN_REGEX.test(sanitizedDomain)) {
      errors.domain = "Invalid domain format (e.g., example.com).";
    }
    return errors;
  };

  const {
    data: tenants,
    isLoading,
    error,
  } = useQuery<Tenant[]>({
    queryKey: ["tenants"],
    queryFn: async () => {
      const { data } = await api.get("/platform/tenants");
      return data;
    },
    onError: (err: any) => {
      setFetchError(err?.message || "Failed to fetch tenants.");
      showToast("error", err?.message || "Failed to fetch tenants.");
    },
  });

  const createTenant = useMutation({
    mutationFn: async (tenant: CreateTenantDto) => {
      const { data } = await api.post("/platform/tenants", tenant);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
      showToast("success", "Tenant created successfully");
      setIsCreateModalOpen(false);
      setNewTenant({ name: "", domain: "" });
      setInputErrors({});
    },
    onError: (error: Error) => {
      showToast("error", `Failed to create tenant: ${error.message}`);
    },
  });

  const handleInputChange = (field: keyof CreateTenantDto, value: string) => {
    const sanitizedValue = field === "domain" ? sanitize(value) : value;
    setNewTenant((prev) => ({ ...prev, [field]: sanitizedValue }));
    setInputErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleCreateTenant = () => {
    const errors = validateInputs(newTenant.name, newTenant.domain);
    setInputErrors(errors);
    if (Object.keys(errors).length === 0) {
      createTenant.mutate({
        name: newTenant.name.trim(),
        domain: sanitize(newTenant.domain.trim()),
      });
    }
  };

  const isCreateDisabled =
    !newTenant.name.trim() ||
    !newTenant.domain.trim() ||
    Object.keys(validateInputs(newTenant.name, newTenant.domain)).length > 0;

  if (isLoading) {
    return <LoadingSpinner size="lg" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <Typography variant="h4" color="blue-gray">
          Tenant Management
        </Typography>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          Create Tenant
        </Button>
      </div>

      {fetchError && (
        <div className="bg-red-100 text-red-700 p-2 rounded mb-4">
          {fetchError}
        </div>
      )}

      <Card>
        <CardHeader color="blue" className="mb-4">
          <Typography variant="h6">Tenants</Typography>
        </CardHeader>
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full min-w-max table-auto text-left">
              <thead>
                <tr>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography
                      variant="small"
                      color="blue-gray"
                      className="font-normal leading-none opacity-70"
                    >
                      Name
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography
                      variant="small"
                      color="blue-gray"
                      className="font-normal leading-none opacity-70"
                    >
                      Domain
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography
                      variant="small"
                      color="blue-gray"
                      className="font-normal leading-none opacity-70"
                    >
                      Status
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography
                      variant="small"
                      color="blue-gray"
                      className="font-normal leading-none opacity-70"
                    >
                      Created At
                    </Typography>
                  </th>
                </tr>
              </thead>
              <tbody>
                {tenants?.map((tenant) => (
                  <tr key={tenant.id}>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                      >
                        {tenant.name}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                      >
                        {tenant.domain}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color={tenant.status === "active" ? "green" : "red"}
                        className="font-normal"
                      >
                        {tenant.status}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                      >
                        {new Date(tenant.createdAt).toLocaleDateString()}
                      </Typography>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Create Tenant Modal */}
      <Dialog
        open={isCreateModalOpen}
        handler={() => setIsCreateModalOpen(false)}
      >
        <DialogHeader>Create New Tenant</DialogHeader>
        <DialogBody>
          <div className="space-y-4">
            <Input
              label="Tenant Name"
              value={newTenant.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              error={!!inputErrors.name}
              crossOrigin={undefined}
            />
            {inputErrors.name && (
              <div className="text-red-600 text-sm">{inputErrors.name}</div>
            )}
            <Input
              label="Domain"
              value={newTenant.domain}
              onChange={(e) => handleInputChange("domain", e.target.value)}
              error={!!inputErrors.domain}
              crossOrigin={undefined}
            />
            {inputErrors.domain && (
              <div className="text-red-600 text-sm">{inputErrors.domain}</div>
            )}
          </div>
        </DialogBody>
        <DialogFooter>
          <Button
            variant="text"
            color="red"
            onClick={() => setIsCreateModalOpen(false)}
            className="mr-1"
          >
            Cancel
          </Button>
          <Button
            variant="gradient"
            color="green"
            onClick={handleCreateTenant}
            disabled={isCreateDisabled}
          >
            Create
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};
