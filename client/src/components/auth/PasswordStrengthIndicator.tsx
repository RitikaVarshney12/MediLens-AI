import { getPasswordStrength, getPasswordStrengthLabel } from "@/lib/validation/passwordStrength";

interface PasswordStrengthIndicatorProps {
  password: string;
}

const BAR_COLORS: Record<string, string> = {
  weak: "bg-red-400",
  fair: "bg-amber-400",
  good: "bg-primary-400",
  strong: "bg-emerald-500",
};

const FILLED_BARS: Record<string, number> = {
  empty: 0,
  weak: 1,
  fair: 2,
  good: 3,
  strong: 4,
};

export default function PasswordStrengthIndicator({ password }: PasswordStrengthIndicatorProps) {
  const strength = getPasswordStrength(password);
  if (strength === "empty") return null;

  const filled = FILLED_BARS[strength];
  const label = getPasswordStrengthLabel(strength);

  return (
    <div className="flex items-center gap-2" aria-live="polite">
      <div className="flex flex-1 gap-1" aria-hidden="true">
        {[0, 1, 2, 3].map((index) => (
          <span
            key={index}
            className={`h-1.5 flex-1 rounded-full ${
              index < filled ? BAR_COLORS[strength] : "bg-surface-border"
            }`}
          />
        ))}
      </div>
      <span className="text-xs font-medium text-ink-soft">{label}</span>
    </div>
  );
}
