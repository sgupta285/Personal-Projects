import * as SQLite from 'expo-sqlite';
import { Goal, MealLog, WorkoutLog } from '@/types/models';
import { demoGoals, demoMeals, demoWorkouts } from './demoData';

let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;

async function getDb(): Promise<SQLite.SQLiteDatabase> {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync('pulse-log.db');
  }
  return dbPromise;
}

export async function initializeDatabase(): Promise<void> {
  const db = await getDb();
  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS workouts (
      id TEXT PRIMARY KEY NOT NULL,
      type TEXT NOT NULL,
      duration_minutes INTEGER NOT NULL,
      calories_burned INTEGER NOT NULL,
      notes TEXT,
      date TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      sync_status TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS meals (
      id TEXT PRIMARY KEY NOT NULL,
      meal_type TEXT NOT NULL,
      calories INTEGER NOT NULL,
      protein_grams INTEGER NOT NULL,
      carbs_grams INTEGER NOT NULL,
      fat_grams INTEGER NOT NULL,
      date TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      sync_status TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS goals (
      id TEXT PRIMARY KEY NOT NULL,
      title TEXT NOT NULL,
      target REAL NOT NULL,
      unit TEXT NOT NULL,
      progress REAL NOT NULL,
      deadline TEXT,
      updated_at TEXT NOT NULL,
      sync_status TEXT NOT NULL
    );
  `);
}

export async function seedDemoDataIfEmpty(): Promise<void> {
  const db = await getDb();
  const count = await db.getFirstAsync<{ count: number }>('SELECT COUNT(*) as count FROM workouts');
  if ((count?.count ?? 0) > 0) {
    return;
  }

  for (const workout of demoWorkouts) {
    await saveWorkout(workout);
  }
  for (const meal of demoMeals) {
    await saveMeal(meal);
  }
  for (const goal of demoGoals) {
    await saveGoal(goal);
  }
}

export async function loadWorkouts(): Promise<WorkoutLog[]> {
  const db = await getDb();
  const rows = await db.getAllAsync<any>('SELECT * FROM workouts ORDER BY date DESC');
  return rows.map((row) => ({
    id: row.id,
    type: row.type,
    durationMinutes: row.duration_minutes,
    caloriesBurned: row.calories_burned,
    notes: row.notes ?? undefined,
    date: row.date,
    updatedAt: row.updated_at,
    syncStatus: row.sync_status,
  }));
}

export async function saveWorkout(workout: WorkoutLog): Promise<void> {
  const db = await getDb();
  await db.runAsync(
    `INSERT OR REPLACE INTO workouts (id, type, duration_minutes, calories_burned, notes, date, updated_at, sync_status)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [workout.id, workout.type, workout.durationMinutes, workout.caloriesBurned, workout.notes ?? null, workout.date, workout.updatedAt, workout.syncStatus],
  );
}

export async function loadMeals(): Promise<MealLog[]> {
  const db = await getDb();
  const rows = await db.getAllAsync<any>('SELECT * FROM meals ORDER BY date DESC');
  return rows.map((row) => ({
    id: row.id,
    mealType: row.meal_type,
    calories: row.calories,
    proteinGrams: row.protein_grams,
    carbsGrams: row.carbs_grams,
    fatGrams: row.fat_grams,
    date: row.date,
    updatedAt: row.updated_at,
    syncStatus: row.sync_status,
  }));
}

export async function saveMeal(meal: MealLog): Promise<void> {
  const db = await getDb();
  await db.runAsync(
    `INSERT OR REPLACE INTO meals (id, meal_type, calories, protein_grams, carbs_grams, fat_grams, date, updated_at, sync_status)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [meal.id, meal.mealType, meal.calories, meal.proteinGrams, meal.carbsGrams, meal.fatGrams, meal.date, meal.updatedAt, meal.syncStatus],
  );
}

export async function loadGoals(): Promise<Goal[]> {
  const db = await getDb();
  const rows = await db.getAllAsync<any>('SELECT * FROM goals ORDER BY title ASC');
  return rows.map((row) => ({
    id: row.id,
    title: row.title,
    target: row.target,
    unit: row.unit,
    progress: row.progress,
    deadline: row.deadline ?? undefined,
    updatedAt: row.updated_at,
    syncStatus: row.sync_status,
  }));
}

export async function saveGoal(goal: Goal): Promise<void> {
  const db = await getDb();
  await db.runAsync(
    `INSERT OR REPLACE INTO goals (id, title, target, unit, progress, deadline, updated_at, sync_status)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [goal.id, goal.title, goal.target, goal.unit, goal.progress, goal.deadline ?? null, goal.updatedAt, goal.syncStatus],
  );
}
