export type HabitFrequency = "daily" | "weekly";

export interface User {
  id: string;
  name: string;
  email: string;
  timezone: string;
  notificationWindowStart: string;
  notificationWindowEnd: string;
}

export interface Habit {
  id: string;
  userId: string;
  name: string;
  category: string;
  frequency: HabitFrequency;
  targetPerPeriod: number;
  color: string;
}

export interface HabitEntry {
  id: string;
  habitId: string;
  userId: string;
  completedAt: string;
  source: "manual" | "challenge" | "backfill";
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  ownerId: string;
  habitCategory: string;
  startsOn: string;
  endsOn: string;
}
