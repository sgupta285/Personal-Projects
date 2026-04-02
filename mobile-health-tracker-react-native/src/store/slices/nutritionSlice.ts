import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { MealLog } from '@/types/models';

interface NutritionState {
  items: MealLog[];
}

const initialState: NutritionState = {
  items: [],
};

const nutritionSlice = createSlice({
  name: 'nutrition',
  initialState,
  reducers: {
    setMeals(state, action: PayloadAction<MealLog[]>) {
      state.items = action.payload.sort((a, b) => b.date.localeCompare(a.date));
    },
    upsertMeal(state, action: PayloadAction<MealLog>) {
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

export const { setMeals, upsertMeal } = nutritionSlice.actions;
export default nutritionSlice.reducer;
