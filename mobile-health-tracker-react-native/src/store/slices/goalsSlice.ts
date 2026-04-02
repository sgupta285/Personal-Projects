import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { Goal } from '@/types/models';

interface GoalsState {
  items: Goal[];
}

const initialState: GoalsState = {
  items: [],
};

const goalsSlice = createSlice({
  name: 'goals',
  initialState,
  reducers: {
    setGoals(state, action: PayloadAction<Goal[]>) {
      state.items = action.payload;
    },
    upsertGoal(state, action: PayloadAction<Goal>) {
      const index = state.items.findIndex((item) => item.id === action.payload.id);
      if (index >= 0) {
        state.items[index] = action.payload;
      } else {
        state.items.push(action.payload);
      }
    },
  },
});

export const { setGoals, upsertGoal } = goalsSlice.actions;
export default goalsSlice.reducer;
