-- Run this once in the Supabase SQL Editor (Project > SQL Editor > New query).

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null,
  challenge_type text not null check (challenge_type in ('burpees', 'steps')),
  created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;

create policy "profiles_select_authenticated"
  on public.profiles for select to authenticated using (true);

create policy "profiles_insert_own"
  on public.profiles for insert to authenticated with check (auth.uid() = id);
-- No update/delete policy: a profile is immutable after creation
-- (challenge type is a one-time choice), enforced by default-deny.

create table public.entries (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles(id) on delete cascade,
  entry_date date not null default (now() at time zone 'utc')::date,
  amount integer not null check (amount >= 0),
  message text,
  created_at timestamptz not null default now()
);
alter table public.entries enable row level security;

create policy "entries_select_authenticated"
  on public.entries for select to authenticated using (true);

create policy "entries_insert_own"
  on public.entries for insert to authenticated with check (auth.uid() = user_id);
-- No update/delete policy: entries are append-only; multiple same-day
-- entries are allowed and simply sum together.
