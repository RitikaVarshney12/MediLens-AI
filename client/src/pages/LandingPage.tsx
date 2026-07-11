import { Link } from "react-router-dom";

import Logo from "@/components/ui/Logo";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import DisclaimerBanner from "@/components/ui/DisclaimerBanner";

const modes = [
  { icon: "👩‍⚕️", label: "Doctor" },
  { icon: "👨", label: "Patient" },
  { icon: "👵", label: "Senior Citizen" },
  { icon: "👨‍👩‍👧", label: "Caregiver" },
  { icon: "🧒", label: "Explain Like I'm 10" },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-surface">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-6 sm:px-6">
        <Logo />
        <Link to="/dashboard">
          <Button variant="secondary">Open dashboard</Button>
        </Link>
      </header>

      <main className="flex-1">
        {/* Hero */}
        <section className="mx-auto max-w-4xl px-4 pb-16 pt-10 text-center sm:px-6">
          <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-ink sm:text-5xl">
            Making healthcare
            <br />
            <span className="text-primary-500">understandable</span> for everyone.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-lg text-ink-soft">
            MediLens AI turns confusing blood reports, lab results, and prescriptions into
            explanations every patient, senior, and caregiver can actually understand.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link to="/dashboard">
              <Button>Try the dashboard</Button>
            </Link>
          </div>
        </section>

        {/* Signature element: one real report line, translated across modes */}
        <section className="mx-auto max-w-4xl px-4 pb-20 sm:px-6">
          <Card className="overflow-hidden p-0">
            <div className="border-b border-surface-border bg-surface-subtle px-6 py-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-ink-faint">
                Same finding, explained for who's reading
              </p>
              <p className="mt-1 font-mono text-sm text-ink-soft">Elevated LDL Cholesterol</p>
            </div>
            <div className="grid gap-px bg-surface-border sm:grid-cols-2">
              <div className="bg-surface px-6 py-5">
                <p className="text-sm font-semibold text-primary-600">Patient mode</p>
                <p className="mt-1 text-ink-soft">
                  Your bad cholesterol is slightly higher than normal.
                </p>
              </div>
              <div className="bg-surface px-6 py-5">
                <p className="text-sm font-semibold text-emerald-600">Explain Like I'm 10</p>
                <p className="mt-1 text-ink-soft">
                  Imagine your blood vessels are water pipes. Too much fat can slowly stick to
                  the inside of the pipes.
                </p>
              </div>
            </div>
          </Card>
        </section>

        {/* Modes */}
        <section className="mx-auto max-w-5xl px-4 pb-20 sm:px-6">
          <h2 className="text-center text-2xl font-bold text-ink">One report, five ways to understand it</h2>
          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-5">
            {modes.map((mode) => (
              <Card key={mode.label} className="flex flex-col items-center gap-2 text-center">
                <span className="text-3xl" aria-hidden="true">
                  {mode.icon}
                </span>
                <span className="text-sm font-semibold text-ink">{mode.label}</span>
              </Card>
            ))}
          </div>
        </section>
      </main>

      <DisclaimerBanner />
    </div>
  );
}
