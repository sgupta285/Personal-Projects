export const demoProfile = {
  user: {
    id: "11111111-1111-1111-1111-111111111111",
    name: "Maya Carter",
    email: "maya@example.com"
  },
  stats: {
    streak: 4,
    totalCheckIns: 12,
    badges: ["Momentum Starter", "Week Warrior"],
    recommendedReminder: "17:00"
  },
  habits: [
    { id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", name: "Morning Run", category: "fitness", targetPerPeriod: 1, color: "#16a34a" },
    { id: "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", name: "Read 20 Minutes", category: "mindset", targetPerPeriod: 1, color: "#2563eb" }
  ]
};

export const demoFriends = [
  { id: "22222222-2222-2222-2222-222222222222", name: "Leo Tran" },
  { id: "33333333-3333-3333-3333-333333333333", name: "Nina Patel" }
];

export const demoChallenges = [
  {
    id: "dddddddd-dddd-dddd-dddd-dddddddddddd",
    title: "7 Day Hydration Push",
    description: "Check in daily and keep the streak moving.",
    score: 46,
    progress: 4
  }
];

export const demoLeaderboard = [
  { userId: "111", name: "Maya Carter", score: 46, progress: 4, rank: 1 },
  { userId: "222", name: "Leo Tran", score: 42, progress: 4, rank: 2 },
  { userId: "333", name: "Nina Patel", score: 33, progress: 3, rank: 3 }
];
