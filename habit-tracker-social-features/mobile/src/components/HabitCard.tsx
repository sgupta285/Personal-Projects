import { Pressable, StyleSheet, Text, View } from "react-native";

interface HabitCardProps {
  name: string;
  category: string;
  color: string;
  onComplete?: () => void;
}

export function HabitCard({ name, category, color, onComplete }: HabitCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={[styles.dot, { backgroundColor: color }]} />
        <View style={{ flex: 1 }}>
          <Text style={styles.name}>{name}</Text>
          <Text style={styles.category}>{category}</Text>
        </View>
        <Pressable onPress={onComplete} style={styles.button}>
          <Text style={styles.buttonText}>Check in</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    marginBottom: 12
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 999
  },
  name: {
    fontSize: 16,
    fontWeight: "700",
    color: "#111827"
  },
  category: {
    color: "#6b7280",
    marginTop: 2
  },
  button: {
    backgroundColor: "#111827",
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 8
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "600"
  }
});
