export function streakLabel(days: number) {
  if (days >= 30) return "Locked in";
  if (days >= 7) return "Strong week";
  if (days >= 3) return "Momentum";
  return "Getting started";
}
