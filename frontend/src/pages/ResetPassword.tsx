import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Card,
  CardBody,
  Typography,
  Button,
  Input,
} from "@material-tailwind/react";
import { useAuth } from "../hooks/useAuth";
import { logger } from "../utils/logger";

const resetPasswordSchema = z.object({
  password: z.string().min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

export const ResetPassword: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useParams<{ token: string }>();
  const { resetPassword } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setError("Invalid reset token");
      return;
    }

    try {
      setError(null);
      await resetPassword(token, data.password);
      setSuccess(true);
      logger.info("Password reset successful");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while resetting your password"
      );
      logger.error("Password reset failed", err as Error);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <Card className="w-96">
          <CardBody className="flex flex-col gap-4">
            <Typography variant="h4" color="blue-gray" className="text-center mb-4">
              Invalid Reset Link
            </Typography>
            <Typography variant="paragraph" className="text-center">
              This password reset link is invalid or has expired.
              Please request a new password reset link.
            </Typography>
            <Button
              color="blue"
              variant="text"
              onClick={() => navigate("/forgot-password")}
              className="mt-4"
            >
              Request New Reset Link
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <Card className="w-96">
          <CardBody className="flex flex-col gap-4">
            <Typography variant="h4" color="blue-gray" className="text-center mb-4">
              Password Reset Successful
            </Typography>
            <Typography variant="paragraph" className="text-center">
              Your password has been reset successfully.
              You can now log in with your new password.
            </Typography>
            <Button
              color="blue"
              variant="text"
              onClick={() => navigate("/login")}
              className="mt-4"
            >
              Go to Login
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Card className="w-96">
        <CardBody className="flex flex-col gap-4">
          <Typography variant="h4" color="blue-gray" className="text-center mb-4">
            Reset Password
          </Typography>
          <Typography variant="small" color="gray" className="text-center mb-4">
            Please enter your new password below.
          </Typography>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Input
                label="New Password"
                type="password"
                {...register("password")}
                error={!!errors.password}
              />
              {errors.password && (
                <Typography variant="small" color="red" className="mt-1">
                  {errors.password.message}
                </Typography>
              )}
            </div>

            <div>
              <Input
                label="Confirm Password"
                type="password"
                {...register("confirmPassword")}
                error={!!errors.confirmPassword}
              />
              {errors.confirmPassword && (
                <Typography variant="small" color="red" className="mt-1">
                  {errors.confirmPassword.message}
                </Typography>
              )}
            </div>

            {error && (
              <Typography variant="small" color="red" className="text-center">
                {error}
              </Typography>
            )}

            <Button
              type="submit"
              color="blue"
              variant="gradient"
              fullWidth
              disabled={isSubmitting}
            >
              {isSubmitting ? "Resetting..." : "Reset Password"}
            </Button>

            <Typography variant="small" color="gray" className="text-center mt-4">
              Remember your password?{" "}
              <button
                type="button"
                onClick={() => navigate("/login")}
                className="text-blue-500 hover:text-blue-700 font-medium"
              >
                Sign In
              </button>
            </Typography>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}; 