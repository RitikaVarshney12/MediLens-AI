import { Link, Navigate } from "react-router-dom";

import AuthLayout from "@/components/auth/AuthLayout";
import AuthCard from "@/components/auth/AuthCard";
import ForgotPasswordForm from "@/components/auth/ForgotPasswordForm";
import { useAuth } from "@/hooks/useAuth";

export default function ForgotPasswordPage() {
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <AuthLayout>
      <AuthCard
        title="Reset your password"
        subtitle="Enter your email and we'll send you a link to reset your password."
        footer={
          <p className="text-center text-sm text-ink-soft">
            Remembered it after all?{" "}
            <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-700">
              Back to log in
            </Link>
          </p>
        }
      >
        <ForgotPasswordForm />
      </AuthCard>
    </AuthLayout>
  );
}
