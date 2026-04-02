import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { ActivitySnapshot } from '@/types/models';

interface ActivityState {
  latest?: ActivitySnapshot;
}

const initialState: ActivityState = {};

const activitySlice = createSlice({
  name: 'activity',
  initialState,
  reducers: {
    setActivitySnapshot(state, action: PayloadAction<ActivitySnapshot>) {
      state.latest = action.payload;
    },
  },
});

export const { setActivitySnapshot } = activitySlice.actions;
export default activitySlice.reducer;
