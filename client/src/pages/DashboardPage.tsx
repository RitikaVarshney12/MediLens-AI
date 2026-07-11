import Card from "@/components/ui/Card";

const upcomingSections = [
  {
    title: "Upload a report",
    description: "Add a blood report, prescription, or lab result to get a plain-language explanation.",
  },
  {
    title: "Health timeline",
    description: "Track how your results change over time, once you've uploaded more than one report.",
  },
  {
    title: "Ask MediLens",
    description: "Ask questions about your reports in your own words.",
  },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-bold text-ink">Welcome to MediLens AI</h1>
        <p className="mt-1 text-ink-soft">
          This is your dashboard. Upload and explanation features are coming in the next phase.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {upcomingSections.map((section) => (
          <Card key={section.title} className="flex flex-col gap-2">
            <h2 className="font-semibold text-ink">{section.title}</h2>
            <p className="text-sm text-ink-soft">{section.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
