import { pool, redis } from "../db/index.js";
import { achievementsForProfile } from "./achievementService.js";
import { leaderboardWithPositions } from "./challengeService.js";
import { badgeForStreak, computeStreak } from "./streakService.js";
import { recommendReminderTime } from "./notificationService.js";

export async function getUserSummary(userId: string) {
  const user = await pool.query(
    `select id, name, email, timezone, notification_window_start, notification_window_end
     from users where id = $1`,
    [userId]
  );

  if (user.rowCount === 0) {
    return null;
  }

  const habits = await pool.query(
    `select id, name, category, frequency, target_per_period, color
     from habits where user_id = $1 and archived = false
     order by created_at asc`,
    [userId]
  );

  const entries = await pool.query(
    `select habit_id, completed_at
     from habit_entries where user_id = $1 order by completed_at desc`,
    [userId]
  );

  const challengeCount = await pool.query(
    `select count(*)::int as active_count
     from challenge_participants cp
     join challenges c on c.id = cp.challenge_id
     where cp.user_id = $1 and c.ends_on >= current_date`,
    [userId]
  );

  const entryTimestamps = entries.rows.map((row) => row.completed_at.toISOString());
  const streak = computeStreak(entryTimestamps);
  const badges = badgeForStreak(streak);
  const achievements = achievementsForProfile(streak, Math.min(entries.rowCount, 7), Number(challengeCount.rows[0]?.active_count ?? 0));

  return {
    user: {
      ...user.rows[0],
      notificationWindowStart: user.rows[0].notification_window_start,
      notificationWindowEnd: user.rows[0].notification_window_end
    },
    habits: habits.rows,
    stats: {
      streak,
      totalCheckIns: entries.rowCount,
      badges,
      achievements,
      recommendedReminder: recommendReminderTime({
        completionHistory: entryTimestamps.map((completedAt) => ({ completedAt })),
        quietWindowStart: user.rows[0].notification_window_start,
        quietWindowEnd: user.rows[0].notification_window_end
      })
    }
  };
}

export async function getFriends(userId: string) {
  const result = await pool.query(
    `select u.id, u.name, u.email
     from friendships f
     join users u on u.id = f.friend_id
     where f.user_id = $1 and f.status = 'accepted'
     order by u.name asc`,
    [userId]
  );
  return result.rows;
}

export async function getChallenges(userId: string) {
  const result = await pool.query(
    `select c.id, c.title, c.description, c.habit_category, c.starts_on, c.ends_on, cp.score, cp.progress
     from challenge_participants cp
     join challenges c on c.id = cp.challenge_id
     where cp.user_id = $1
     order by c.starts_on desc`,
    [userId]
  );
  return result.rows;
}

export async function getLeaderboard(challengeId: string) {
  const cacheKey = `leaderboard:${challengeId}`;
  if (redis.isOpen) {
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }
  }

  const result = await pool.query(
    `select u.id as "userId", u.name, cp.score, cp.progress
     from challenge_participants cp
     join users u on u.id = cp.user_id
     where cp.challenge_id = $1`,
    [challengeId]
  );

  const leaderboard = leaderboardWithPositions(result.rows);

  if (redis.isOpen) {
    await redis.set(cacheKey, JSON.stringify(leaderboard), { EX: 60 });
  }

  return leaderboard;
}

export async function createHabit(input: {
  userId: string;
  name: string;
  category: string;
  frequency: "daily" | "weekly";
  targetPerPeriod: number;
  color: string;
}) {
  const result = await pool.query(
    `insert into habits (user_id, name, category, frequency, target_per_period, color)
     values ($1, $2, $3, $4, $5, $6)
     returning id, user_id as "userId", name, category, frequency, target_per_period as "targetPerPeriod", color`,
    [input.userId, input.name, input.category, input.frequency, input.targetPerPeriod, input.color]
  );
  return result.rows[0];
}

export async function completeHabit(input: { userId: string; habitId: string; completedAt: string; }) {
  const result = await pool.query(
    `insert into habit_entries (habit_id, user_id, completed_at, source)
     values ($1, $2, $3, 'manual')
     returning id, habit_id as "habitId", user_id as "userId", completed_at as "completedAt"`,
    [input.habitId, input.userId, input.completedAt]
  );
  return result.rows[0];
}

export async function registerDevice(input: { userId: string; token: string; platform: "ios" | "android"; }) {
  const result = await pool.query(
    `insert into device_tokens (user_id, token, platform)
     values ($1, $2, $3)
     on conflict (token) do update set user_id = excluded.user_id, platform = excluded.platform, last_seen_at = now()
     returning id, user_id as "userId", token, platform`,
    [input.userId, input.token, input.platform]
  );
  return result.rows[0];
}

export async function createChallenge(input: {
  ownerId: string;
  title: string;
  description: string;
  habitCategory: string;
  startsOn: string;
  endsOn: string;
  participantIds: string[];
}) {
  const client = await pool.connect();
  try {
    await client.query("begin");
    const challengeResult = await client.query(
      `insert into challenges (owner_id, title, description, habit_category, starts_on, ends_on)
       values ($1, $2, $3, $4, $5, $6)
       returning id, owner_id as "ownerId", title, description, habit_category as "habitCategory", starts_on as "startsOn", ends_on as "endsOn"`,
      [input.ownerId, input.title, input.description, input.habitCategory, input.startsOn, input.endsOn]
    );
    const challenge = challengeResult.rows[0];
    const participants = [...new Set([input.ownerId, ...input.participantIds])];
    for (const userId of participants) {
      await client.query(
        `insert into challenge_participants (challenge_id, user_id)
         values ($1, $2) on conflict do nothing`,
        [challenge.id, userId]
      );
    }
    await client.query("commit");
    if (redis.isOpen) {
      await redis.del(`leaderboard:${challenge.id}`);
    }
    return challenge;
  } catch (error) {
    await client.query("rollback");
    throw error;
  } finally {
    client.release();
  }
}
