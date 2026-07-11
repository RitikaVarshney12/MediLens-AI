import { Link, Navigate } from "react-router-dom";

import AuthLayout from "@/components/auth/AuthLayout";
import AuthCard from "@/components/auth/AuthCard";
import SignupForm from "@/components/auth/SignupForm";
import { useAuth } from "@/hooks/useAuth";

export default function SignupPage() {
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <AuthLayout>
      <AuthCard
        title="Create your account"
        subtitle="Understand your medical reports in language that makes sense to you."
        footer={
          <p className="text-center text-sm text-ink-soft">
            Already have an account?{" "}
            <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-700">
              Log in
            </Link>
          </p>
        }
      >
        <SignupForm />
      </AuthCard>
    </AuthLayout>
  );
}
