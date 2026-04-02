import { resolveLatestWrite } from '@/services/conflictResolution';

describe('resolveLatestWrite', () => {
  it('keeps the latest local value when timestamps are newer', () => {
    const resolved = resolveLatestWrite(
      { source: 'local', updatedAt: '2026-04-01T10:00:00.000Z', payload: { value: 12 } },
      { source: 'remote', updatedAt: '2026-04-01T09:00:00.000Z', payload: { value: 8 } },
    );
    expect(resolved.source).toBe('local');
    expect(resolved.payload.value).toBe(12);
  });
});
