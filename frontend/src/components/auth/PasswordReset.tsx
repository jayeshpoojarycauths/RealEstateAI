import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Input,
} from "@material-tailwind/react";
import { useMaterialTailwind } from "../../hooks/useMaterialTailwind";
import { useAuth } from "../../hooks/useAuth";

// Define validation schema
const resetSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Invalid email format")
    .max(255, "Email must be less than 255 characters")
    .transform((val) => val.toLowerCase().trim()),
});

const newPasswordSchema = z.object({
  password: z
    .string()
    .min(1, "Password is required")
    .min(8, "Password must be at least 8 characters")
    .max(100, "Password must be less than 100 characters")
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
      "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
    ),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type ResetFormData = z.infer<typeof resetSchema>;
type NewPasswordFormData = z.infer<typeof newPasswordSchema>;

export const PasswordReset: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const { requestPasswordReset, resetPassword, error: authError } = useAuth();
  const { getButtonProps, getCardProps, getCardBodyProps, getCardHeaderProps, getTypographyProps, getInputProps } = useMaterialTailwind();
  const [isRequestSent, setIsRequestSent] = useState(false);
  const [isResetComplete, setIsResetComplete] = useState(false);

  const {
    register: registerRequest,
    handleSubmit: handleRequestSubmit,
    formState: { errors: requestErrors, isSubmitting: isRequestSubmitting },
    setError: setRequestError,
  } = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
  });

  const {
    register: registerNewPassword,
    handleSubmit: handleNewPasswordSubmit,
    formState: { errors: newPasswordErrors, isSubmitting: isNewPasswordSubmitting },
    setError: setNewPasswordError,
  } = useForm<NewPasswordFormData>({
    resolver: zodResolver(newPasswordSchema),
  });

  const onRequestSubmit = async (data: ResetFormData) => {
    try {
      await requestPasswordReset(data.email);
      setIsRequestSent(true);
    } catch (err) {
      setRequestError("root", {
        type: "manual",
        message: err instanceof Error ? err.message : "An error occurred",
      });
    }
  };

  const onNewPasswordSubmit = async (data: NewPasswordFormData) => {
    if (!token) {
      setNewPasswordError("root", {
        type: "manual",
        message: "Invalid reset token",
      });
      return;
    }

    try {
      await resetPassword(token, data.password);
      setIsResetComplete(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err) {
      setNewPasswordError("root", {
        type: "manual",
        message: err instanceof Error ? err.message : "An error occurred",
      });
    }
  };

  if (isResetComplete) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card {...getCardProps()} className="w-full max-w-md">
          <CardHeader {...getCardHeaderProps()} className="text-center">
            <Typography {...getTypographyProps()} variant="h4" color="blue-gray">
              Password Reset Complete
            </Typography>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <Typography {...getTypographyProps()} variant="paragraph" color="gray" className="text-center">
              Your password has been reset successfully. You will be redirected to the login page.
            </Typography>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (isRequestSent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card {...getCardProps()} className="w-full max-w-md">
          <CardHeader {...getCardHeaderProps()} className="text-center">
            <Typography {...getTypographyProps()} variant="h4" color="blue-gray">
              Check Your Email
            </Typography>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <Typography {...getTypographyProps()} variant="paragraph" color="gray" className="text-center">
              If an account exists with the email you provided, you will receive a password reset link.
            </Typography>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card {...getCardProps()} className="w-full max-w-md">
          <CardHeader {...getCardHeaderProps()} className="text-center">
            <Typography {...getTypographyProps()} variant="h4" color="blue-gray">
              Reset Your Password
            </Typography>
          </CardHeader>
          <CardBody {...getCardBodyProps()}>
            <form onSubmit={handleNewPasswordSubmit(onNewPasswordSubmit)} className="space-y-6">
              <div>
                <Input
                  {...getInputProps()}
                  type="password"
                  label="New Password"
                  {...registerNewPassword("password")}
                  error={!!newPasswordErrors.password}
                  aria-invalid={!!newPasswordErrors.password}
                  aria-describedby={newPasswordErrors.password ? "password-error" : undefined}
                />
                {newPasswordErrors.password && (
                  <Typography 
                    {...getTypographyProps()} 
                    variant="small" 
                    color="red" 
                    className="mt-1"
                    id="password-error"
                  >
                    {newPasswordErrors.password.message}
                  </Typography>
                )}
              </div>

              <div>
                <Input
                  {...getInputProps()}
                  type="password"
                  label="Confirm Password"
                  {...registerNewPassword("confirmPassword")}
                  error={!!newPasswordErrors.confirmPassword}
                  aria-invalid={!!newPasswordErrors.confirmPassword}
                  aria-describedby={newPasswordErrors.confirmPassword ? "confirm-password-error" : undefined}
                />
                {newPasswordErrors.confirmPassword && (
                  <Typography 
                    {...getTypographyProps()} 
                    variant="small" 
                    color="red" 
                    className="mt-1"
                    id="confirm-password-error"
                  >
                    {newPasswordErrors.confirmPassword.message}
                  </Typography>
                )}
              </div>

              {(newPasswordErrors.root || authError) && (
                <Typography 
                  {...getTypographyProps()} 
                  variant="small" 
                  color="red" 
                  className="text-center"
                  role="alert"
                >
                  {newPasswordErrors.root?.message || authError}
                </Typography>
              )}

              <Button
                {...getButtonProps()}
                type="submit"
                fullWidth
                disabled={isNewPasswordSubmitting}
                aria-busy={isNewPasswordSubmitting}
              >
                {isNewPasswordSubmitting ? "Resetting..." : "Reset Password"}
              </Button>
            </form>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card {...getCardProps()} className="w-full max-w-md">
        <CardHeader {...getCardHeaderProps()} className="text-center">
          <Typography {...getTypographyProps()} variant="h4" color="blue-gray">
            Reset Password
          </Typography>
        </CardHeader>
        <CardBody {...getCardBodyProps()}>
          <form onSubmit={handleRequestSubmit(onRequestSubmit)} className="space-y-6">
            <div>
              <Input
                {...getInputProps()}
                type="email"
                label="Email address"
                {...registerRequest("email")}
                error={!!requestErrors.email}
                aria-invalid={!!requestErrors.email}
                aria-describedby={requestErrors.email ? "email-error" : undefined}
              />
              {requestErrors.email && (
                <Typography 
                  {...getTypographyProps()} 
                  variant="small" 
                  color="red" 
                  className="mt-1"
                  id="email-error"
                >
                  {requestErrors.email.message}
                </Typography>
              )}
            </div>

            {(requestErrors.root || authError) && (
              <Typography 
                {...getTypographyProps()} 
                variant="small" 
                color="red" 
                className="text-center"
                role="alert"
              >
                {requestErrors.root?.message || authError}
              </Typography>
            )}

            <Button
              {...getButtonProps()}
              type="submit"
              fullWidth
              disabled={isRequestSubmitting}
              aria-busy={isRequestSubmitting}
            >
              {isRequestSubmitting ? "Sending..." : "Send Reset Link"}
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}; 