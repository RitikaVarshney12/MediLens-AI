import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/useToast";

export default function ProfileDropdown() {
  const { user, signOut } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!user) return null;

  const initial = user.email?.[0]?.toUpperCase() ?? "?";

  async function handleLogout() {
    await signOut();
    showToast("success", "You've been logged out.");
    navigate("/", { replace: true });
  }

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-50 text-sm font-bold text-primary-600 hover:bg-primary-100"
      >
        {initial}
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-56 rounded-2xl border border-surface-border bg-surface p-2 shadow-card-hover"
        >
          <p className="truncate px-3 py-2 text-sm text-ink-soft">{user.email}</p>
          <button
            type="button"
            role="menuitem"
            onClick={handleLogout}
            className="w-full rounded-xl px-3 py-2 text-left text-sm font-semibold text-ink hover:bg-surface-subtle"
          >
            Log out
          </button>
        </div>
      )}
    </div>
  );
}
