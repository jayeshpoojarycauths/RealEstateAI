import React from "react";
import ReCAPTCHA from "react-google-recaptcha";

interface ReCaptchaProps {
  onChange: (token: string | null) => void;
  error?: string;
}

export const ReCaptcha: React.FC<ReCaptchaProps> = ({ onChange, error }) => {
  const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY;

  if (!siteKey) {
    console.error("ReCAPTCHA site key is not configured");
    return null;
  }

  return (
    <div className="flex flex-col items-center">
      <ReCAPTCHA
        sitekey={siteKey}
        onChange={onChange}
        theme="light"
        size="normal"
      />
      {error && <span className="text-red-500 text-sm mt-1">{error}</span>}
    </div>
  );
};
