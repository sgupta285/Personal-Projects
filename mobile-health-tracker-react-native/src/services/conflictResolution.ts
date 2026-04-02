interface SyncCandidate {
  updatedAt: string;
  source: 'local' | 'remote';
  payload: Record<string, unknown>;
}

export function resolveLatestWrite(local: SyncCandidate, remote: SyncCandidate): SyncCandidate {
  if (local.updatedAt >= remote.updatedAt) {
    return local;
  }
  return remote;
}
