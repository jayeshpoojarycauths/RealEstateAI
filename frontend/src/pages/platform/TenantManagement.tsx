import { useState } from 'react';
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
} from '@material-tailwind/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../config/api';
import { LoadingSpinner } from '../../components/common/LoadingStates';
import { useToast } from '../../components/common/Toast';

interface Tenant {
  id: string;
  name: string;
  domain: string;
  status: 'active' | 'suspended' | 'pending';
  createdAt: string;
  updatedAt: string;
}

interface CreateTenantDto {
  name: string;
  domain: string;
}

export const TenantManagement = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTenant, setNewTenant] = useState<CreateTenantDto>({
    name: '',
    domain: '',
  });
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data: tenants, isLoading } = useQuery<Tenant[]>({
    queryKey: ['tenants'],
    queryFn: async () => {
      const { data } = await api.get('/platform/tenants');
      return data;
    },
  });

  const createTenant = useMutation({
    mutationFn: async (tenant: CreateTenantDto) => {
      const { data } = await api.post('/platform/tenants', tenant);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] });
      showToast('success', 'Tenant created successfully');
      setIsCreateModalOpen(false);
      setNewTenant({ name: '', domain: '' });
    },
    onError: (error: Error) => {
      showToast('error', `Failed to create tenant: ${error.message}`);
    },
  });

  const handleCreateTenant = () => {
    createTenant.mutate(newTenant);
  };

  if (isLoading) {
    return <LoadingSpinner size="lg" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <Typography variant="h4" color="blue-gray">
          Tenant Management
        </Typography>
        <Button onClick={() => setIsCreateModalOpen(true)}>Create Tenant</Button>
      </div>

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
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Name
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Domain
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Status
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Created At
                    </Typography>
                  </th>
                </tr>
              </thead>
              <tbody>
                {tenants?.map((tenant) => (
                  <tr key={tenant.id}>
                    <td className="p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {tenant.name}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {tenant.domain}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color={tenant.status === 'active' ? 'green' : 'red'}
                        className="font-normal"
                      >
                        {tenant.status}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal">
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
      <Dialog open={isCreateModalOpen} handler={() => setIsCreateModalOpen(false)}>
        <DialogHeader>Create New Tenant</DialogHeader>
        <DialogBody>
          <div className="space-y-4">
            <Input
              label="Tenant Name"
              value={newTenant.name}
              onChange={(e) => setNewTenant({ ...newTenant, name: e.target.value })}
            />
            <Input
              label="Domain"
              value={newTenant.domain}
              onChange={(e) => setNewTenant({ ...newTenant, domain: e.target.value })}
            />
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
            disabled={!newTenant.name || !newTenant.domain}
          >
            Create
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
}; 