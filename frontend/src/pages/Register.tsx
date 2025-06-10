import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, SubmitHandler, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  SafeTypography,
  SafeButton,
  SafeCard,
  SafeCardHeader,
  SafeCardBody,
  SafeInput,
} from "../components/SafeMTW";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";
import { useAuth } from "../hooks/useAuth";
import { ReCaptcha } from "../components/auth/ReCaptcha";
import { authService } from "../services/authService";
import log from "loglevel";
import { logger } from "../utils/logger";

// Form schema
const registerSchema = z
  .object({
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .max(30, "Username must be less than 30 characters")
      .regex(/^[a-zA-Z0-9_]+$/, "Username can only contain letters, numbers, and underscores"),
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
        "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
      ),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export const Register: React.FC = () => {
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

  const [error, setError] = useState<string | null>(null);
  const [verificationSent, setVerificationSent] = useState(false);

  const {
    handleSubmit,
    formState: { errors, isSubmitting },
    control,
    setValue,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      confirm_password: "",
    },
  });

  const onSubmit: SubmitHandler<RegisterFormData> = async (data) => {
    log.info("[Register Attempt]", { email: data.email });
    try {
      setError(null);
      await registerUser({
        username: data.username.trim(),
        email: data.email.trim().toLowerCase(),
        password: data.password,
        full_name: data.username, // Using username as full_name initially
      });
      log.info("[Register Success]", { email: data.email });
      setVerificationSent(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred during registration",
      );
      log.error("[Register Error]", err);
    }
  };

  const handleResendVerification = async () => {
    try {
      const email = control._formValues.email;
      await authService.resendVerificationEmail(email);
      log.info("[Resend Verification Success]", { email });
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to resend verification email",
      );
      log.error("[Resend Verification Error]", err);
    }
  };

  if (verificationSent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 p-4">
        <SafeCard className="max-w-md w-full mx-auto shadow-xl rounded-2xl bg-white border border-blue-100 backdrop-blur-md">
          <SafeCardHeader color="blue" className="mb-4">
            <SafeTypography variant="h4" color="white">
              Verify Your Email
            </SafeTypography>
          </SafeCardHeader>
          <SafeCardBody className="space-y-4">
            <SafeTypography variant="paragraph">
              We've sent a verification email to your address. Please check your
              inbox and follow the instructions to verify your account.
            </SafeTypography>
            <div className="flex flex-col gap-4">
              <SafeButton
                onClick={handleResendVerification}
                variant="outlined"
                color="blue"
              >
                Resend Verification Email
              </SafeButton>
              <SafeButton
                onClick={() => navigate("/login")}
                variant="text"
                color="blue"
              >
                Back to Login
              </SafeButton>
            </div>
            {error && (
              <SafeTypography
                variant="small"
                color="red"
                className="text-center"
              >
                {error}
              </SafeTypography>
            )}
          </SafeCardBody>
        </SafeCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 p-4">
      <SafeCard className="max-w-md w-full mx-auto shadow-xl rounded-2xl bg-white border border-blue-100 backdrop-blur-md">
        <SafeCardHeader color="blue" className="mb-4">
          <SafeTypography variant="h4" color="white">
            Create Account
          </SafeTypography>
          <SafeTypography
            variant="small"
            color="white"
            className="text-xs opacity-80 mt-1"
          >
            Enter your details to register
          </SafeTypography>
        </SafeCardHeader>
        <SafeCardBody>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="flex flex-col gap-5"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Controller
                  name="username"
                  control={control}
                  render={({ field: { onChange, value } }) => (
                    <SafeInput
                      label="Username"
                      value={value}
                      onChange={onChange}
                      error={!!errors.username}
                      {...getInputProps()}
                    />
                  )}
                />
                {errors.username && (
                  <SafeTypography
                    variant="small"
                    color="red"
                    className="mt-1"
                  >
                    {errors.username.message}
                  </SafeTypography>
                )}
              </div>
              <div>
                <Controller
                  name="email"
                  control={control}
                  render={({ field: { onChange, value } }) => (
                    <SafeInput
                      label="Email"
                      type="email"
                      value={value}
                      onChange={onChange}
                      error={!!errors.email}
                      {...getInputProps()}
                    />
                  )}
                />
                {errors.email && (
                  <SafeTypography
                    variant="small"
                    color="red"
                    className="mt-1"
                  >
                    {errors.email.message}
                  </SafeTypography>
                )}
              </div>
            </div>

            <div>
              <Controller
                name="password"
                control={control}
                render={({ field: { onChange, value } }) => (
                  <SafeInput
                    label="Password"
                    type="password"
                    value={value}
                    onChange={onChange}
                    error={!!errors.password}
                    {...getInputProps()}
                  />
                )}
              />
              {errors.password && (
                <SafeTypography
                  variant="small"
                  color="red"
                  className="mt-1"
                >
                  {errors.password.message}
                </SafeTypography>
              )}
            </div>

            <div>
              <Controller
                name="confirm_password"
                control={control}
                render={({ field: { onChange, value } }) => (
                  <SafeInput
                    label="Confirm Password"
                    type="password"
                    value={value}
                    onChange={onChange}
                    error={!!errors.confirm_password}
                    {...getInputProps()}
                  />
                )}
              />
              {errors.confirm_password && (
                <SafeTypography
                  variant="small"
                  color="red"
                  className="mt-1"
                >
                  {errors.confirm_password.message}
                </SafeTypography>
              )}
            </div>

            <SafeButton
              type="submit"
              color="blue"
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? "Creating Account..." : "Create Account"}
            </SafeButton>

            {error && (
              <SafeTypography
                variant="small"
                color="red"
                className="text-center"
              >
                {error}
              </SafeTypography>
            )}

            <div className="text-center">
              <SafeTypography variant="small" color="blue-gray">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => navigate("/login")}
                  className="text-blue-500 hover:text-blue-700"
                >
                  Sign In
                </button>
              </SafeTypography>
            </div>
          </form>
        </SafeCardBody>
      </SafeCard>
    </div>
  );
};
