-- Run this once in Supabase → SQL Editor

-- 1. Create table
create table if not exists public.games (
  file_id  text primary key,          -- e.g. "CUSA00002_01.00"
  name     text not null,             -- game title (for fast search index)
  cusa_id  text not null,             -- CUSA ID
  data     jsonb not null default '{}' -- full original cheat JSON
);

-- 2. Indexes for fast lookups
create index if not exists games_cusa_id_idx on public.games (cusa_id);
create index if not exists games_name_idx    on public.games using gin (to_tsvector('english', name));

-- 3. Allow anyone to read (safe — anon key is read-only with RLS)
alter table public.games enable row level security;

create policy "Public read access"
  on public.games
  for select
  to anon
  using (true);
