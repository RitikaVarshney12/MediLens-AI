interface LogoProps {
  className?: string;
}

export default function Logo({ className = "" }: LogoProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span
        className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-emerald-500 text-white shadow-card"
        aria-hidden="true"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M12 21s-7.5-4.6-10-9.3C.5 8.1 2.3 4.5 6 4c2.2-.3 4.1.8 6 2.9C13.9 4.8 15.8 3.7 18 4c3.7.5 5.5 4.1 4 7.7C19.5 16.4 12 21 12 21z"
            stroke="white"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path d="M7 12h2.2l1.3-3 2 6 1.3-3H16" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <span className="text-lg font-bold tracking-tight text-ink">
        MediLens <span className="text-primary-500">AI</span>
      </span>
    </div>
  );
}
