import React from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';
import { Card } from '@/components/Card';
import { PrimaryButton } from '@/components/PrimaryButton';
import { Screen } from '@/components/Screen';
import { useAppSelector } from '@/hooks/redux';
import { logGoal } from '@/services/logging';
import { store } from '@/store';
import { createId } from '@/utils/id';
import { nowIso } from '@/utils/time';

export function GoalsScreen() {
  const goals = useAppSelector((state) => state.goals.items);

  async function handleQuickAdd() {
    const now = nowIso();
    await logGoal(store, {
      id: createId('goal'),
      title: 'Hydration target',
      target: 3,
      unit: 'liters',
      progress: 1.6,
      updatedAt: now,
      syncStatus: 'pending',
    });
    Alert.alert('Goal added', 'A demo goal was saved locally and queued for sync.');
  }

  return (
    <Screen title="Goals" subtitle="Set targets and watch progress move forward over time.">
      <PrimaryButton title="Add goal" onPress={handleQuickAdd} />
      {goals.map((goal) => (
        <Card key={goal.id}>
          <View style={styles.header}>
            <Text style={styles.title}>{goal.title}</Text>
            <Text style={styles.progress}>{Math.round((goal.progress / goal.target) * 100)}%</Text>
          </View>
          <Text style={styles.meta}>{goal.progress} / {goal.target} {goal.unit}</Text>
          <View style={styles.track}>
            <View style={[styles.fill, { width: `${Math.min(100, Math.round((goal.progress / goal.target) * 100))}%` }]} />
          </View>
          <Text style={styles.meta}>Sync state: {goal.syncStatus}</Text>
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: 17, fontWeight: '700', color: '#14213d' },
  progress: { fontSize: 14, fontWeight: '700', color: '#1d4ed8' },
  meta: { fontSize: 13, color: '#52607a' },
  track: { backgroundColor: '#e5ecf8', borderRadius: 999, height: 10, overflow: 'hidden' },
  fill: { backgroundColor: '#1d4ed8', height: '100%' },
});
