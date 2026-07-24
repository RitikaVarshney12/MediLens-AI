-- Phase 4: OCR processing pipeline
-- Run in the Supabase SQL editor (Project -> SQL Editor -> New query).
-- Requires 0001_create_reports_and_storage.sql to have been run already.

create table if not exists public.report_extractions (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null unique references public.reports(id) on delete cascade,
  raw_text text,
  structured_json jsonb,
  ocr_status text not null default 'processing'
    check (ocr_status in ('processing', 'completed', 'failed')),
  processing_started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists report_extractions_report_id_idx
  on public.report_extractions(report_id);

alter table public.report_extractions enable row level security;

-- No insert/update policy: only the backend (via the service-role
-- connection) writes to this table, which bypasses RLS entirely. Users
-- only ever need to read their own extraction results.
drop policy if exists "Users can view their own report extractions" on public.report_extractions;
create policy "Users can view their own report extractions"
  on public.report_extractions for select
  using (
    exists (
      select 1 from public.reports
      where reports.id = report_extractions.report_id
        and reports.user_id = auth.uid()
    )
  );