import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Card } from '@/components/Card';
import { MetricPill } from '@/components/MetricPill';
import { Screen } from '@/components/Screen';
import { useAppSelector } from '@/hooks/redux';

export function DashboardScreen() {
  const workouts = useAppSelector((state) => state.workouts.items);
  const meals = useAppSelector((state) => state.nutrition.items);
  const goals = useAppSelector((state) => state.goals.items);
  const activity = useAppSelector((state) => state.activity.latest);
  const sync = useAppSelector((state) => state.sync);

  const totalCaloriesBurned = workouts.reduce((sum, item) => sum + item.caloriesBurned, 0);
  const totalCaloriesConsumed = meals.reduce((sum, item) => sum + item.calories, 0);

  return (
    <Screen
      title="PulseLog"
      subtitle="An offline-first health tracker for workouts, nutrition, goals, and connected activity data."
    >
      <Card>
        <Text style={styles.sectionTitle}>Today at a glance</Text>
        <View style={styles.row}>
          <MetricPill label="Steps" value={String(activity?.steps ?? 0)} />
          <MetricPill label="Active min" value={String(activity?.activeMinutes ?? 0)} />
          <MetricPill label="Source" value={activity?.source ?? 'demo'} />
        </View>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Weekly snapshot</Text>
        <View style={styles.row}>
          <MetricPill label="Workouts" value={String(workouts.length)} />
          <MetricPill label="Burned" value={`${totalCaloriesBurned}`} />
          <MetricPill label="Intake" value={`${totalCaloriesConsumed}`} />
        </View>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Goals in progress</Text>
        {goals.map((goal) => (
          <View key={goal.id} style={styles.goalRow}>
            <View>
              <Text style={styles.goalTitle}>{goal.title}</Text>
              <Text style={styles.goalMeta}>{goal.progress} / {goal.target} {goal.unit}</Text>
            </View>
            <Text style={styles.goalMeta}>{Math.round((goal.progress / goal.target) * 100)}%</Text>
          </View>
        ))}
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Sync health</Text>
        <Text style={styles.syncText}>Pending changes: {sync.queue.length}</Text>
        <Text style={styles.syncText}>Last sync: {sync.lastSyncedAt ?? 'not yet synced'}</Text>
        <Text style={styles.syncText}>Failed attempts: {sync.failures}</Text>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#14213d' },
  goalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  goalTitle: { fontSize: 16, fontWeight: '600', color: '#1d3557' },
  goalMeta: { fontSize: 13, color: '#52607a' },
  syncText: { color: '#52607a', lineHeight: 20 },
});
