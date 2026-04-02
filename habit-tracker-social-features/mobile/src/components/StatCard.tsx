import { ReactNode } from "react";
import { StyleSheet, Text, View } from "react-native";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  accent?: string;
  children?: ReactNode;
}

export function StatCard({ title, value, subtitle, accent = "#4f46e5", children }: StatCardProps) {
  return (
    <View style={[styles.card, { borderLeftColor: accent }]}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.value}>{value}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#ffffff",
    borderLeftWidth: 5,
    borderRadius: 16,
    padding: 16,
    gap: 8,
    shadowColor: "#111827",
    shadowOpacity: 0.06,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2
  },
  title: {
    fontSize: 13,
    color: "#6b7280",
    fontWeight: "600"
  },
  value: {
    fontSize: 24,
    fontWeight: "700",
    color: "#111827"
  },
  subtitle: {
    fontSize: 13,
    color: "#6b7280"
  }
});
