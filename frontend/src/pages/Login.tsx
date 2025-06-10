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

const loginSchema = z.object({
  username_or_email: z.string().min(1, "Username or email is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      await login(data);
      logger.info("Login successful");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred during login"
      );
      logger.error("Login failed", err as Error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Card className="w-96">
        <CardBody className="flex flex-col gap-4">
          <Typography variant="h4" color="blue-gray" className="text-center mb-4">
            Sign In
          </Typography>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Input
                label="Username or Email"
                type="text"
                {...register("username_or_email")}
                error={!!errors.username_or_email}
              />
              {errors.username_or_email && (
                <Typography variant="small" color="red" className="mt-1">
                  {errors.username_or_email.message}
                </Typography>
              )}
            </div>

            <div>
              <Input
                label="Password"
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
              {isSubmitting ? "Signing in..." : "Sign In"}
            </Button>

            <div className="flex flex-col gap-2">
              <Typography variant="small" color="gray" className="text-center">
                <button
                  type="button"
                  onClick={() => navigate("/forgot-password")}
                  className="text-blue-500 hover:text-blue-700 font-medium"
                >
                  Forgot Password?
                </button>
              </Typography>
              <Typography variant="small" color="gray" className="text-center">
                <button
                  type="button"
                  onClick={() => navigate("/forgot-username")}
                  className="text-blue-500 hover:text-blue-700 font-medium"
                >
                  Forgot Username?
                </button>
              </Typography>
              <Typography variant="small" color="gray" className="text-center mt-2">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => navigate("/register")}
                  className="text-blue-500 hover:text-blue-700 font-medium"
                >
                  Sign Up
                </button>
              </Typography>
            </div>
          </form>
        </CardBody>
      </Card>
    </div>
  );
};
