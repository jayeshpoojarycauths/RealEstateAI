import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, SubmitHandler, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Input,
} from "@material-tailwind/react";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";
import { useAuth } from "../hooks/useAuth";
import { MFAVerification } from "../components/auth/MFAVerification";
import log from "loglevel";

// Form schema
const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  rememberMe: z.boolean(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, requiresMFA } = useAuth();
  const {
    getButtonProps,
    getCardProps,
    getCardBodyProps,
    getCardHeaderProps,
    getTypographyProps,
    getInputProps,
  } = useMaterialTailwind();

  const [error, setError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    control,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      rememberMe: false,
    },
  });

  const onSubmit: SubmitHandler<LoginFormData> = async (data) => {
    log.info("[Login Attempt]", { email: data.email, rememberMe: data.rememberMe });
    try {
      setError(null);
      await login(data.email, data.password, data.rememberMe);
      log.info("[Login Success]", { email: data.email });
      if (!requiresMFA) {
        navigate("/dashboard");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An error occurred during login"
      );
      log.error("[Login Error]", err);
    }
  };

  if (requiresMFA) return <MFAVerification />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 p-4">

      <Card
        className="max-w-md w-full mx-auto shadow-xl rounded-2xl bg-white border border-blue-100 backdrop-blur-md"
        {...(getCardProps() as any)}
      >
        <CardHeader
          variant="gradient"
          color="blue"
          className="rounded-t-2xl py-6 px-4 text-center"
          {...(getCardHeaderProps() as any)}
        >
          <Typography
            variant="h4"
            color="white"
            className="font-bold"
            {...(getTypographyProps() as any)}
          >
            Real Estate AI Login
          </Typography>
          <Typography
            variant="small"
            color="white"
            className="text-xs opacity-80 mt-1"
            {...(getTypographyProps() as any)}
          >
            Enter your email and password
          </Typography>
        </CardHeader>
        <CardBody className="p-6 space-y-6" {...(getCardBodyProps() as any)}>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
            <div>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="email"
                    label="Email"
                    error={!!errors.email}
                    aria-invalid={!!errors.email}
                    aria-describedby={errors.email ? "email-error" : undefined}
                    {...(getInputProps() as any)}
                  />
                )}
              />
              {errors.email && (
                <Typography
                  variant="small"
                  color="red"
                  id="email-error"
                  className="mt-1 animate-pulse"
                  {...(getTypographyProps() as any)}
                >
                  {errors.email.message}
                </Typography>
              )}
            </div>

            <div>
              <Controller
                name="password"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="password"
                    label="Password"
                    error={!!errors.password}
                    aria-invalid={!!errors.password}
                    aria-describedby={errors.password ? "password-error" : undefined}
                    {...(getInputProps() as any)}
                  />
                )}
              />
              {errors.password && (
                <Typography
                  variant="small"
                  color="red"
                  id="password-error"
                  className="mt-1 animate-pulse"
                  {...(getTypographyProps() as any)}
                >
                  {errors.password.message}
                </Typography>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="rememberMe"
                className="w-4 h-4 text-blue-600 border-gray-300 rounded"
                {...register("rememberMe")}
              />
              <label htmlFor="rememberMe" className="text-sm text-gray-700">
                Remember me
              </label>
            </div>

            {error && (
              <Typography
                variant="small"
                color="red"
                role="alert"
                className="text-center animate-pulse"
                {...(getTypographyProps() as any)}
              >
                {error}
              </Typography>
            )}

            <Button
              type="submit"
              fullWidth
              disabled={isSubmitting}
              aria-busy={isSubmitting}
              className="font-semibold tracking-wide text-base transition-transform duration-150 ease-in-out hover:scale-105"
              {...(getButtonProps() as any)}
            >
              {isSubmitting ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  );
};
