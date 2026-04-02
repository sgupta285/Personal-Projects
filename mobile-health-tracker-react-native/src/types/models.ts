export type SyncStatus = 'pending' | 'synced' | 'failed';

export interface WorkoutLog {
  id: string;
  type: string;
  durationMinutes: number;
  caloriesBurned: number;
  notes?: string;
  date: string;
  updatedAt: string;
  syncStatus: SyncStatus;
}

export interface MealLog {
  id: string;
  mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  calories: number;
  proteinGrams: number;
  carbsGrams: number;
  fatGrams: number;
  date: string;
  updatedAt: string;
  syncStatus: SyncStatus;
}

export interface Goal {
  id: string;
  title: string;
  target: number;
  unit: string;
  progress: number;
  deadline?: string;
  updatedAt: string;
  syncStatus: SyncStatus;
}

export interface ActivitySnapshot {
  steps: number;
  activeMinutes: number;
  restingHeartRate?: number;
  source: 'demo' | 'healthkit' | 'google_fit';
  capturedAt: string;
}

export interface SyncQueueItem {
  id: string;
  entityType: 'workout' | 'meal' | 'goal';
  action: 'upsert' | 'delete';
  payload: Record<string, unknown>;
  localUpdatedAt: string;
}
