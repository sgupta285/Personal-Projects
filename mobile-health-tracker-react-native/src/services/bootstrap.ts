import { Store } from '@reduxjs/toolkit';
import { initializeDatabase, loadGoals, loadMeals, loadWorkouts, seedDemoDataIfEmpty } from '@/database/sqlite';
import { setGoals } from '@/store/slices/goalsSlice';
import { setMeals } from '@/store/slices/nutritionSlice';
import { setWorkouts } from '@/store/slices/workoutsSlice';
import { setActivitySnapshot } from '@/store/slices/activitySlice';
import { resolveHealthProvider } from './healthProviders';

export async function bootstrapApp(store: Store): Promise<void> {
  await initializeDatabase();
  if (process.env.EXPO_PUBLIC_ENABLE_DEMO_SEED !== 'false') {
    await seedDemoDataIfEmpty();
  }
  const [workouts, meals, goals] = await Promise.all([loadWorkouts(), loadMeals(), loadGoals()]);
  store.dispatch(setWorkouts(workouts));
  store.dispatch(setMeals(meals));
  store.dispatch(setGoals(goals));
  const healthProvider = resolveHealthProvider();
  const snapshot = await healthProvider.readTodaySnapshot();
  store.dispatch(setActivitySnapshot(snapshot));
}
