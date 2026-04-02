import { Store } from '@reduxjs/toolkit';
import { incrementFailures, markSynced, setSyncing } from '@/store/slices/syncSlice';
import { pushQueueItems } from './mockRemote';

export async function runSync(store: Store): Promise<void> {
  const state = store.getState() as any;
  const queue = state.sync.queue;
  if (!queue.length) {
    return;
  }
  store.dispatch(setSyncing(true));
  try {
    await pushQueueItems(queue);
    store.dispatch(markSynced(new Date().toISOString()));
  } catch (error) {
    store.dispatch(incrementFailures());
    throw error;
  } finally {
    store.dispatch(setSyncing(false));
  }
}
