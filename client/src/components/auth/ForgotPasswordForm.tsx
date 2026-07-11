import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import TextField from "@/components/ui/TextField";
import Button from "@/components/ui/Button";
import { useToast } from "@/hooks/useToast";
import { supabase } from "@/lib/supabase";
import {
  forgotPasswordSchema,
  type ForgotPasswordFormValues,
} from "@/lib/validation/authSchemas";

export default function ForgotPasswordForm() {
  const { showToast } = useToast();
  const [sent, setSent] = useState(false);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  async function onSubmit(values: ForgotPasswordFormValues) {
    // Sent directly (rather than via useAuth().resetPassword) so the
    // recovery link can point at /reset-password instead of /login.
    const { error } = await supabase.auth.resetPasswordForEmail(values.email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });

    if (error) {
      setError("root", { message: error.message });
      showToast("error", error.message);
      return;
    }

    setSent(true);
    showToast("success", "Reset link sent. Check your inbox.");
  }

  if (sent) {
    return (
      <p className="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        If an account exists for that email, a password reset link is on its way.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">
      {errors.root && (
        <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
          {errors.root.message}
        </p>
      )}

      <TextField
        label="Email"
        type="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register("email")}
      />

      <Button type="submit" isLoading={isSubmitting} className="w-full">
        Send reset link
      </Button>
    </form>
  );
}