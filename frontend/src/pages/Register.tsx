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
  SafeSelect,
  SafeOption,
} from "../../components/SafeMTW";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";
import { useAuth } from "../hooks/useAuth";
import { ReCaptcha } from "../components/auth/ReCaptcha";
import { authService } from "../services/authService";
import log from "loglevel";

// Form schema
const registerSchema = z
  .object({
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
    company_name: z.string().min(1, "Company name is required"),
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(
        /(?=.*[a-z])/,
        "Password must contain at least one lowercase letter",
      )
      .regex(
        /(?=.*[A-Z])/,
        "Password must contain at least one uppercase letter",
      )
      .regex(/(?=.*\d)/, "Password must contain at least one number")
      .regex(
        /(?=.*[@$!%*?&])/,
        "Password must contain at least one special character",
      ),
    confirm_password: z.string(),
    recaptcha_token: z.string().min(1, "Please complete the CAPTCHA"),
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
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    control,
    setValue,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      company_name: "",
      email: "",
      password: "",
      confirm_password: "",
      recaptcha_token: "",
    },
  });

  const onSubmit: SubmitHandler<RegisterFormData> = async (data) => {
    log.info("[Register Attempt]", { email: data.email });
    try {
      setError(null);
      // Sanitize input data
      const sanitizedData = {
        ...data,
        first_name: data.first_name.trim(),
        last_name: data.last_name.trim(),
        company_name: data.company_name.trim(),
        email: data.email.trim().toLowerCase(),
      };
      await registerUser(sanitizedData);
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
                  name="first_name"
                  control={control}
                  render={({ field }) => (
                    <SafeInput
                      {...field}
                      type="text"
                      label="First Name"
                      error={!!errors.first_name}
                      aria-invalid={!!errors.first_name}
                      aria-describedby={
                        errors.first_name ? "first-name-error" : undefined
                      }
                    />
                  )}
                />
                {errors.first_name && (
                  <SafeTypography
                    variant="small"
                    color="red"
                    id="first-name-error"
                    className="mt-1 animate-pulse"
                  >
                    {errors.first_name.message}
                  </SafeTypography>
                )}
              </div>

              <div>
                <Controller
                  name="last_name"
                  control={control}
                  render={({ field }) => (
                    <SafeInput
                      {...field}
                      type="text"
                      label="Last Name"
                      error={!!errors.last_name}
                      aria-invalid={!!errors.last_name}
                      aria-describedby={
                        errors.last_name ? "last-name-error" : undefined
                      }
                    />
                  )}
                />
                {errors.last_name && (
                  <SafeTypography
                    variant="small"
                    color="red"
                    id="last-name-error"
                    className="mt-1 animate-pulse"
                  >
                    {errors.last_name.message}
                  </SafeTypography>
                )}
              </div>
            </div>

            <div>
              <Controller
                name="company_name"
                control={control}
                render={({ field }) => (
                  <SafeInput
                    {...field}
                    type="text"
                    label="Company Name"
                    error={!!errors.company_name}
                    aria-invalid={!!errors.company_name}
                    aria-describedby={
                      errors.company_name ? "company-name-error" : undefined
                    }
                  />
                )}
              />
              {errors.company_name && (
                <SafeTypography
                  variant="small"
                  color="red"
                  id="company-name-error"
                  className="mt-1 animate-pulse"
                >
                  {errors.company_name.message}
                </SafeTypography>
              )}
            </div>

            <div>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <SafeInput
                    {...field}
                    type="email"
                    label="Email"
                    error={!!errors.email}
                    aria-invalid={!!errors.email}
                    aria-describedby={errors.email ? "email-error" : undefined}
                  />
                )}
              />
              {errors.email && (
                <SafeTypography
                  variant="small"
                  color="red"
                  id="email-error"
                  className="mt-1 animate-pulse"
                >
                  {errors.email.message}
                </SafeTypography>
              )}
            </div>

            <div>
              <Controller
                name="password"
                control={control}
                render={({ field }) => (
                  <SafeInput
                    {...field}
                    type="password"
                    label="Password"
                    error={!!errors.password}
                    aria-invalid={!!errors.password}
                    aria-describedby={
                      errors.password ? "password-error" : undefined
                    }
                  />
                )}
              />
              {errors.password && (
                <SafeTypography
                  variant="small"
                  color="red"
                  id="password-error"
                  className="mt-1 animate-pulse"
                >
                  {errors.password.message}
                </SafeTypography>
              )}
            </div>

            <div>
              <Controller
                name="confirm_password"
                control={control}
                render={({ field }) => (
                  <SafeInput
                    {...field}
                    type="password"
                    label="Confirm Password"
                    error={!!errors.confirm_password}
                    aria-invalid={!!errors.confirm_password}
                    aria-describedby={
                      errors.confirm_password
                        ? "confirm-password-error"
                        : undefined
                    }
                  />
                )}
              />
              {errors.confirm_password && (
                <SafeTypography
                  variant="small"
                  color="red"
                  id="confirm-password-error"
                  className="mt-1 animate-pulse"
                >
                  {errors.confirm_password.message}
                </SafeTypography>
              )}
            </div>

            <div>
              <Controller
                name="recaptcha_token"
                control={control}
                render={({ field }) => (
                  <ReCaptcha
                    onChange={(token) => {
                      setValue("recaptcha_token", token || "");
                    }}
                    error={errors.recaptcha_token?.message}
                  />
                )}
              />
            </div>

            {error && (
              <SafeTypography
                variant="small"
                color="red"
                role="alert"
                className="text-center animate-pulse"
              >
                {error}
              </SafeTypography>
            )}

            <SafeButton
              type="submit"
              fullWidth
              disabled={isSubmitting}
              aria-busy={isSubmitting}
              className="font-semibold tracking-wide text-base transition-transform duration-150 ease-in-out hover:scale-105"
            >
              {isSubmitting ? "Creating Account..." : "Create Account"}
            </SafeButton>

            <SafeTypography
              variant="small"
              color="gray"
              className="text-center mt-4"
            >
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => navigate("/login")}
                className="text-blue-500 hover:text-blue-700 font-medium"
              >
                Sign In
              </button>
            </SafeTypography>
          </form>
        </SafeCardBody>
      </SafeCard>
    </div>
  );
};
