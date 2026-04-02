export function normalizeDay(input: string): string {
  return input.slice(0, 10);
}

export function computeStreak(completions: string[], todayIso: string = new Date().toISOString()): number {
  const days = [...new Set(completions.map(normalizeDay))].sort().reverse();
  if (days.length === 0) {
    return 0;
  }

  let streak = 0;
  let cursor = new Date(normalizeDay(todayIso));

  for (const day of days) {
    const cursorKey = cursor.toISOString().slice(0, 10);
    const previousCursor = new Date(cursor);
    previousCursor.setUTCDate(previousCursor.getUTCDate() - 1);

    if (day === cursorKey) {
      streak += 1;
      cursor = previousCursor;
      continue;
    }

    if (streak === 0 && day === previousCursor.toISOString().slice(0, 10)) {
      streak += 1;
      cursor = new Date(previousCursor);
      cursor.setUTCDate(cursor.getUTCDate() - 1);
      continue;
    }

    if (day === cursor.toISOString().slice(0, 10)) {
      streak += 1;
      cursor.setUTCDate(cursor.getUTCDate() - 1);
      continue;
    }

    break;
  }

  return streak;
}

export function badgeForStreak(streak: number): string[] {
  const badges: string[] = [];
  if (streak >= 3) badges.push("Momentum Starter");
  if (streak >= 7) badges.push("Week Warrior");
  if (streak >= 30) badges.push("Consistency Machine");
  if (streak >= 100) badges.push("Unbreakable");
  return badges;
}
