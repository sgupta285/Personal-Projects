import { Store } from '@reduxjs/toolkit';
import { queueSync } from '@/store/slices/syncSlice';
import { upsertWorkout } from '@/store/slices/workoutsSlice';
import { upsertMeal } from '@/store/slices/nutritionSlice';
import { upsertGoal } from '@/store/slices/goalsSlice';
import { saveGoal, saveMeal, saveWorkout } from '@/database/sqlite';
import { Goal, MealLog, WorkoutLog } from '@/types/models';

export async function logWorkout(store: Store, workout: WorkoutLog): Promise<void> {
  await saveWorkout(workout);
  store.dispatch(upsertWorkout(workout));
  store.dispatch(queueSync({
    id: workout.id,
    entityType: 'workout',
    action: 'upsert',
    payload: workout,
    localUpdatedAt: workout.updatedAt,
  }));
}

export async function logMeal(store: Store, meal: MealLog): Promise<void> {
  await saveMeal(meal);
  store.dispatch(upsertMeal(meal));
  store.dispatch(queueSync({
    id: meal.id,
    entityType: 'meal',
    action: 'upsert',
    payload: meal,
    localUpdatedAt: meal.updatedAt,
  }));
}

export async function logGoal(store: Store, goal: Goal): Promise<void> {
  await saveGoal(goal);
  store.dispatch(upsertGoal(goal));
  store.dispatch(queueSync({
    id: goal.id,
    entityType: 'goal',
    action: 'upsert',
    payload: goal,
    localUpdatedAt: goal.updatedAt,
  }));
}
