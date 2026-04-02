import { configureStore } from '@reduxjs/toolkit';
import workoutsReducer from './slices/workoutsSlice';
import nutritionReducer from './slices/nutritionSlice';
import goalsReducer from './slices/goalsSlice';
import syncReducer from './slices/syncSlice';
import activityReducer from './slices/activitySlice';

export const store = configureStore({
  reducer: {
    workouts: workoutsReducer,
    nutrition: nutritionReducer,
    goals: goalsReducer,
    sync: syncReducer,
    activity: activityReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
