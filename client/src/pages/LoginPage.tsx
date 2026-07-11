import { Link, Navigate } from "react-router-dom";

import AuthLayout from "@/components/auth/AuthLayout";
import AuthCard from "@/components/auth/AuthCard";
import LoginForm from "@/components/auth/LoginForm";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <AuthLayout>
      <AuthCard
        title="Log in"
        subtitle="Welcome back to MediLens AI."
        footer={
          <p className="text-center text-sm text-ink-soft">
            Don't have an account?{" "}
            <Link to="/signup" className="font-semibold text-primary-600 hover:text-primary-700">
              Sign up
            </Link>
          </p>
        }
      >
        <LoginForm />
      </AuthCard>
    </AuthLayout>
  );
}
