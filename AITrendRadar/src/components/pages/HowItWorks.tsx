import { StepCard } from "../StepCard";
import { Database, TrendingUp, GitBranch, BarChart3, Target, Bell } from "lucide-react";

export function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "Ingest from Official APIs",
      description: "Pull ToS-compliant public signals from Reddit, X, Instagram Graph API, TikTok developer surfaces, and licensed blog/news feeds.",
      icon: Database,
    },
    {
      number: "2",
      title: "Detect Spikes (STL + z-score)",
      description: "Apply Seasonal-Trend decomposition and statistical z-scoring to identify unusual engagement patterns that signal emerging trends.",
      icon: TrendingUp,
    },
    {
      number: "3",
      title: "Cluster Topics (e5 + HDBSCAN)",
      description: "Use e5 embeddings and HDBSCAN density-based clustering to automatically group related signals into coherent topic clusters.",
      icon: GitBranch,
    },
    {
      number: "4",
      title: "Forecast Lifecycle (FSM)",
      description: "Track each trend through a Finite State Machine: emerging → rising → peaking → declining → dead, with transition probabilities.",
      icon: BarChart3,
    },
    {
      number: "5",
      title: "Recommend Channels & Timing",
      description: "Generate marketer-friendly recommendations: what to post, where to post it, and when—optimized for each lifecycle stage.",
      icon: Target,
    },
    {
      number: "6",
      title: "Alert Rules & Notifications",
      description: "Configure custom alert rules to notify your team when specific trends hit emerging, rising, or peaking stages via email or webhooks.",
      icon: Bell,
    },
  ];

  return (
    <div className="flex-1">
      <section className="max-w-[1200px] mx-auto px-6 lg:px-8 py-20">
        <div className="max-w-[800px] mx-auto text-center mb-16">
          <h1 className="mb-6">How It Works</h1>
          <p className="text-xl text-muted-foreground">
            Our six-step pipeline transforms raw social signals into actionable trend intelligence
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-[1000px] mx-auto">
          {steps.map((step) => (
            <StepCard
              key={step.number}
              number={step.number}
              title={step.title}
              description={step.description}
              icon={step.icon}
            />
          ))}
        </div>

        <div className="mt-16 p-8 bg-muted/30 rounded-lg max-w-[800px] mx-auto">
          <h3 className="mb-4">Technical Architecture</h3>
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>
              <strong className="text-foreground">Data Layer:</strong> Official API ingestion → ETL with Polars/DuckDB → feature store/warehouse
            </p>
            <p>
              <strong className="text-foreground">Models:</strong> Spike detection (STL decomposition + z-score), topic clustering (e5 embeddings + HDBSCAN), lifecycle FSM
            </p>
            <p>
              <strong className="text-foreground">Backend:</strong> FastAPI powers REST endpoints for queries, alerts, and recommendations
            </p>
            <p>
              <strong className="text-foreground">Frontend:</strong> Next.js UI displays timelines, cluster graphs, influencer networks, and alert dashboards
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}