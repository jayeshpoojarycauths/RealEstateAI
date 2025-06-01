import { useState } from 'react';
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Switch,
  Input,
  Select,
  Option,
} from '@material-tailwind/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../config/api';
import { LoadingSpinner } from '../../components/common/LoadingStates';
import { useToast } from '../../components/common/Toast';

interface SystemSettings {
  maintenanceMode: boolean;
  defaultLanguage: string;
  maxFileSize: number;
  allowedFileTypes: string[];
  emailProvider: string;
  smtpSettings: {
    host: string;
    port: number;
    username: string;
    password: string;
  };
  featureFlags: {
    enableAnalytics: boolean;
    enableAuditLogs: boolean;
    enableMultiTenancy: boolean;
  };
}

export const SystemSettings = () => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<SystemSettings | null>(null);

  const { isLoading } = useQuery<SystemSettings>({
    queryKey: ['systemSettings'],
    queryFn: async () => {
      const { data } = await api.get('/platform/settings');
      setSettings(data);
      return data;
    },
  });

  const updateSettings = useMutation({
    mutationFn: async (newSettings: SystemSettings) => {
      const { data } = await api.put('/platform/settings', newSettings);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['systemSettings'] });
      showToast('success', 'Settings updated successfully');
    },
    onError: (error: Error) => {
      showToast('error', `Failed to update settings: ${error.message}`);
    },
  });

  const handleUpdateSettings = () => {
    if (settings) {
      updateSettings.mutate(settings);
    }
  };

  if (isLoading || !settings) {
    return <LoadingSpinner size="lg" />;
  }

  return (
    <div className="space-y-6">
      <Typography variant="h4" color="blue-gray">
        System Settings
      </Typography>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* General Settings */}
        <Card>
          <CardHeader color="blue" className="mb-4">
            <Typography variant="h6">General Settings</Typography>
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="flex items-center justify-between">
              <Typography variant="small">Maintenance Mode</Typography>
              <Switch
                checked={settings.maintenanceMode}
                onChange={(e) =>
                  setSettings({ ...settings, maintenanceMode: e.target.checked })
                }
              />
            </div>
            <div>
              <Typography variant="small" className="mb-2">
                Default Language
              </Typography>
              <Select
                value={settings.defaultLanguage}
                onChange={(value) =>
                  setSettings({ ...settings, defaultLanguage: value as string })
                }
              >
                <Option value="en">English</Option>
                <Option value="es">Spanish</Option>
                <Option value="fr">French</Option>
              </Select>
            </div>
          </CardBody>
        </Card>

        {/* File Upload Settings */}
        <Card>
          <CardHeader color="blue" className="mb-4">
            <Typography variant="h6">File Upload Settings</Typography>
          </CardHeader>
          <CardBody className="space-y-4">
            <div>
              <Typography variant="small" className="mb-2">
                Max File Size (MB)
              </Typography>
              <Input
                type="number"
                value={settings.maxFileSize}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    maxFileSize: parseInt(e.target.value),
                  })
                }
              />
            </div>
            <div>
              <Typography variant="small" className="mb-2">
                Allowed File Types
              </Typography>
              <Input
                value={settings.allowedFileTypes.join(', ')}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    allowedFileTypes: e.target.value.split(',').map((type) => type.trim()),
                  })
                }
              />
            </div>
          </CardBody>
        </Card>

        {/* Email Settings */}
        <Card>
          <CardHeader color="blue" className="mb-4">
            <Typography variant="h6">Email Settings</Typography>
          </CardHeader>
          <CardBody className="space-y-4">
            <div>
              <Typography variant="small" className="mb-2">
                Email Provider
              </Typography>
              <Select
                value={settings.emailProvider}
                onChange={(value) =>
                  setSettings({ ...settings, emailProvider: value as string })
                }
              >
                <Option value="smtp">SMTP</Option>
                <Option value="sendgrid">SendGrid</Option>
                <Option value="aws">Amazon SES</Option>
              </Select>
            </div>
            <div className="space-y-4">
              <Input
                label="SMTP Host"
                value={settings.smtpSettings.host}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      host: e.target.value,
                    },
                  })
                }
              />
              <Input
                label="SMTP Port"
                type="number"
                value={settings.smtpSettings.port}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      port: parseInt(e.target.value),
                    },
                  })
                }
              />
              <Input
                label="SMTP Username"
                value={settings.smtpSettings.username}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      username: e.target.value,
                    },
                  })
                }
              />
              <Input
                label="SMTP Password"
                type="password"
                value={settings.smtpSettings.password}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      password: e.target.value,
                    },
                  })
                }
              />
            </div>
          </CardBody>
        </Card>

        {/* Feature Flags */}
        <Card>
          <CardHeader color="blue" className="mb-4">
            <Typography variant="h6">Feature Flags</Typography>
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="flex items-center justify-between">
              <Typography variant="small">Enable Analytics</Typography>
              <Switch
                checked={settings.featureFlags.enableAnalytics}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    featureFlags: {
                      ...settings.featureFlags,
                      enableAnalytics: e.target.checked,
                    },
                  })
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <Typography variant="small">Enable Audit Logs</Typography>
              <Switch
                checked={settings.featureFlags.enableAuditLogs}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    featureFlags: {
                      ...settings.featureFlags,
                      enableAuditLogs: e.target.checked,
                    },
                  })
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <Typography variant="small">Enable Multi-tenancy</Typography>
              <Switch
                checked={settings.featureFlags.enableMultiTenancy}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    featureFlags: {
                      ...settings.featureFlags,
                      enableMultiTenancy: e.target.checked,
                    },
                  })
                }
              />
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleUpdateSettings}>Save Settings</Button>
      </div>
    </div>
  );
}; 