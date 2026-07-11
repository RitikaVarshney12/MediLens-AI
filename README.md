# MediLens AI

**Making Healthcare Understandable for Everyone.**

MediLens AI is an AI-powered health literacy platform. It is not a diagnosis
tool — it translates complex medical reports (blood reports, lab results,
prescriptions) into simple, personalized explanations for the person reading
them, adapting tone and vocabulary to who they are: patient, senior citizen,
caregiver, or a 10-year-old hearing about it for the first time.

> AI-generated explanations are for educational purposes only and do not
> replace professional medical advice.

This is **Phase 1**: project architecture, folder structure, and basic
frontend/backend scaffolding only. No authentication or AI features are
implemented yet.

---

## Monorepo structure

```
medilens-ai/
├── client/                  React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/      Header, Layout (shared app chrome)
│   │   │   └── ui/          Logo, Card, Button, DisclaimerBanner
│   │   ├── pages/           LandingPage, DashboardPage
│   │   ├── routes/          AppRoutes (React Router route table)
│   │   ├── hooks/           (reserved for Phase 2+)
│   │   ├── services/        apiClient (Axios instance)
│   │   ├── types/           (reserved for Phase 2+)
│   │   └── styles/          Tailwind global stylesheet
│   ├── index.html
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
│
├── server/                  FastAPI backend
│   ├── app/
│   │   ├── main.py          App instance, CORS, health route
│   │   ├── core/config.py   Environment-driven settings
│   │   ├── api/              (reserved for Phase 2+ routers)
│   │   ├── models/           (reserved for Phase 4+ SQLAlchemy models)
│   │   ├── schemas/          (reserved for Phase 2+ Pydantic schemas)
│   │   └── services/         (reserved for Phase 5+ AI/OCR services)
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

**Why the empty `api/`, `models/`, `schemas/`, `services/`, `hooks/`, and
`types/` folders exist:** they establish the service-layer architecture the
project will follow (clean separation between routing, data, and business
logic) so later phases add files into a structure that's already agreed on,
rather than restructuring mid-project.

---

## Tech stack

| Layer | Choices |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Axios |
| Backend | FastAPI, Python, SQLAlchemy, Alembic, PostgreSQL |
| Auth (Phase 2+) | JWT, bcrypt |
| AI (Phase 5+) | Gemini API |
| OCR (Phase 4+) | EasyOCR |
| Speech (Phase 8+) | Whisper |
| Charts (Phase 7+) | Recharts |
| Database / Storage | Supabase PostgreSQL, Supabase Storage |

---

## Running the project

### Frontend (`client/`)

```bash
cd client
npm install
cp .env.example .env
npm run dev
```

Runs at `http://localhost:5173`. Renders the landing page at `/` and a
dashboard shell at `/dashboard`.

### Backend (`server/`)

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Runs at `http://localhost:8000`. Verify with:

- `GET /` → `{"project": "MediLens AI", "status": "ok"}`
- `GET /health` → `{"status": "healthy"}`

Interactive API docs are auto-generated at `http://localhost:8000/docs`.

---

## Environment variables

Both `client/.env.example` and `server/.env.example` list what's needed.
For Phase 1, only these matter:

- `client/.env`: `VITE_API_BASE_URL` (defaults to `http://localhost:8000`)
- `server/.env`: none are required yet — `ENVIRONMENT` alone is enough to
  boot the app. `DATABASE_URL`, `SUPABASE_URL`/`SUPABASE_KEY`,
  `JWT_SECRET_KEY`, and `GEMINI_API_KEY` are placeholders for later phases
  (auth, database, and AI respectively) and aren't read yet.

---

## What's built in Phase 1

- Monorepo structure (`client/`, `server/`) with the service-layer folders
  each phase will fill in
- Vite + React + TypeScript frontend, strict TS config, path alias (`@/`)
- Tailwind CSS configured with the project's design tokens (medical blue,
  emerald, rounded cards, soft shadows — Apple Health–inspired)
- React Router wired with two routes: `/` (landing) and `/dashboard`
  (shell, inside the shared `Layout`)
- Reusable UI primitives: `Logo`, `Card`, `Button`, `DisclaimerBanner`
- FastAPI backend with CORS configured for the Vite dev server, a root
  route, and a `/health` check
- Environment variable scaffolding for both apps

## What's intentionally not built yet (as of Phase 1)

Authentication, report upload, OCR, AI explanations, chat, health timeline,
voice features, multi-language support, and the doctor visit assistant are
all out of scope for this phase — they arrive in later phases per the
project plan.

---

## Phase 2 — Authentication (Supabase Auth)

Adds complete authentication using Supabase Auth. No backend auth endpoints
were added — the FastAPI server from Phase 1 is untouched; Supabase handles
signup, login, session storage, refresh, and logout directly from the
frontend via the official `@supabase/supabase-js` SDK.

### New frontend structure

```
client/src/
├── lib/
│   ├── supabase.ts                  Supabase client + remember-me storage adapter
│   └── validation/
│       ├── authSchemas.ts           Zod schemas: login, signup, forgot password
│       └── passwordStrength.ts      Password strength scoring utility
├── types/auth.ts                    AuthContextValue / AuthResult types
├── contexts/
│   ├── AuthContext.tsx              Supabase session state + auth actions
│   └── ToastContext.tsx             Success/error toast queue
├── hooks/
│   ├── useAuth.ts
│   └── useToast.ts
├── components/
│   ├── auth/
│   │   ├── AuthLayout.tsx           Split-panel layout for all auth pages
│   │   ├── AuthCard.tsx             Card wrapper (title/subtitle/footer)
│   │   ├── LoginForm.tsx
│   │   ├── SignupForm.tsx
│   │   ├── ForgotPasswordForm.tsx
│   │   ├── ProtectedRoute.tsx       Redirects to /login when signed out
│   │   ├── ProfileDropdown.tsx      Avatar menu with email + logout
│   │   └── PasswordStrengthIndicator.tsx
│   └── ui/
│       ├── TextField.tsx            Label + error + password show/hide toggle
│       ├── Checkbox.tsx             Used for "Remember me"
│       └── ToastViewport.tsx        Renders active toasts
└── pages/
    ├── LoginPage.tsx
    ├── SignupPage.tsx
    └── ForgotPasswordPage.tsx
```

`Button.tsx` (from Phase 1) was extended in place with an `isLoading` prop
instead of creating a second button component.

### Routes

- `/login`, `/signup`, `/forgot-password` — public; redirect to `/dashboard`
  automatically if already signed in
- `/dashboard` — now wrapped in `ProtectedRoute`; redirects to `/login` if
  signed out, and sends the user back to where they came from after login

### Environment variables

`client/.env.example` now also lists:

```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

Find both in your Supabase project under **Project Settings → API**.

### Creating a Supabase project

1. Go to [supabase.com](https://supabase.com) and create a free account.
2. Click **New project**, choose an organization, name it (e.g.
   `medilens-ai`), set a database password, and pick a region close to you.
3. Once it's provisioned, open **Project Settings → API**. Copy the
   **Project URL** into `VITE_SUPABASE_URL` and the **anon public** key into
   `VITE_SUPABASE_ANON_KEY` in `client/.env`.
4. Email confirmation is on by default. For faster local testing, you can
   turn it off under **Authentication → Providers → Email → Confirm email**
   — just remember to turn it back on before shipping.

### Testing signup / login locally

```bash
cd client
npm install
cp .env.example .env   # fill in the two Supabase values above
npm run dev
```

1. Visit `http://localhost:5173`, click **Sign up**, and create an account.
2. If email confirmation is on, check the inbox for that address and click
   the confirmation link (Supabase sends this automatically — no email
   provider setup needed for local dev).
3. Go to `/login` and sign in. You should land on `/dashboard`, with your
   email initial showing as an avatar in the header.
4. Try **Forgot password** from the login page — Supabase emails a reset
   link that lands back on `/login`.
5. Click the avatar → **Log out**, then try visiting `/dashboard` directly —
   it should bounce you to `/login`.
6. Uncheck **Remember me** before logging in, then close and reopen the
   browser tab — the session won't persist. With it checked, it will.

### What's intentionally not built in Phase 2

OCR, AI report explanations, uploads, and dashboard functionality are still
out of scope — Phase 2 is authentication only.

One gap worth knowing about: `ForgotPasswordForm` sends the reset email
correctly, and Supabase's link redirects the user back to `/login` with a
temporary recovery session. But there's no "set your new password" form yet
to actually complete the reset — that page wasn't in the requested file
list (`LoginPage`, `SignupPage`, `ForgotPasswordPage` only). Right now a
user who clicks the email link lands on `/login` without a way to enter a
new password. If you want that closed, it just needs one more page (e.g.
`ResetPasswordPage.tsx`) that calls `supabase.auth.updateUser({ password })`
— flag it and I'll add it as its own phase or a Phase 2 follow-up.
