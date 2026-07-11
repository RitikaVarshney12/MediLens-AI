import { forwardRef, useId, type InputHTMLAttributes } from "react";

interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, id, className = "", ...rest }, ref) => {
    const generatedId = useId();
    const fieldId = id ?? generatedId;

    return (
      <div className="flex items-center gap-2">
        <input
          ref={ref}
          id={fieldId}
          type="checkbox"
          className={`h-4 w-4 rounded border-surface-border text-primary-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 ${className}`}
          {...rest}
        />
        <label htmlFor={fieldId} className="text-sm text-ink-soft">
          {label}
        </label>
      </div>
    );
  }
);

Checkbox.displayName = "Checkbox";

export default Checkbox;
