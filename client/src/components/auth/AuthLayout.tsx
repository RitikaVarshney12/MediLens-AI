import { Link } from "react-router-dom";
import type { ReactNode } from "react";

import Logo from "@/components/ui/Logo";

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden flex-col justify-between bg-gradient-to-br from-primary-500 to-emerald-600 p-12 text-white lg:flex">
        <Link to="/" aria-label="MediLens AI home">
          <div className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M12 21s-7.5-4.6-10-9.3C.5 8.1 2.3 4.5 6 4c2.2-.3 4.1.8 6 2.9C13.9 4.8 15.8 3.7 18 4c3.7.5 5.5 4.1 4 7.7C19.5 16.4 12 21 12 21z"
                  stroke="white"
                  strokeWidth="1.6"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <span className="text-lg font-bold tracking-tight">MediLens AI</span>
          </div>
        </Link>
        <div>
          <p className="text-2xl font-semibold leading-snug">
            Every patient deserves to understand their own health.
          </p>
          <p className="mt-3 max-w-sm text-white/80">
            Sign in to translate your reports into language that actually makes sense — for
            you, your parents, or the people you care for.
          </p>
        </div>
        <p className="text-sm text-white/70">
          AI-generated explanations are educational only and never replace medical advice.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center bg-surface-subtle px-4 py-12 sm:px-6">
        <div className="mb-8 lg:hidden">
          <Link to="/" aria-label="MediLens AI home">
            <Logo />
          </Link>
        </div>
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
