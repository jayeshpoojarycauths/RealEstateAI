import React from "react";
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
import log from "loglevel";

// Form schema
const registerSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  company_name: z.string().min(1, "Company name is required"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();
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
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      company_name: "",
      email: "",
      password: "",
      confirm_password: "",
    },
  });

  const onSubmit: SubmitHandler<RegisterFormData> = async (data) => {
    log.info("[Register Attempt]", { email: data.email });
    try {
      setError(null);
      await registerUser(data);
      log.info("[Register Success]", { email: data.email });
      navigate("/login");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An error occurred during registration"
      );
      log.error("[Register Error]", err);
    }
  };

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
            Create Account
          </Typography>
          <Typography
            variant="small"
            color="white"
            className="text-xs opacity-80 mt-1"
            {...(getTypographyProps() as any)}
          >
            Enter your details to register
          </Typography>
        </CardHeader>
        <CardBody className="p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Controller
                  name="first_name"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      type="text"
                      label="First Name"
                      error={!!errors.first_name}
                      aria-invalid={!!errors.first_name}
                      aria-describedby={errors.first_name ? "first-name-error" : undefined}
                      {...(getInputProps() as any)}
                    />
                  )}
                />
                {errors.first_name && (
                  <Typography
                    variant="small"
                    color="red"
                    id="first-name-error"
                    className="mt-1 animate-pulse"
                    {...(getTypographyProps() as any)}
                  >
                    {errors.first_name.message}
                  </Typography>
                )}
              </div>

              <div>
                <Controller
                  name="last_name"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      type="text"
                      label="Last Name"
                      error={!!errors.last_name}
                      aria-invalid={!!errors.last_name}
                      aria-describedby={errors.last_name ? "last-name-error" : undefined}
                      {...(getInputProps() as any)}
                    />
                  )}
                />
                {errors.last_name && (
                  <Typography
                    variant="small"
                    color="red"
                    id="last-name-error"
                    className="mt-1 animate-pulse"
                    {...(getTypographyProps() as any)}
                  >
                    {errors.last_name.message}
                  </Typography>
                )}
              </div>
            </div>

            <div>
              <Controller
                name="company_name"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="text"
                    label="Company Name"
                    error={!!errors.company_name}
                    aria-invalid={!!errors.company_name}
                    aria-describedby={errors.company_name ? "company-name-error" : undefined}
                    {...(getInputProps() as any)}
                  />
                )}
              />
              {errors.company_name && (
                <Typography
                  variant="small"
                  color="red"
                  id="company-name-error"
                  className="mt-1 animate-pulse"
                  {...(getTypographyProps() as any)}
                >
                  {errors.company_name.message}
                </Typography>
              )}
            </div>

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

            <div>
              <Controller
                name="confirm_password"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    type="password"
                    label="Confirm Password"
                    error={!!errors.confirm_password}
                    aria-invalid={!!errors.confirm_password}
                    aria-describedby={errors.confirm_password ? "confirm-password-error" : undefined}
                    {...(getInputProps() as any)}
                  />
                )}
              />
              {errors.confirm_password && (
                <Typography
                  variant="small"
                  color="red"
                  id="confirm-password-error"
                  className="mt-1 animate-pulse"
                  {...(getTypographyProps() as any)}
                >
                  {errors.confirm_password.message}
                </Typography>
              )}
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
              {isSubmitting ? "Creating Account..." : "Create Account"}
            </Button>

            <Typography
              variant="small"
              color="gray"
              className="text-center mt-4"
              {...(getTypographyProps() as any)}
            >
              Already have an account?{" "}
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