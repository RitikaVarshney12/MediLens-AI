import { forwardRef, useId, useState, type InputHTMLAttributes } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, hint, type = "text", id, className = "", ...rest }, ref) => {
    const generatedId = useId();
    const fieldId = id ?? generatedId;
    const errorId = `${fieldId}-error`;
    const hintId = `${fieldId}-hint`;
    const isPassword = type === "password";
    const [visible, setVisible] = useState(false);

    return (
      <div className="flex flex-col gap-1.5">
        <label htmlFor={fieldId} className="text-sm font-semibold text-ink">
          {label}
        </label>
        <div className="relative">
          <input
            ref={ref}
            id={fieldId}
            type={isPassword && visible ? "text" : type}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : hint ? hintId : undefined}
            className={`w-full rounded-xl border bg-surface px-4 py-3 text-base text-ink placeholder:text-ink-faint focus:outline-none ${
              error
                ? "border-red-300 focus:border-red-400"
                : "border-surface-border focus:border-primary-400"
            } ${isPassword ? "pr-12" : ""} ${className}`}
            {...rest}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setVisible((v) => !v)}
              aria-label={visible ? "Hide password" : "Show password"}
              aria-pressed={visible}
              className="absolute inset-y-0 right-0 flex items-center px-3 text-sm font-semibold text-ink-soft hover:text-ink"
            >
              {visible ? "Hide" : "Show"}
            </button>
          )}
        </div>
        {error ? (
          <p id={errorId} role="alert" className="text-sm text-red-600">
            {error}
          </p>
        ) : hint ? (
          <p id={hintId} className="text-sm text-ink-faint">
            {hint}
          </p>
        ) : null}
      </div>
    );
  }
);

TextField.displayName = "TextField";

export default TextField;
