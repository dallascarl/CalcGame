-- CalcGame database. Paste this whole file into Supabase: SQL Editor, New query, Run.
-- It is safe to run more than once.
-- Privacy design: no real names, no emails, no student IDs. Students are known only by a username they pick.

create extension if not exists pgcrypto;

-- ---------- tables ----------
create table if not exists public.classes (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  code text not null unique check (code ~ '^[A-Z0-9]{4,12}$'),
  created_at timestamptz not null default now()
);

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text not null check (username ~ '^[A-Za-z0-9_]{3,20}$'),
  avatar text not null default 'blob',
  class_id uuid references public.classes(id) on delete set null,
  is_instructor boolean not null default false,
  points integer not null default 0 check (points >= 0),
  created_at timestamptz not null default now(),
  last_seen timestamptz not null default now()
);
create unique index if not exists profiles_username_lower on public.profiles (lower(username));

-- the student's whole game state (same shape as the browser save), so progress follows them between devices
create table if not exists public.saves (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

-- every checked answer: which question, right or wrong
create table if not exists public.answers (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references public.profiles(id) on delete cascade,
  deck text not null,
  area text not null,            -- 'lesson:<id>' or 'drill:<kind>'
  qid text not null,
  ok boolean not null,
  at timestamptz not null default now()
);
create index if not exists answers_user on public.answers(user_id);
create index if not exists answers_q on public.answers(deck, qid);

-- lessons finished, drill sets finished, stops cleared
create table if not exists public.completions (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references public.profiles(id) on delete cascade,
  deck text not null,
  kind text not null check (kind in ('lesson','drill','stop')),
  ref text not null,             -- lesson id, drill kind, or '<world>:<stop>'
  score integer,
  out_of integer,
  at timestamptz not null default now()
);
create index if not exists completions_user on public.completions(user_id);

-- "Send feedback" and "I don't understand"
create table if not exists public.messages (
  id bigint generated always as identity primary key,
  user_id uuid default auth.uid() references public.profiles(id) on delete set null,
  kind text not null check (kind in ('feedback','question')),
  deck text,
  ref text,
  context text,
  body text not null check (length(body) between 1 and 4000),
  status text not null default 'new' check (status in ('new','done')),
  created_at timestamptz not null default now()
);

create table if not exists public.due_dates (
  class_id uuid not null references public.classes(id) on delete cascade,
  stop text not null,            -- '<world>:<stop>'
  due_at timestamptz not null,
  primary key (class_id, stop)
);

-- one-time completion codes for Canvas credit
create table if not exists public.codes (
  code text primary key,
  user_id uuid not null references public.profiles(id) on delete cascade,
  stop text not null,
  created_at timestamptz not null default now(),
  redeemed_at timestamptz,
  unique (user_id, stop)
);

-- ---------- helpers ----------
create or replace function public.is_instructor() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select is_instructor from profiles where id = auth.uid()), false)
$$;
create or replace function public.my_class() returns uuid
language sql stable security definer set search_path = public as $$
  select class_id from profiles where id = auth.uid()
$$;

-- ---------- row level security ----------
alter table public.classes enable row level security;
alter table public.profiles enable row level security;
alter table public.saves enable row level security;
alter table public.answers enable row level security;
alter table public.completions enable row level security;
alter table public.messages enable row level security;
alter table public.due_dates enable row level security;
alter table public.codes enable row level security;

drop policy if exists classes_read on public.classes;
create policy classes_read on public.classes for select to authenticated using (id = public.my_class() or public.is_instructor());
drop policy if exists classes_write on public.classes;
create policy classes_write on public.classes for all to authenticated using (public.is_instructor()) with check (public.is_instructor());

drop policy if exists profiles_read on public.profiles;
create policy profiles_read on public.profiles for select to authenticated using (id = auth.uid() or public.is_instructor());

drop policy if exists saves_own on public.saves;
create policy saves_own on public.saves for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists saves_inst on public.saves;
create policy saves_inst on public.saves for select to authenticated using (public.is_instructor());

drop policy if exists answers_insert on public.answers;
create policy answers_insert on public.answers for insert to authenticated with check (user_id = auth.uid());
drop policy if exists answers_read on public.answers;
create policy answers_read on public.answers for select to authenticated using (user_id = auth.uid() or public.is_instructor());

drop policy if exists completions_insert on public.completions;
create policy completions_insert on public.completions for insert to authenticated with check (user_id = auth.uid());
drop policy if exists completions_read on public.completions;
create policy completions_read on public.completions for select to authenticated using (user_id = auth.uid() or public.is_instructor());

-- anyone may send feedback (guests too); only the instructor reads it
drop policy if exists messages_insert on public.messages;
create policy messages_insert on public.messages for insert to anon, authenticated with check (user_id is null or user_id = auth.uid());
drop policy if exists messages_read on public.messages;
create policy messages_read on public.messages for select to authenticated using (user_id = auth.uid() or public.is_instructor());
drop policy if exists messages_update on public.messages;
create policy messages_update on public.messages for update to authenticated using (public.is_instructor()) with check (public.is_instructor());
drop policy if exists messages_delete on public.messages;
create policy messages_delete on public.messages for delete to authenticated using (public.is_instructor());

drop policy if exists due_read on public.due_dates;
create policy due_read on public.due_dates for select to authenticated using (class_id = public.my_class() or public.is_instructor());
drop policy if exists due_write on public.due_dates;
create policy due_write on public.due_dates for all to authenticated using (public.is_instructor()) with check (public.is_instructor());

drop policy if exists codes_read on public.codes;
create policy codes_read on public.codes for select to authenticated using (user_id = auth.uid() or public.is_instructor());

-- ---------- functions the app calls ----------
-- before signing up: is the class code real? is the username free?
create or replace function public.class_name(p_code text) returns text
language sql stable security definer set search_path = public as $$
  select name from classes where code = upper(trim(p_code))
$$;
create or replace function public.username_free(p_name text) returns boolean
language sql stable security definer set search_path = public as $$
  select not exists (select 1 from profiles where lower(username) = lower(trim(p_name)))
$$;

-- after signing up: create the profile (class code required for students)
create or replace function public.create_profile(p_username text, p_avatar text, p_code text) returns void
language plpgsql security definer set search_path = public as $$
declare c uuid;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  select id into c from classes where code = upper(trim(p_code));
  if c is null then raise exception 'That class code was not found.'; end if;
  insert into profiles (id, username, avatar, class_id) values (auth.uid(), trim(p_username), coalesce(p_avatar, 'blob'), c)
  on conflict (id) do update set username = excluded.username, avatar = excluded.avatar, class_id = excluded.class_id;
end $$;

-- the instructor account: no class code needed; becomes an instructor only after you run the line at the bottom
create or replace function public.create_instructor_profile(p_username text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  insert into profiles (id, username, avatar) values (auth.uid(), trim(p_username), 'owl')
  on conflict (id) do nothing;
end $$;

create or replace function public.set_avatar(p_avatar text) returns void
language sql security definer set search_path = public as $$
  update profiles set avatar = left(p_avatar, 30) where id = auth.uid()
$$;

create or replace function public.touch() returns void
language sql security definer set search_path = public as $$
  update profiles set last_seen = now() where id = auth.uid()
$$;

-- Match Board points: can only go up, and by at most 500 per update
create or replace function public.sync_points(p integer) returns integer
language sql security definer set search_path = public as $$
  update profiles set points = greatest(points, least(p, points + 500)) where id = auth.uid() returning points
$$;

-- leaderboard for the caller's class: usernames and characters only
create or replace function public.leaderboard() returns table(username text, avatar text, points integer, me boolean)
language sql stable security definer set search_path = public as $$
  select p.username, p.avatar, p.points, p.id = auth.uid()
  from profiles p
  where p.class_id = (select class_id from profiles where id = auth.uid()) and not p.is_instructor
  order by p.points desc, p.created_at
  limit 50
$$;

-- a one-time completion code for a cleared stop (the same code if asked again)
create or replace function public.claim_code(p_stop text) returns text
language plpgsql security definer set search_path = public as $$
declare k text; abc text := 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'; i int;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if not exists (select 1 from completions where user_id = auth.uid() and kind = 'stop' and ref = p_stop) then
    raise exception 'Clear this stop first.';
  end if;
  select code into k from codes where user_id = auth.uid() and stop = p_stop;
  if k is not null then return k; end if;
  loop
    k := 'CG-';
    for i in 1..6 loop k := k || substr(abc, 1 + floor(random() * length(abc))::int, 1); end loop;
    begin
      insert into codes (code, user_id, stop) values (k, auth.uid(), p_stop);
      return k;
    exception when unique_violation then
      -- try another
    end;
  end loop;
end $$;

-- instructor: look up codes from a Canvas export (names never leave your browser)
create or replace function public.check_codes(p_codes text[]) returns table(code text, stop text, created_at timestamptz, redeemed_at timestamptz)
language plpgsql stable security definer set search_path = public as $$
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  return query select c.code, c.stop, c.created_at, c.redeemed_at from codes c where c.code = any(select upper(trim(x)) from unnest(p_codes) x);
end $$;
create or replace function public.redeem_codes(p_codes text[]) returns integer
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  update codes set redeemed_at = now() where code = any(select upper(trim(x)) from unnest(p_codes) x) and redeemed_at is null;
  get diagnostics n = row_count; return n;
end $$;

-- instructor: summaries
create or replace function public.inst_students(p_class uuid) returns table(id uuid, username text, avatar text, class_id uuid, points integer, created_at timestamptz, last_seen timestamptz, answers bigint, wrong bigint, lessons bigint, sets bigint, stops bigint)
language plpgsql stable security definer set search_path = public as $$
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  return query
  select p.id, p.username, p.avatar, p.class_id, p.points, p.created_at, p.last_seen,
    (select count(*) from answers a where a.user_id = p.id),
    (select count(*) from answers a where a.user_id = p.id and not a.ok),
    (select count(*) from completions c where c.user_id = p.id and c.kind = 'lesson'),
    (select count(*) from completions c where c.user_id = p.id and c.kind = 'drill'),
    (select count(distinct c.ref) from completions c where c.user_id = p.id and c.kind = 'stop')
  from profiles p
  where not p.is_instructor and (p_class is null or p.class_id = p_class)
  order by p.username;
end $$;

create or replace function public.inst_questions(p_class uuid) returns table(deck text, area text, qid text, attempts bigint, wrong bigint, students bigint, first_try_wrong bigint)
language plpgsql stable security definer set search_path = public as $$
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  return query
  with a as (
    select a.*, row_number() over (partition by a.user_id, a.deck, a.qid order by a.at) as n
    from answers a join profiles p on p.id = a.user_id
    where p_class is null or p.class_id = p_class)
  select a.deck, a.area, a.qid, count(*), count(*) filter (where not a.ok), count(distinct a.user_id),
         count(*) filter (where a.n = 1 and not a.ok)
  from a group by a.deck, a.area, a.qid;
end $$;

create or replace function public.inst_completions(p_class uuid) returns table(user_id uuid, deck text, kind text, ref text, score integer, out_of integer, at timestamptz)
language plpgsql stable security definer set search_path = public as $$
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  return query select c.user_id, c.deck, c.kind, c.ref, c.score, c.out_of, c.at
    from completions c join profiles p on p.id = c.user_id
    where p_class is null or p.class_id = p_class order by c.at;
end $$;

create or replace function public.inst_messages() returns table(id bigint, kind text, deck text, ref text, context text, body text, status text, created_at timestamptz, username text, class_id uuid)
language plpgsql stable security definer set search_path = public as $$
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  return query select m.id, m.kind, m.deck, m.ref, m.context, m.body, m.status, m.created_at, p.username, p.class_id
    from messages m left join profiles p on p.id = m.user_id order by m.created_at desc;
end $$;

-- instructor: set a new password for a student who forgot theirs
create or replace function public.inst_reset_password(p_username text, p_password text) returns void
language plpgsql security definer set search_path = public, auth, extensions as $$
declare u uuid;
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  if length(p_password) < 6 then raise exception 'Use at least 6 characters.'; end if;
  select id into u from profiles where lower(username) = lower(trim(p_username)) and not is_instructor;
  if u is null then raise exception 'No student with that username.'; end if;
  update auth.users set encrypted_password = crypt(p_password, gen_salt('bf')) where id = u;
end $$;

-- instructor: remove a student and everything they stored
create or replace function public.inst_delete_student(p_id uuid) returns void
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_instructor() then raise exception 'instructor only'; end if;
  if exists (select 1 from profiles where id = p_id and is_instructor) then raise exception 'cannot delete an instructor'; end if;
  delete from auth.users where id = p_id;
end $$;

-- who may call what
revoke all on function public.check_codes(text[]), public.redeem_codes(text[]), public.inst_students(uuid), public.inst_questions(uuid),
  public.inst_completions(uuid), public.inst_messages(), public.inst_reset_password(text, text), public.inst_delete_student(uuid) from public, anon;
grant execute on function public.check_codes(text[]), public.redeem_codes(text[]), public.inst_students(uuid), public.inst_questions(uuid),
  public.inst_completions(uuid), public.inst_messages(), public.inst_reset_password(text, text), public.inst_delete_student(uuid) to authenticated;
grant execute on function public.class_name(text), public.username_free(text) to anon, authenticated;

-- ============================================================================
-- AFTER you create your instructor account on instructor.html, run this one
-- line (with your instructor username) to give it instructor powers:
--
--   update public.profiles set is_instructor = true where lower(username) = lower('YOUR_USERNAME');
-- ============================================================================
