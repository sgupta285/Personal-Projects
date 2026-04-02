import { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { getFriends } from "../api/client";

export function FriendsScreen() {
  const [friends, setFriends] = useState<any[]>([]);

  useEffect(() => {
    getFriends().then(setFriends);
  }, []);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Friends</Text>
      <Text style={styles.subheading}>Accountability works better when progress is visible.</Text>
      <View style={styles.list}>
        {friends.map((friend) => (
          <View key={friend.id} style={styles.card}>
            <Text style={styles.name}>{friend.name}</Text>
            <Text style={styles.meta}>Ready for the next challenge</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 20, gap: 12 },
  heading: { fontSize: 28, fontWeight: "800", color: "#111827" },
  subheading: { color: "#4b5563" },
  list: { gap: 12 },
  card: { backgroundColor: "#ffffff", padding: 16, borderRadius: 16 },
  name: { fontWeight: "700", fontSize: 16, color: "#111827" },
  meta: { color: "#6b7280", marginTop: 4 }
});
