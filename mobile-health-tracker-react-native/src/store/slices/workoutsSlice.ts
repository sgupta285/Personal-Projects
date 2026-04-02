import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { WorkoutLog } from '@/types/models';

interface WorkoutsState {
  items: WorkoutLog[];
}

const initialState: WorkoutsState = {
  items: [],
};

const workoutsSlice = createSlice({
  name: 'workouts',
  initialState,
  reducers: {
    setWorkouts(state, action: PayloadAction<WorkoutLog[]>) {
      state.items = action.payload.sort((a, b) => b.date.localeCompare(a.date));
    },
    upsertWorkout(state, action: PayloadAction<WorkoutLog>) {
      const index = state.items.findIndex((item) => item.id === action.payload.id);
      if (index >= 0) {
        state.items[index] = action.payload;
      } else {
        state.items.unshift(action.payload);
      }
      state.items.sort((a, b) => b.date.localeCompare(a.date));
    },
  },
});

export const { setWorkouts, upsertWorkout } = workoutsSlice.actions;
export default workoutsSlice.reducer;
