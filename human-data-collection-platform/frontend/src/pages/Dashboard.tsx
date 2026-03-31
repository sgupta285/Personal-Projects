const demoMetrics = {
  openTasks: 14,
  pendingReview: 6,
  completedToday: 42,
  seedTaskAccuracy: "0.92",
};

const taskCards = [
  {
    title: "Pairwise preference queue",
    subtitle: "Designed for rapid side-by-side comparisons with hotkey support.",
  },
  {
    title: "Reviewer inbox",
    subtitle: "Shows flagged responses, anomaly warnings, and approval decisions.",
  },
  {
    title: "Admin operations",
    subtitle: "Monitors throughput, queue balance, and quality-control signals.",
  },
];

export function Dashboard() {
  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">Human Data Collection Platform</p>
          <h1>Quality-controlled annotation workflows for preference data and review operations.</h1>
          <p className="subtext">
            This frontend is intentionally lightweight in the starter repo. It shows the operator surfaces you would extend
            in production: queue intake, fast annotation, reviewer adjudication, and admin metrics.
          </p>
        </div>
      </section>

      <section className="statsGrid">
        <article className="statCard"><span>Open tasks</span><strong>{demoMetrics.openTasks}</strong></article>
        <article className="statCard"><span>Pending review</span><strong>{demoMetrics.pendingReview}</strong></article>
        <article className="statCard"><span>Completed today</span><strong>{demoMetrics.completedToday}</strong></article>
        <article className="statCard"><span>Seed accuracy</span><strong>{demoMetrics.seedTaskAccuracy}</strong></article>
      </section>

      <section className="cardGrid">
        {taskCards.map((card) => (
          <article key={card.title} className="panelCard">
            <h2>{card.title}</h2>
            <p>{card.subtitle}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
