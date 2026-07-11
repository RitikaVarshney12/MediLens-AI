import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import TextField from "@/components/ui/TextField";
import Button from "@/components/ui/Button";
import PasswordStrengthIndicator from "@/components/auth/PasswordStrengthIndicator";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/useToast";
import { signupSchema, type SignupFormValues } from "@/lib/validation/authSchemas";

export default function SignupForm() {
  const { signUp } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: "", password: "", confirmPassword: "" },
  });

  const password = watch("password");

  async function onSubmit(values: SignupFormValues) {
    const { error } = await signUp(values.email, values.password);

    if (error) {
      setError("root", { message: error });
      showToast("error", error);
      return;
    }

    showToast("success", "Account created. Check your email to confirm it.");
    navigate("/login", { replace: true });
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

      <div className="flex flex-col gap-2">
        <TextField
          label="Password"
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <PasswordStrengthIndicator password={password} />
      </div>

      <TextField
        label="Confirm password"
        type="password"
        autoComplete="new-password"
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />

      <Button type="submit" isLoading={isSubmitting} className="w-full">
        Create account
      </Button>
    </form>
  );
}
