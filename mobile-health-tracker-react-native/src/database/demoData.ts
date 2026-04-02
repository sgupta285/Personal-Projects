import { Goal, MealLog, WorkoutLog } from '@/types/models';
import { createId } from '@/utils/id';
import { nowIso } from '@/utils/time';

const now = nowIso();

export const demoWorkouts: WorkoutLog[] = [
  {
    id: createId('workout'),
    type: 'Strength Training',
    durationMinutes: 50,
    caloriesBurned: 420,
    notes: 'Upper body push day',
    date: now,
    updatedAt: now,
    syncStatus: 'pending',
  },
  {
    id: createId('workout'),
    type: 'Run',
    durationMinutes: 32,
    caloriesBurned: 310,
    notes: 'Zone 2 recovery run',
    date: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: now,
    syncStatus: 'synced',
  },
];

export const demoMeals: MealLog[] = [
  {
    id: createId('meal'),
    mealType: 'breakfast',
    calories: 520,
    proteinGrams: 34,
    carbsGrams: 48,
    fatGrams: 18,
    date: now,
    updatedAt: now,
    syncStatus: 'pending',
  },
  {
    id: createId('meal'),
    mealType: 'dinner',
    calories: 740,
    proteinGrams: 46,
    carbsGrams: 65,
    fatGrams: 22,
    date: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: now,
    syncStatus: 'synced',
  },
];

export const demoGoals: Goal[] = [
  {
    id: createId('goal'),
    title: 'Weekly workouts',
    target: 5,
    unit: 'sessions',
    progress: 3,
    updatedAt: now,
    syncStatus: 'pending',
  },
  {
    id: createId('goal'),
    title: 'Daily protein',
    target: 160,
    unit: 'grams',
    progress: 124,
    updatedAt: now,
    syncStatus: 'synced',
  },
];
