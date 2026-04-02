import { useEffect, useState } from "react";
import { Alert, RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";
import { completeHabit, getDashboard, loginDemoUser } from "../api/client";
import { HabitCard } from "../components/HabitCard";
import { StatCard } from "../components/StatCard";
import { registerForNotifications } from "../services/notifications";
import { streakLabel } from "../utils/streak";
import { useOfflineQueue } from "../hooks/useOfflineQueue";

export function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<any>(null);
  const { items, enqueue, clear } = useOfflineQueue();

  async function load() {
    setLoading(true);
    await loginDemoUser();
    const token = await registerForNotifications();
    if (token) {
      console.log("Registered push token", token);
    }
    const result = await getDashboard();
    setDashboard(result);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  const handleCompleteHabit = async (habitId: string) => {
    try {
      await completeHabit(habitId);
      Alert.alert("Nice work", "Your check-in was saved.");
      await clear();
      await load();
    } catch {
      await enqueue(habitId);
      Alert.alert("Saved offline", "We queued your check-in and will sync it later.");
    }
  };

  if (!dashboard) {
    return <View style={styles.center}><Text>{loading ? "Loading your habits..." : "No data available."}</Text></View>;
  }

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
    >
      <Text style={styles.heading}>Hi, {dashboard.user.name.split(" ")[0]}</Text>
      <Text style={styles.subheading}>Your social streak system is built around small wins and visible progress.</Text>

      <View style={styles.statGrid}>
        <StatCard title="Current streak" value={`${dashboard.stats.streak} days`} subtitle={streakLabel(dashboard.stats.streak)} accent="#f97316" />
        <StatCard title="Badges" value={dashboard.stats.badges.length} subtitle={dashboard.stats.badges.join(", ")} accent="#8b5cf6" />
        <StatCard title="Reminder window" value={dashboard.stats.recommendedReminder} subtitle="Based on your completion history" accent="#10b981" />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Today&apos;s habits</Text>
        {dashboard.habits.map((habit: any) => (
          <HabitCard
            key={habit.id}
            name={habit.name}
            category={habit.category}
            color={habit.color}
            onComplete={() => handleCompleteHabit(habit.id)}
          />
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Offline queue</Text>
        <Text style={styles.body}>{items.length === 0 ? "No pending check-ins." : `${items.length} check-ins will sync when the API is reachable.`}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#f3f4f6"
  },
  content: {
    padding: 20,
    gap: 16
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center"
  },
  heading: {
    fontSize: 28,
    fontWeight: "800",
    color: "#111827"
  },
  subheading: {
    color: "#4b5563",
    lineHeight: 20
  },
  statGrid: {
    gap: 12
  },
  section: {
    gap: 10
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827"
  },
  body: {
    color: "#4b5563"
  }
});
