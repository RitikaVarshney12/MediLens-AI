import { Link, NavLink } from "react-router-dom";

import Logo from "@/components/ui/Logo";
import ProfileDropdown from "@/components/auth/ProfileDropdown";

const navItems = [{ label: "Dashboard", to: "/dashboard" }];

export default function Header() {
  return (
    <header className="sticky top-0 z-10 border-b border-surface-border bg-surface/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" aria-label="MediLens AI home">
          <Logo />
        </Link>
        <div className="flex items-center gap-2">
          <nav aria-label="Primary" className="flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-xl px-4 py-2 text-[0.95rem] font-medium transition-colors ${
                    isActive
                      ? "bg-primary-50 text-primary-600"
                      : "text-ink-soft hover:bg-surface-subtle hover:text-ink"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <ProfileDropdown />
        </div>
      </div>
    </header>
  );
}
