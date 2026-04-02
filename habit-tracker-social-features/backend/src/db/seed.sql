insert into users (id, name, email, timezone, notification_window_start, notification_window_end)
values
  ('11111111-1111-1111-1111-111111111111', 'Maya Carter', 'maya@example.com', 'America/Chicago', '07:30', '21:00'),
  ('22222222-2222-2222-2222-222222222222', 'Leo Tran', 'leo@example.com', 'America/New_York', '07:00', '20:30'),
  ('33333333-3333-3333-3333-333333333333', 'Nina Patel', 'nina@example.com', 'America/Los_Angeles', '08:00', '22:00')
on conflict (email) do nothing;

insert into habits (id, user_id, name, category, frequency, target_per_period, color)
values
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'Morning Run', 'fitness', 'daily', 1, '#16a34a'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', 'Read 20 Minutes', 'mindset', 'daily', 1, '#2563eb'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', '22222222-2222-2222-2222-222222222222', 'Drink Water', 'health', 'daily', 8, '#0ea5e9')
on conflict do nothing;

insert into habit_entries (habit_id, user_id, completed_at, source)
values
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', now() - interval '4 day', 'manual'),
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', now() - interval '3 day', 'manual'),
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', now() - interval '2 day', 'manual'),
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', now() - interval '1 day', 'manual'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', now() - interval '2 day', 'manual'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', now() - interval '1 day', 'manual'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', '22222222-2222-2222-2222-222222222222', now() - interval '1 day', 'manual')
on conflict do nothing;

insert into friendships (user_id, friend_id, status)
values
  ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'accepted'),
  ('11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'accepted')
on conflict do nothing;

insert into challenges (id, owner_id, title, description, habit_category, starts_on, ends_on)
values
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', '7 Day Hydration Push', 'Keep the streak alive and check in every day this week.', 'health', current_date, current_date + interval '6 day')
on conflict do nothing;

insert into challenge_participants (challenge_id, user_id, score, progress)
values
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', 46, 4),
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', '22222222-2222-2222-2222-222222222222', 42, 4),
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', '33333333-3333-3333-3333-333333333333', 33, 3)
on conflict do nothing;
