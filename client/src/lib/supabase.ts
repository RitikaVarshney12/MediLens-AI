import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  // createClient() throws synchronously if either value is missing, which
  // crashes the whole React tree to a blank white screen on every route
  // (not just /login) before anything can render. Falling back to a
  // clearly-fake placeholder keeps the app alive; auth calls will just
  // fail with a network error the UI can display, instead of a hard crash.
  console.error(
    "Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY. Copy client/.env.example to client/.env and fill in your Supabase project values — auth will not work until you do."
  );
}

/**
 * "Remember me" preference. This only decides which browser storage backs
 * the Supabase session (localStorage survives browser restarts, sessionStorage
 * doesn't) — Supabase still fully owns creating, refreshing, and clearing the
 * session itself. Nothing here reads or writes the session tokens directly.
 */
const REMEMBER_ME_KEY = "medilens-remember-me";

export function setRememberMePreference(remember: boolean) {
  localStorage.setItem(REMEMBER_ME_KEY, String(remember));
}

function getActiveStorage(): Storage {
  const remember = localStorage.getItem(REMEMBER_ME_KEY);
  return remember === "false" ? sessionStorage : localStorage;
}

const rememberAwareStorage = {
  getItem: (key: string) => getActiveStorage().getItem(key),
  setItem: (key: string, value: string) => getActiveStorage().setItem(key, value),
  removeItem: (key: string) => getActiveStorage().removeItem(key),
};

export const supabase = createClient(
  supabaseUrl || "https://placeholder.supabase.co",
  supabaseAnonKey || "placeholder-anon-key",
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
      storage: rememberAwareStorage,
    },
  }
);
