import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { SyncQueueItem } from '@/types/models';

interface SyncState {
  queue: SyncQueueItem[];
  lastSyncedAt?: string;
  isSyncing: boolean;
  failures: number;
}

const initialState: SyncState = {
  queue: [],
  isSyncing: false,
  failures: 0,
};

const syncSlice = createSlice({
  name: 'sync',
  initialState,
  reducers: {
    queueSync(state, action: PayloadAction<SyncQueueItem>) {
      state.queue.push(action.payload);
    },
    clearSyncQueue(state) {
      state.queue = [];
    },
    setSyncing(state, action: PayloadAction<boolean>) {
      state.isSyncing = action.payload;
    },
    markSynced(state, action: PayloadAction<string>) {
      state.lastSyncedAt = action.payload;
      state.failures = 0;
      state.queue = [];
    },
    incrementFailures(state) {
      state.failures += 1;
    },
  },
});

export const { queueSync, clearSyncQueue, setSyncing, markSynced, incrementFailures } = syncSlice.actions;
export default syncSlice.reducer;
