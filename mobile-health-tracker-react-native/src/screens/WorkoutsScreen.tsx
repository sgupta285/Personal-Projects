import React from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';
import { Card } from '@/components/Card';
import { PrimaryButton } from '@/components/PrimaryButton';
import { Screen } from '@/components/Screen';
import { useAppSelector } from '@/hooks/redux';
import { logWorkout } from '@/services/logging';
import { store } from '@/store';
import { createId } from '@/utils/id';
import { humanDate, nowIso } from '@/utils/time';

export function WorkoutsScreen() {
  const workouts = useAppSelector((state) => state.workouts.items);

  async function handleQuickAdd() {
    const now = nowIso();
    await logWorkout(store, {
      id: createId('workout'),
      type: 'Cycling',
      durationMinutes: 40,
      caloriesBurned: 360,
      notes: 'Quick add from workouts tab',
      date: now,
      updatedAt: now,
      syncStatus: 'pending',
    });
    Alert.alert('Workout logged', 'A demo workout was saved locally and queued for sync.');
  }

  return (
    <Screen title="Workouts" subtitle="Log training sessions and keep a complete offline history.">
      <PrimaryButton title="Quick add workout" onPress={handleQuickAdd} />
      {workouts.map((workout) => (
        <Card key={workout.id}>
          <View style={styles.header}>
            <Text style={styles.title}>{workout.type}</Text>
            <Text style={styles.meta}>{workout.durationMinutes} min</Text>
          </View>
          <Text style={styles.meta}>{humanDate(workout.date)}</Text>
          <Text style={styles.notes}>{workout.notes ?? 'No notes recorded.'}</Text>
          <Text style={styles.meta}>Calories burned: {workout.caloriesBurned}</Text>
          <Text style={styles.meta}>Sync state: {workout.syncStatus}</Text>
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: 17, fontWeight: '700', color: '#14213d' },
  meta: { fontSize: 13, color: '#52607a' },
  notes: { fontSize: 14, color: '#1d3557', lineHeight: 20 },
});
