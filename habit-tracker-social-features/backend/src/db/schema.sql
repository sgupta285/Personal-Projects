create extension if not exists "pgcrypto";

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text not null unique,
  timezone text not null default 'America/Chicago',
  notification_window_start time not null default '07:00',
  notification_window_end time not null default '21:00',
  created_at timestamptz not null default now()
);

create table if not exists habits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  name text not null,
  category text not null,
  frequency text not null check (frequency in ('daily', 'weekly')),
  target_per_period integer not null check (target_per_period > 0),
  color text not null default '#4f46e5',
  archived boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists habit_entries (
  id uuid primary key default gen_random_uuid(),
  habit_id uuid not null references habits(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  completed_at timestamptz not null,
  source text not null default 'manual',
  created_at timestamptz not null default now()
);

create table if not exists friendships (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  friend_id uuid not null references users(id) on delete cascade,
  status text not null check (status in ('pending', 'accepted', 'blocked')),
  created_at timestamptz not null default now(),
  unique(user_id, friend_id)
);

create table if not exists challenges (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references users(id) on delete cascade,
  title text not null,
  description text not null,
  habit_category text not null,
  starts_on date not null,
  ends_on date not null,
  created_at timestamptz not null default now()
);

create table if not exists challenge_participants (
  id uuid primary key default gen_random_uuid(),
  challenge_id uuid not null references challenges(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  score integer not null default 0,
  progress integer not null default 0,
  joined_at timestamptz not null default now(),
  unique(challenge_id, user_id)
);

create table if not exists device_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  token text not null unique,
  platform text not null check (platform in ('ios', 'android')),
  last_seen_at timestamptz not null default now()
);

create index if not exists idx_habits_user_id on habits(user_id);
create index if not exists idx_habit_entries_user_habit_time on habit_entries(user_id, habit_id, completed_at desc);
create index if not exists idx_friendships_user_status on friendships(user_id, status);
create index if not exists idx_challenge_participants_challenge_score on challenge_participants(challenge_id, score desc);
