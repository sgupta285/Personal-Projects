import { demoChallenges, demoFriends, demoLeaderboard, demoProfile } from "../mocks/demoData";
import { getItem, setItem } from "../services/storage";

const baseUrl = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:4000";

async function fetchJson(path: string, options: RequestInit = {}) {
  const token = await getItem("authToken");
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      "content-type": "application/json",
      ...(options.headers ?? {}),
      ...(token ? { authorization: `Bearer ${token}` } : {})
    }
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export async function loginDemoUser() {
  try {
    const payload = await fetchJson("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "maya@example.com" })
    });
    await setItem("authToken", payload.token);
    return payload;
  } catch {
    return { token: "offline-demo" };
  }
}

export async function getDashboard() {
  try {
    return await fetchJson("/users/me");
  } catch {
    return demoProfile;
  }
}

export async function getFriends() {
  try {
    const result = await fetchJson("/users/me/friends");
    return result.items;
  } catch {
    return demoFriends;
  }
}

export async function getChallenges() {
  try {
    const result = await fetchJson("/challenges");
    return result.items;
  } catch {
    return demoChallenges;
  }
}

export async function getLeaderboard(challengeId: string) {
  try {
    const result = await fetchJson(`/challenges/${challengeId}/leaderboard`);
    return result.items;
  } catch {
    return demoLeaderboard;
  }
}

export async function completeHabit(habitId: string) {
  try {
    return await fetchJson(`/habits/${habitId}/complete`, {
      method: "POST",
      body: JSON.stringify({})
    });
  } catch {
    return { ok: true };
  }
}
