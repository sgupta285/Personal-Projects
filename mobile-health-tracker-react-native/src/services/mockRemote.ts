import { SyncQueueItem } from '@/types/models';

const remoteStore = new Map<string, SyncQueueItem>();

export async function pushQueueItems(queue: SyncQueueItem[]): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 250));
  for (const item of queue) {
    remoteStore.set(`${item.entityType}:${item.id}`, item);
  }
}

export function getRemoteCount(): number {
  return remoteStore.size;
}
