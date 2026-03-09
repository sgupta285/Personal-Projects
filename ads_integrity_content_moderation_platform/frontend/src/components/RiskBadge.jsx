export function RiskBadge({ score }) {
  const numeric = Number(score || 0);
  let cls = "risk-low";
  if (numeric >= 0.85) cls = "risk-high";
  else if (numeric >= 0.55) cls = "risk-medium";

  return <span className={`risk-badge ${cls}`}>{numeric.toFixed(2)}</span>;
}
