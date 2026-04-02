import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export function MetricPill({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.value}>{value}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    backgroundColor: '#eef4ff',
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 12,
    gap: 4,
    minWidth: 108,
  },
  value: { fontSize: 22, fontWeight: '700', color: '#1d3557' },
  label: { fontSize: 12, color: '#52607a' },
});
