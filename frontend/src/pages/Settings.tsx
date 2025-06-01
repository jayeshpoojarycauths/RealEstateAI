import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Input,
  Select,
  Option,
  Button,
  Switch,
} from "@material-tailwind/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsService, UserSettings } from "../services/settingsService";
import { useAuth } from "../hooks/useAuth";
import { toast } from "react-hot-toast";

export const Settings: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<Partial<UserSettings>>({});

  const { data: userSettings, isLoading } = useQuery({
    queryKey: ["userSettings"],
    queryFn: settingsService.getCurrentUserSettings,
    onSuccess: (data) => {
      setSettings(data);
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: (updatedSettings: Partial<UserSettings>) =>
      settingsService.updateSettings({
        ...updatedSettings,
        userId: user?.id!,
      }),
    mutationKey: ["updateUserSettings"],
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userSettings"] });
      toast.success("Settings updated successfully");
    },
    onError: (error) => {
      toast.error("Failed to update settings");
      console.error("Error updating settings:", error);
    },
  });

  // Don't render if user is not available
  if (!user?.id) {
    return <div>Please log in to access settings.</div>;
  }

  const handleInputChange = (field: keyof UserSettings, value: string) => {
    setSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNotificationChange = (
    field: keyof UserSettings["notifications"],
    value: boolean,
  ) => {
    setSettings((prev) => ({
      ...prev,
      notifications: {
        ...(prev.notifications || {}),
        [field]: value,
      },
    }));
  };

  const handleSave = () => {
    updateSettingsMutation.mutate(settings);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-4">
      <Card>
        <CardHeader
          variant="gradient"
          color="blue"
          className="mb-4 grid h-28 place-items-center"
        >
          <Typography variant="h3" color="white">
            Settings
          </Typography>
        </CardHeader>
        <CardBody className="flex flex-col gap-4">
          {/* Profile Section */}
          <div className="mb-6">
            <Typography variant="h5" color="blue-gray" className="mb-4">
              Profile
            </Typography>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Email"
                value={settings.email || ""}
                onChange={(e) => handleInputChange("email", e.target.value)}
                disabled
              />
              <Input
                label="First Name"
                value={settings.firstName || ""}
                onChange={(e) => handleInputChange("firstName", e.target.value)}
              />
              <Input
                label="Last Name"
                value={settings.lastName || ""}
                onChange={(e) => handleInputChange("lastName", e.target.value)}
              />
              <Input
                label="Phone"
                value={settings.phone || ""}
                onChange={(e) => handleInputChange("phone", e.target.value)}
              />
            </div>
          </div>

          {/* Preferences Section */}
          <div className="mb-6">
            <Typography variant="h5" color="blue-gray" className="mb-4">
              Preferences
            </Typography>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label="Language"
                value={settings.language || "en"}
                onChange={(value) =>
                  handleInputChange("language", value as string)
                }
              >
                <Option value="en">English</Option>
                <Option value="es">Spanish</Option>
                <Option value="fr">French</Option>
              </Select>
              <Select
                label="Theme"
                value={settings.theme || "light"}
                onChange={(value) =>
                  handleInputChange("theme", value as string)
                }
              >
                <Option value="light">Light</Option>
                <Option value="dark">Dark</Option>
                <Option value="system">System</Option>
              </Select>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="mb-6">
            <Typography variant="h5" color="blue-gray" className="mb-4">
              Notifications
            </Typography>
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <Typography variant="small">Email Notifications</Typography>
                <Switch
                  checked={settings.notifications?.email || false}
                  onChange={(e) =>
                    handleNotificationChange("email", e.target.checked)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Typography variant="small">SMS Notifications</Typography>
                <Switch
                  checked={settings.notifications?.sms || false}
                  onChange={(e) =>
                    handleNotificationChange("sms", e.target.checked)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Typography variant="small">Push Notifications</Typography>
                <Switch
                  checked={settings.notifications?.push || false}
                  onChange={(e) =>
                    handleNotificationChange("push", e.target.checked)
                  }
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button
              color="blue"
              onClick={handleSave}
              disabled={updateSettingsMutation.isPending}
            >
              {updateSettingsMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};
