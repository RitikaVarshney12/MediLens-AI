import AuthLayout from "@/components/auth/AuthLayout";
import AuthCard from "@/components/auth/AuthCard";
import ResetPasswordForm from "@/components/auth/ResetPasswordForm";

export default function ResetPasswordPage() {
  return (
    <AuthLayout>
      <AuthCard
        title="Set a new password"
        subtitle="Choose a new password for your MediLens AI account."
      >
        <ResetPasswordForm />
      </AuthCard>
    </AuthLayout>
  );
}