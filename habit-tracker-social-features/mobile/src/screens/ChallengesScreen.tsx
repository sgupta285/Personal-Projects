import { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { getChallenges, getLeaderboard } from "../api/client";
import { StatCard } from "../components/StatCard";

export function ChallengesScreen() {
  const [challenges, setChallenges] = useState<any[]>([]);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    getChallenges().then(async (items) => {
      setChallenges(items);
      if (items[0]?.id) {
        setLeaderboard(await getLeaderboard(items[0].id));
      }
    });
  }, []);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Challenges</Text>
      {challenges.map((challenge) => (
        <StatCard
          key={challenge.id}
          title={challenge.title}
          value={`${challenge.progress} day progress`}
          subtitle={challenge.description}
          accent="#0ea5e9"
        />
      ))}

      <View style={styles.board}>
        <Text style={styles.sectionTitle}>Leaderboard</Text>
        {leaderboard.map((item) => (
          <View key={item.rank} style={styles.row}>
            <Text style={styles.rank}>#{item.rank}</Text>
            <View style={{ flex: 1 }}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.detail}>{item.progress} check-ins</Text>
            </View>
            <Text style={styles.score}>{item.score}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 20, gap: 14 },
  heading: { fontSize: 28, fontWeight: "800", color: "#111827" },
  board: { backgroundColor: "#ffffff", borderRadius: 16, padding: 16, gap: 12 },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: "#111827" },
  row: { flexDirection: "row", alignItems: "center", gap: 12, paddingVertical: 8 },
  rank: { width: 34, fontWeight: "700", color: "#6366f1" },
  name: { fontWeight: "700", color: "#111827" },
  detail: { color: "#6b7280" },
  score: { fontWeight: "800", color: "#111827" }
});
