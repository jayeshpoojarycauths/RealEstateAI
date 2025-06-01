import { useState, ChangeEvent } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../config/api";
import { LoadingSpinner } from "../../components/common/LoadingStates";
import { useToast } from "../../components/common/Toast";
import {
  SafeTypography,
  SafeButton,
  SafeCard,
  SafeCardHeader,
  SafeCardBody,
  SafeInput,
  SafeSelect,
  SafeOption,
  SafeSwitch,
} from "../../components/SafeMTW";

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
    password?: string;
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
  const [smtpPasswordDirty, setSmtpPasswordDirty] = useState(false);
  const [inputErrors, setInputErrors] = useState<{ [key: string]: string }>({});

  const { isLoading } = useQuery<SystemSettings>({
    queryKey: ["systemSettings"],
    queryFn: async () => {
      const { data } = await api.get("/platform/settings");
      if (data.smtpSettings && data.smtpSettings.password) {
        data.smtpSettings.password = "********";
      }
      setSettings(data);
      return data;
    },
  });

  const validateInputs = (settings: SystemSettings) => {
    const errors: { [key: string]: string } = {};
    if (settings.emailProvider === "smtp") {
      if (!settings.smtpSettings.host.trim()) {
        errors.smtpHost = "SMTP host is required.";
      }
      if (
        !settings.smtpSettings.port ||
        isNaN(settings.smtpSettings.port) ||
        settings.smtpSettings.port <= 0
      ) {
        errors.smtpPort = "Valid SMTP port is required.";
      }
      if (!settings.smtpSettings.username.trim()) {
        errors.smtpUsername = "SMTP username is required.";
      }
      if (smtpPasswordDirty && !settings.smtpSettings.password.trim()) {
        errors.smtpPassword = "SMTP password is required.";
      }
    }
    return errors;
  };

  const updateSettings = useMutation({
    mutationFn: async (newSettings: SystemSettings) => {
      const { data } = await api.put("/platform/settings", newSettings);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["systemSettings"] });
      showToast("success", "Settings updated successfully");
    },
    onError: (error: Error) => {
      showToast("error", `Failed to update settings: ${error.message}`);
    },
  });

  const handleUpdateSettings = () => {
    if (!settings) return;
    const errors = validateInputs(settings);
    setInputErrors(errors);
    if (Object.keys(errors).length > 0) return;
    const settingsToSend = { ...settings };
    if (
      "password" in settingsToSend.smtpSettings &&
      settingsToSend.smtpSettings.password === "********"
    ) {
      settingsToSend.smtpSettings.password = undefined;
    }
    updateSettings.mutate(settingsToSend);
  };

  if (isLoading || !settings) {
    return <LoadingSpinner size="lg" />;
  }

  return (
    <div className="space-y-6">
      <SafeTypography variant="h4" color="blue-gray">
        System Settings
      </SafeTypography>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* General Settings */}
        <SafeCard>
          <SafeCardHeader color="blue" className="mb-4">
            <SafeTypography variant="h6">General Settings</SafeTypography>
          </SafeCardHeader>
          <SafeCardBody className="space-y-4">
            <div className="flex items-center justify-between">
              <SafeTypography variant="small">Maintenance Mode</SafeTypography>
              <SafeSwitch
                checked={settings.maintenanceMode}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setSettings({
                    ...settings,
                    maintenanceMode: e.target.checked,
                  })
                }
              />
            </div>
            <div>
              <SafeTypography variant="small" className="mb-2">
                Default Language
              </SafeTypography>
              <SafeSelect
                value={settings.defaultLanguage}
                onChange={(value: string | undefined) =>
                  setSettings({ ...settings, defaultLanguage: value as string })
                }
              >
                <SafeOption value="en">English</SafeOption>
                <SafeOption value="es">Spanish</SafeOption>
                <SafeOption value="fr">French</SafeOption>
              </SafeSelect>
            </div>
          </SafeCardBody>
        </SafeCard>

        {/* File Upload Settings */}
        <SafeCard>
          <SafeCardHeader color="blue" className="mb-4">
            <SafeTypography variant="h6">File Upload Settings</SafeTypography>
          </SafeCardHeader>
          <SafeCardBody className="space-y-4">
            <div>
              <SafeTypography variant="small" className="mb-2">
                Max File Size (MB)
              </SafeTypography>
              <SafeInput
                type="number"
                value={settings.maxFileSize}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setSettings({
                    ...settings,
                    maxFileSize: parseInt(e.target.value),
                  })
                }
              />
            </div>
            <div>
              <SafeTypography variant="small" className="mb-2">
                Allowed File Types
              </SafeTypography>
              <SafeInput
                value={settings.allowedFileTypes.join(", ")}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setSettings({
                    ...settings,
                    allowedFileTypes: e.target.value
                      .split(",")
                      .map((type: string) => type.trim()),
                  })
                }
              />
            </div>
          </SafeCardBody>
        </SafeCard>

        {/* Email Settings */}
        <SafeCard>
          <SafeCardHeader color="blue" className="mb-4">
            <SafeTypography variant="h6">Email Settings</SafeTypography>
          </SafeCardHeader>
          <SafeCardBody className="space-y-4">
            <div>
              <SafeTypography variant="small" className="mb-2">
                Email Provider
              </SafeTypography>
              <SafeSelect
                value={settings.emailProvider}
                onChange={(value: string | undefined) =>
                  setSettings({ ...settings, emailProvider: value as string })
                }
              >
                <SafeOption value="smtp">SMTP</SafeOption>
                <SafeOption value="sendgrid">SendGrid</SafeOption>
                <SafeOption value="aws">Amazon SES</SafeOption>
              </SafeSelect>
            </div>
            <div className="space-y-4">
              <SafeInput
                label="SMTP Host"
                value={settings.smtpSettings.host}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      host: e.target.value,
                    },
                  })
                }
                error={!!inputErrors.smtpHost}
              />
              {inputErrors.smtpHost && (
                <div className="text-red-600 text-sm">
                  {inputErrors.smtpHost}
                </div>
              )}
              <SafeInput
                label="SMTP Port"
                type="number"
                value={settings.smtpSettings.port}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      port: parseInt(e.target.value),
                    },
                  })
                }
                error={!!inputErrors.smtpPort}
              />
              {inputErrors.smtpPort && (
                <div className="text-red-600 text-sm">
                  {inputErrors.smtpPort}
                </div>
              )}
              <SafeInput
                label="SMTP Username"
                value={settings.smtpSettings.username}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      username: e.target.value,
                    },
                  })
                }
                error={!!inputErrors.smtpUsername}
              />
              {inputErrors.smtpUsername && (
                <div className="text-red-600 text-sm">
                  {inputErrors.smtpUsername}
                </div>
              )}
              <SafeInput
                label="SMTP Password"
                type="password"
                value={settings.smtpSettings.password}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  setSettings({
                    ...settings,
                    smtpSettings: {
                      ...settings.smtpSettings,
                      password: e.target.value,
                    },
                  });
                  setSmtpPasswordDirty(true);
                }}
                error={!!inputErrors.smtpPassword}
              />
              {inputErrors.smtpPassword && (
                <div className="text-red-600 text-sm">
                  {inputErrors.smtpPassword}
                </div>
              )}
              {/*
                SECURITY NOTE: In production, never store or handle real SMTP credentials in the frontend. Use environment variables or a secure vault on the backend, and only allow credential updates via secure, dedicated endpoints.
              */}
            </div>
          </SafeCardBody>
        </SafeCard>

        {/* Feature Flags */}
        <SafeCard>
          <SafeCardHeader color="blue" className="mb-4">
            <SafeTypography variant="h6">Feature Flags</SafeTypography>
          </SafeCardHeader>
          <SafeCardBody className="space-y-4">
            <div className="flex items-center justify-between">
              <SafeTypography variant="small">Enable Analytics</SafeTypography>
              <SafeSwitch
                checked={settings.featureFlags.enableAnalytics}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
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
              <SafeTypography variant="small">Enable Audit Logs</SafeTypography>
              <SafeSwitch
                checked={settings.featureFlags.enableAuditLogs}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
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
              <SafeTypography variant="small">
                Enable Multi-tenancy
              </SafeTypography>
              <SafeSwitch
                checked={settings.featureFlags.enableMultiTenancy}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
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
          </SafeCardBody>
        </SafeCard>
      </div>

      <div className="flex justify-end">
        <SafeButton
          onClick={handleUpdateSettings}
          disabled={updateSettings.isPending}
        >
          {updateSettings.isPending ? "Saving..." : "Save Settings"}
        </SafeButton>
      </div>
    </div>
  );
};
