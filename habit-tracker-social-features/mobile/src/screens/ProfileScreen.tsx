import { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { getDashboard } from "../api/client";

export function ProfileScreen() {
  const [dashboard, setDashboard] = useState<any>(null);

  useEffect(() => {
    getDashboard().then(setDashboard);
  }, []);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Profile</Text>
      {dashboard ? (
        <>
          <View style={styles.card}>
            <Text style={styles.name}>{dashboard.user.name}</Text>
            <Text style={styles.meta}>{dashboard.user.email}</Text>
            <Text style={styles.meta}>Recommended reminder: {dashboard.stats.recommendedReminder}</Text>
          </View>
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Achievements</Text>
            {dashboard.stats.achievements?.map((achievement: any) => (
              <View key={achievement.code} style={styles.achievement}>
                <Text style={styles.achievementTitle}>{achievement.title}</Text>
                <Text style={styles.meta}>{achievement.description}</Text>
              </View>
            )) ?? <Text style={styles.meta}>No achievements yet.</Text>}
          </View>
        </>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 20, gap: 12 },
  heading: { fontSize: 28, fontWeight: "800", color: "#111827" },
  card: { backgroundColor: "#ffffff", borderRadius: 16, padding: 16, gap: 8 },
  name: { fontSize: 20, fontWeight: "700", color: "#111827" },
  meta: { color: "#6b7280" },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: "#111827" },
  achievement: { paddingTop: 8, borderTopWidth: 1, borderTopColor: "#e5e7eb" },
  achievementTitle: { fontWeight: "700", color: "#111827" }
});
