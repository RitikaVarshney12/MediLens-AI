import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import TextField from "@/components/ui/TextField";
import Button from "@/components/ui/Button";
import PasswordStrengthIndicator from "@/components/auth/PasswordStrengthIndicator";
import { useToast } from "@/hooks/useToast";
import { supabase } from "@/lib/supabase";
import {
  resetPasswordSchema,
  type ResetPasswordFormValues,
} from "@/lib/validation/authSchemas";

export default function ResetPasswordForm() {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: "", confirmPassword: "" },
  });

  const password = watch("password");

  async function onSubmit(values: ResetPasswordFormValues) {
    const { error } = await supabase.auth.updateUser({ password: values.password });

    if (error) {
      setError("root", { message: error.message });
      showToast("error", error.message);
      return;
    }

    showToast("success", "Password updated. Redirecting to login…");
    setTimeout(() => {
      navigate("/login", { replace: true });
    }, 2000);
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">
      {errors.root && (
        <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
          {errors.root.message}
        </p>
      )}

      <div className="flex flex-col gap-2">
        <TextField
          label="New password"
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <PasswordStrengthIndicator password={password} />
      </div>

      <TextField
        label="Confirm new password"
        type="password"
        autoComplete="new-password"
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />

      <Button type="submit" isLoading={isSubmitting} className="w-full">
        Update password
      </Button>
    </form>
  );
}