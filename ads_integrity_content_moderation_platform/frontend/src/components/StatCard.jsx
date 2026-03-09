export function StatCard({ label, value, accent = "slate" }) {
  return (
    <div className={`stat-card accent-${accent}`}>
      <p className="stat-label">{label}</p>
      <h2 className="stat-value">{value}</h2>
    </div>
  );
}
