export interface Achievement {
  code: string;
  title: string;
  description: string;
}

export function achievementsForProfile(streak: number, completedThisWeek: number, activeChallenges: number): Achievement[] {
  const achievements: Achievement[] = [];

  if (streak >= 3) {
    achievements.push({
      code: "momentum",
      title: "Momentum Starter",
      description: "Logged progress for three straight days."
    });
  }

  if (completedThisWeek >= 5) {
    achievements.push({
      code: "steady-week",
      title: "Steady Week",
      description: "Completed at least five habit check-ins this week."
    });
  }

  if (activeChallenges >= 1) {
    achievements.push({
      code: "social-spark",
      title: "Social Spark",
      description: "Joined a challenge with friends."
    });
  }

  return achievements;
}
