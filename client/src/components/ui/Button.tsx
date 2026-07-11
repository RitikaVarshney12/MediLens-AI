import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "secondary";
}

const variantStyles = {
  primary: "bg-primary-500 text-white hover:bg-primary-600",
  secondary: "bg-surface text-ink border border-surface-border hover:bg-surface-subtle",
};

export default function Button({
  children,
  variant = "primary",
  className = "",
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-xl px-5 py-3 text-[0.95rem] font-semibold transition-colors ${variantStyles[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
