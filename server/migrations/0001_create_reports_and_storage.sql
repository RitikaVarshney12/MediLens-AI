-- Phase 3: report upload & file management
-- Run in the Supabase SQL editor (Project -> SQL Editor -> New query).

-- ---------------------------------------------------------------------------
-- Table: reports
-- ---------------------------------------------------------------------------
create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  file_name text not null,
  file_type text not null,
  file_size bigint not null,
  storage_path text not null,
  status text not null default 'uploaded'
    check (status in ('uploaded', 'processing', 'completed', 'failed')),
  uploaded_at timestamptz not null default now()
);

create index if not exists reports_user_id_idx on public.reports(user_id);
create index if not exists reports_uploaded_at_idx on public.reports(uploaded_at desc);

alter table public.reports enable row level security;

drop policy if exists "Users can view their own reports" on public.reports;
create policy "Users can view their own reports"
  on public.reports for select
  using (auth.uid() = user_id);

drop policy if exists "Users can insert their own reports" on public.reports;
create policy "Users can insert their own reports"
  on public.reports for insert
  with check (auth.uid() = user_id);

drop policy if exists "Users can delete their own reports" on public.reports;
create policy "Users can delete their own reports"
  on public.reports for delete
  using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Storage: medical-reports bucket
-- Files are stored under `{user_id}/{filename}`, which the policies below
-- use to restrict access to each user's own folder.
-- ---------------------------------------------------------------------------
insert into storage.buckets (id, name, public)
values ('medical-reports', 'medical-reports', false)
on conflict (id) do nothing;

drop policy if exists "Users can view own report files" on storage.objects;
create policy "Users can view own report files"
  on storage.objects for select
  using (
    bucket_id = 'medical-reports'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "Users can upload own report files" on storage.objects;
create policy "Users can upload own report files"
  on storage.objects for insert
  with check (
    bucket_id = 'medical-reports'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "Users can delete own report files" on storage.objects;
create policy "Users can delete own report files"
  on storage.objects for delete
  using (
    bucket_id = 'medical-reports'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- Note: the backend uploads using the service role key, which bypasses RLS
-- entirely (the user_id in storage paths and the reports table comes from
-- the verified JWT, not from client input). These policies matter for any
-- direct-from-browser access to Storage, and as defense in depth.