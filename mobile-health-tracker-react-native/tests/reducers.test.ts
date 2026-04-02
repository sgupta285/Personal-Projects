import workoutsReducer, { upsertWorkout } from '@/store/slices/workoutsSlice';

it('upserts a workout entry', () => {
  const result = workoutsReducer({ items: [] }, upsertWorkout({
    id: 'w1',
    type: 'Run',
    durationMinutes: 20,
    caloriesBurned: 200,
    date: '2026-04-01T00:00:00.000Z',
    updatedAt: '2026-04-01T00:00:00.000Z',
    syncStatus: 'pending',
  }));

  expect(result.items).toHaveLength(1);
  expect(result.items[0].type).toBe('Run');
});
