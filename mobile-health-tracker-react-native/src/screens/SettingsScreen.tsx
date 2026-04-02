import React from 'react';
import { Alert, StyleSheet, Text } from 'react-native';
import { Card } from '@/components/Card';
import { PrimaryButton } from '@/components/PrimaryButton';
import { Screen } from '@/components/Screen';
import { useAppSelector } from '@/hooks/redux';
import { runSync } from '@/services/syncService';
import { store } from '@/store';

export function SettingsScreen() {
  const sync = useAppSelector((state) => state.sync);
  const activity = useAppSelector((state) => state.activity.latest);

  async function handleSync() {
    await runSync(store);
    Alert.alert('Sync complete', 'Queued changes were pushed to the mock remote service.');
  }

  return (
    <Screen title="Settings" subtitle="Health provider status, sync controls, and local development notes.">
      <Card>
        <Text style={styles.title}>Connected activity source</Text>
        <Text style={styles.meta}>{activity?.source ?? 'demo'} connector active</Text>
        <Text style={styles.meta}>This repo ships with demo mode enabled so local development works on any machine.</Text>
      </Card>
      <Card>
        <Text style={styles.title}>Offline sync</Text>
        <Text style={styles.meta}>Pending queue size: {sync.queue.length}</Text>
        <Text style={styles.meta}>Last successful sync: {sync.lastSyncedAt ?? 'never'}</Text>
        <PrimaryButton title="Run sync now" onPress={handleSync} />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 17, fontWeight: '700', color: '#14213d', marginBottom: 8 },
  meta: { fontSize: 14, color: '#52607a', lineHeight: 22 },
});
