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

## What's intentionally not built yet

Authentication, report upload, OCR, AI explanations, chat, health timeline,
voice features, multi-language support, and the doctor visit assistant are
all out of scope for this phase — they arrive in later phases per the
project plan.
