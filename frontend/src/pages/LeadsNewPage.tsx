import React, { useState } from 'react';
import {
  SafeCard as Card,
  SafeCardBody as CardBody,
  SafeTypography as Typography,
  SafeButton as Button,
  SafeInput as Input,
  SafeSelect as Select,
  SafeOption as Option,
  SafeAlert as Alert,
} from "../components/SafeMTW";
import api from '../services/api';
import * as RadixSelect from '@radix-ui/react-select';
import { CheckIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

// Custom dropdown component using Radix UI
const StatusDropdown: React.FC<{
  value: string;
  onChange: (value: string) => void;
}> = ({ value, onChange }) => (
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
          {['new', 'contacted', 'qualified', 'lost'].map((status) => (
            <RadixSelect.Item
              key={status}
              value={status}
              className="flex items-center px-4 py-2 rounded-md cursor-pointer text-blue-gray-700 hover:bg-blue-100 focus:bg-blue-200 focus:outline-none"
            >
              <RadixSelect.ItemText>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </RadixSelect.ItemText>
              <RadixSelect.ItemIndicator className="ml-auto">
                <CheckIcon className="h-4 w-4 text-blue-500" />
              </RadixSelect.ItemIndicator>
            </RadixSelect.Item>
          ))}
        </RadixSelect.Viewport>
      </RadixSelect.Content>
    </RadixSelect.Portal>
  </RadixSelect.Root>
);

export const LeadsNewPage: React.FC = () => {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    status: 'new',
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess('');
    setError('');
    try {
      const payload = {
        ...form,
        name: `${form.first_name} ${form.last_name}`.trim(),
      };
      await api.post('/leads/new/', payload);
      setSuccess('Lead created successfully!');
      setForm({ first_name: '', last_name: '', email: '', phone: '', status: 'new', notes: '' });
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create lead');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-blue-gray-50">
      <Card className="w-full max-w-3xl p-10 shadow-2xl border border-blue-gray-100">
        <CardBody>
          <Typography variant="h5" color="blue-gray" className="mb-10 font-bold tracking-wide">Create New Lead</Typography>
          <form onSubmit={handleSubmit} className="space-y-8 mt-4">
            <div className="flex gap-8">
              <Input
                label="First Name"
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                required
                className="flex-1 px-4 py-3 border border-blue-gray-200 rounded-lg bg-white text-blue-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              />
              <Input
                label="Last Name"
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                required
                className="flex-1 px-4 py-3 border border-blue-gray-200 rounded-lg bg-white text-blue-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              />
            </div>
            <Input
              label="Email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-blue-gray-200 rounded-lg bg-white text-blue-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
            <Input
              label="Phone"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-blue-gray-200 rounded-lg bg-white text-blue-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
            <div>
              <label className="block text-blue-gray-700 font-medium mb-2">Status</label>
              <StatusDropdown value={form.status} onChange={(status) => setForm({ ...form, status })} />
            </div>
            <Input
              label="Notes"
              name="notes"
              value={form.notes}
              onChange={handleChange}
              multiline
              rows={2}
              className="w-full px-4 py-3 border border-blue-gray-200 rounded-lg bg-white text-blue-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
            <Button color="blue" type="submit" loading={loading} disabled={loading} className="w-full mt-6 py-3 text-lg font-semibold rounded-lg shadow-md">
              {loading ? 'Saving...' : 'Create Lead'}
            </Button>
            {success && <Alert color="green" className="mt-6 text-base font-medium">{success}</Alert>}
            {error && <Alert color="red" className="mt-6 text-base font-medium">{error}</Alert>}
          </form>
        </CardBody>
      </Card>
    </div>
  );
};

export default LeadsNewPage; 