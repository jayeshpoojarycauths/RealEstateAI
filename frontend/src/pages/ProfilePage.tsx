import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Input,
  Spinner,
  Alert,
} from "@material-tailwind/react";
import { useAuth } from "../contexts/AuthContext";
import api from "../services/api";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  created_at: string;
  phone?: string;
}

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

interface PasswordChangeData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

const defaultEventHandlers = {
  onResize: undefined,
  onResizeCapture: undefined,
  onPointerEnterCapture: undefined,
  onPointerLeaveCapture: undefined,
};

export const ProfilePage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [profileData, setProfileData] = useState<ProfileData>({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
  });
  const [passwordData, setPasswordData] = useState<PasswordChangeData>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const { token } = useAuth();
  const {
    getButtonProps,
    getCardProps,
    getCardBodyProps,
    getCardHeaderProps,
    getTypographyProps,
    getInputProps,
  } = useMaterialTailwind();

  const fetchProfile = React.useCallback(async () => {
    try {
      const response = await api.get<UserProfile>("/api/v1/users/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProfileData({
        first_name: response.data.first_name,
        last_name: response.data.last_name,
        email: response.data.email,
        phone: response.data.phone || "",
      });
    } catch (err) {
      setError("Failed to load profile data");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      await api.put("/api/v1/users/me", profileData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess("Profile updated successfully");
      fetchProfile();
    } catch (err) {
      setError("Failed to update profile");
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError("New passwords do not match");
      return;
    }

    try {
      await api.put(
        "/api/v1/users/me/password",
        {
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      setSuccess("Password updated successfully");
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (err) {
      setError("Failed to update password");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner className="h-8 w-8" {...defaultEventHandlers} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Typography variant="h4" color="blue-gray" {...getTypographyProps()}>
        Profile Settings
      </Typography>

      {error && (
        <Alert color="red" className="mb-4">
          {error}
        </Alert>
      )}

      {success && (
        <Alert color="green" className="mb-4">
          {success}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profile Information */}
        <Card {...getCardProps()}>
          <CardHeader
            variant="gradient"
            color="blue"
            className="mb-4 p-6"
            {...getCardHeaderProps()}
          >
            <Typography variant="h6" color="white" {...getTypographyProps()}>
              Profile Information
            </Typography>
          </CardHeader>
          <CardBody className="p-6" {...getCardBodyProps()}>
            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="text"
                  label="First Name"
                  name="first_name"
                  value={profileData.first_name}
                  onChange={handleInputChange}
                  required
                  {...getInputProps()}
                />
                <Input
                  type="text"
                  label="Last Name"
                  name="last_name"
                  value={profileData.last_name}
                  onChange={handleInputChange}
                  required
                  {...getInputProps()}
                />
              </div>
              <Input
                type="email"
                label="Email"
                value={profileData.email}
                onChange={handleInputChange}
                required
                {...getInputProps()}
              />
              <Input
                type="tel"
                label="Phone"
                value={profileData.phone || ""}
                onChange={handleInputChange}
                {...getInputProps()}
              />
              <Button
                type="submit"
                variant="filled"
                color="blue"
                fullWidth
                {...getButtonProps()}
              >
                Save Changes
              </Button>
            </form>
          </CardBody>
        </Card>

        {/* Change Password */}
        <Card {...getCardProps()}>
          <CardHeader
            variant="gradient"
            color="blue"
            className="mb-4 p-6"
            {...getCardHeaderProps()}
          >
            <Typography variant="h6" color="white" {...getTypographyProps()}>
              Change Password
            </Typography>
          </CardHeader>
          <CardBody className="p-6" {...getCardBodyProps()}>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <Input
                type="password"
                label="Current Password"
                name="current_password"
                value={passwordData.current_password}
                onChange={handleInputChange}
                required
                {...getInputProps()}
              />
              <Input
                type="password"
                label="New Password"
                name="new_password"
                value={passwordData.new_password}
                onChange={handleInputChange}
                required
                {...getInputProps()}
              />
              <Input
                type="password"
                label="Confirm New Password"
                name="confirm_password"
                value={passwordData.confirm_password}
                onChange={handleInputChange}
                required
                {...getInputProps()}
              />
              <Button
                type="submit"
                variant="filled"
                color="blue"
                fullWidth
                {...getButtonProps()}
              >
                Change Password
              </Button>
            </form>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;
