import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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

const forgotUsernameSchema = z.object({
  email: z.string().email("Invalid email address"),
});

type ForgotUsernameFormData = z.infer<typeof forgotUsernameSchema>;

export const ForgotUsername: React.FC = () => {
  const navigate = useNavigate();
  const { requestUsernameReminder } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotUsernameFormData>({
    resolver: zodResolver(forgotUsernameSchema),
  });

  const onSubmit = async (data: ForgotUsernameFormData) => {
    try {
      setError(null);
      await requestUsernameReminder(data.email);
      setSuccess(true);
      logger.info("Username reminder email sent", { email: data.email });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while requesting username reminder"
      );
      logger.error("Username reminder request failed", err as Error);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <Card className="w-96">
          <CardBody className="flex flex-col gap-4">
            <Typography variant="h4" color="blue-gray" className="text-center mb-4">
              Check Your Email
            </Typography>
            <Typography variant="paragraph" className="text-center">
              We've sent your username to your email address.
              Please check your inbox for the reminder.
            </Typography>
            <Button
              color="blue"
              variant="text"
              onClick={() => navigate("/login")}
              className="mt-4"
            >
              Back to Login
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
            Forgot Username
          </Typography>
          <Typography variant="small" color="gray" className="text-center mb-4">
            Enter your email address and we'll send you a reminder of your username.
          </Typography>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Input
                label="Email"
                type="email"
                {...register("email")}
                error={!!errors.email}
              />
              {errors.email && (
                <Typography variant="small" color="red" className="mt-1">
                  {errors.email.message}
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
              {isSubmitting ? "Sending..." : "Send Username Reminder"}
            </Button>

            <Typography variant="small" color="gray" className="text-center mt-4">
              Remember your username?{" "}
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