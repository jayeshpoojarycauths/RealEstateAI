import React from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
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
import { useMaterialTailwind } from "../../hooks/useMaterialTailwind";
import { useAuth } from "../../hooks/useAuth";

const mfaSchema = z.object({
  code: z
    .string()
    .min(1, "MFA code is required")
    .length(6, "MFA code must be 6 digits")
    .regex(/^\d+$/, "MFA code must contain only digits"),
});

type MFAFormData = z.infer<typeof mfaSchema>;

const defaultEventHandlers = {
  onResize: undefined,
  onResizeCapture: undefined,
  onPointerEnterCapture: undefined,
  onPointerLeaveCapture: undefined,
  placeholder: undefined,
  crossOrigin: undefined,
};

export const MFAVerification: React.FC = () => {
  const navigate = useNavigate();
  const { verifyMFA, error: authError } = useAuth();
  const {
    getButtonProps,
    getCardProps,
    getCardBodyProps,
    getCardHeaderProps,
    getTypographyProps,
    getInputProps,
  } = useMaterialTailwind();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<MFAFormData>({
    resolver: zodResolver<MFAFormData, any, MFAFormData>(mfaSchema),
    defaultValues: {
      code: "",
    },
  });

  const onSubmit = async (data: MFAFormData) => {
    try {
      await verifyMFA(data.code);
      navigate("/dashboard");
    } catch (err) {
      setError("root", {
        type: "manual",
        message: err instanceof Error ? err.message : "An error occurred",
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card
        {...getCardProps()}
        className="w-full max-w-md"
        {...defaultEventHandlers}
      >
        <CardHeader
          {...getCardHeaderProps()}
          className="text-center"
          {...defaultEventHandlers}
        >
          <Typography
            {...getTypographyProps()}
            variant="h4"
            color="blue-gray"
            {...defaultEventHandlers}
          >
            Two-Factor Authentication
          </Typography>
          <Typography
            {...getTypographyProps()}
            variant="small"
            color="gray"
            className="mt-1"
            {...defaultEventHandlers}
          >
            Please enter the 6-digit code from your authenticator app
          </Typography>
        </CardHeader>
        <CardBody {...getCardBodyProps()} {...defaultEventHandlers}>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Input
                {...getInputProps()}
                type="text"
                label="MFA Code"
                {...register("code")}
                error={!!errors.code}
                aria-invalid={!!errors.code}
                aria-describedby={errors.code ? "code-error" : undefined}
                maxLength={6}
                {...defaultEventHandlers}
              />
              {errors.code && (
                <Typography
                  {...getTypographyProps()}
                  variant="small"
                  color="red"
                  className="mt-1"
                  id="code-error"
                  {...defaultEventHandlers}
                >
                  {errors.code.message}
                </Typography>
              )}
            </div>

            {(errors.root || authError) && (
              <Typography
                {...getTypographyProps()}
                variant="small"
                color="red"
                className="text-center"
                role="alert"
                {...defaultEventHandlers}
              >
                {errors.root?.message || authError}
              </Typography>
            )}

            <Button
              {...getButtonProps()}
              type="submit"
              fullWidth
              disabled={isSubmitting}
              aria-busy={isSubmitting}
              {...defaultEventHandlers}
            >
              {isSubmitting ? "Verifying..." : "Verify"}
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  );
};
