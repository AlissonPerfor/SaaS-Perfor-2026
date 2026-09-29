-- Cockpit v1. Applied through Supabase migration cockpit_foundation_v1.
-- No ALTER POLICY / ENABLE RLS; existing tables and policies remain unchanged.
create schema cockpit_private;
revoke all on schema cockpit_private from public, anon, authenticated;
grant usage on schema cockpit_private to authenticated;

create table cockpit_private.monthly_metrics (
  project_id bigint not null references public.projetos(id),
  period date not null check (extract(day from period)=1),
  revenue_target numeric(16,2) check (revenue_target >= 0),
  budget numeric(16,2) check (budget >= 0),
  revenue numeric(16,2) check (revenue >= 0),
  spend numeric(16,2) check (spend >= 0),
  paid_orders bigint check (paid_orders >= 0),
  sessions bigint check (sessions >= 0),
  as_of date,
  source text not null check (source in ('manual','csv','gps')),
  notes text not null default '' check (length(notes)<=1000),
  revision integer not null check (revision>0),
  updated_at timestamptz not null default now(),
  updated_by uuid not null,
  primary key (project_id, period),
  check (as_of is null or (as_of >= period and as_of < period + interval '1 month')),
  check ((revenue is null and spend is null and paid_orders is null and sessions is null) or as_of is not null)
);
create index monthly_metrics_period_idx on cockpit_private.monthly_metrics(period, project_id);
create table cockpit_private.metric_history (
  project_id bigint not null references public.projetos(id),
  period date not null,
  revision integer not null,
  snapshot jsonb not null,
  recorded_at timestamptz not null default now(),
  primary key (project_id, period, revision)
);
revoke all on all tables in schema cockpit_private from public, anon, authenticated;

-- Definer is private and narrowly scoped: underlying tables are never granted
-- to API roles. Public wrappers below are SECURITY INVOKER.
create function cockpit_private.can_access(p_project_id bigint)
returns boolean language sql stable security definer set search_path = '' as $$
  select auth.uid() is not null and exists (
    select 1 from public.projetos p
    join auth.users a on a.id=auth.uid()
    left join public.usuarios u on lower(trim(u.email))=lower(trim(a.email))
    where p.id=p_project_id and (
      lower(trim(u.cargo))='ceo'
      or (lower(trim(u.cargo))='head' and u.squad is not null and p.squad=u.squad)
      or (coalesce(lower(trim(u.cargo)),'analista') not in ('ceo','head')
          and lower(trim(p.analista_email))=lower(trim(a.email)))
    )
  );
$$;

create function cockpit_private.read_month(p_period date)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if auth.uid() is null then raise exception 'Autenticação necessária' using errcode='42501'; end if;
  if p_period is null or extract(day from p_period)<>1 then raise exception 'Competência inválida'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'id',p.id,'nome_cliente',p.nome_cliente,'squad',p.squad,
      'analista_email',p.analista_email,'tipo',p.tipo,
      'google_sheet_id',p.google_sheet_id,'snapshot',to_jsonb(m)
    ) order by p.nome_cliente)
    from public.projetos p
    left join cockpit_private.monthly_metrics m on m.project_id=p.id and m.period=p_period
    where cockpit_private.can_access(p.id)
  ),'[]'::jsonb);
end;
$$;

create function cockpit_private.save_month(p_project_id bigint,p_period date,p_snapshot jsonb,p_expected_revision integer)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  old_revision integer;
  saved cockpit_private.monthly_metrics;
  k text;
begin
  if not cockpit_private.can_access(p_project_id) then
    raise exception 'Projeto não autorizado' using errcode='42501';
  end if;
  if p_period is null or extract(day from p_period)<>1 or p_expected_revision is null or p_expected_revision<0
    or jsonb_typeof(p_snapshot) is distinct from 'object' then raise exception 'Registro inválido'; end if;
  for k in select jsonb_object_keys(p_snapshot) loop
    if k not in ('revenue_target','budget','revenue','spend','paid_orders','sessions','as_of','source','notes') then
      raise exception 'Campo desconhecido: %',k;
    end if;
  end loop;
  foreach k in array array['revenue_target','budget','revenue','spend','paid_orders','sessions'] loop
    if p_snapshot ? k and jsonb_typeof(p_snapshot->k) not in ('number','null') then
      raise exception 'Valor numérico inválido: %',k;
    end if;
    if k in ('paid_orders','sessions') and (p_snapshot->>k)::numeric <> trunc((p_snapshot->>k)::numeric) then
      raise exception 'Contagem deve ser inteira: %',k;
    end if;
  end loop;
  if (p_snapshot->>'as_of')::date > current_date then raise exception 'Data de apuração futura'; end if;
  -- Serialize writers for this project; no project data is changed.
  perform 1 from public.projetos where id=p_project_id for update;
  select revision into old_revision from cockpit_private.monthly_metrics where project_id=p_project_id and period=p_period;
  if coalesce(old_revision,0)<>p_expected_revision then
    raise exception 'CONFLICT: registro atualizado por outra sessão; recarregue antes de salvar' using errcode='40001';
  end if;
  insert into cockpit_private.monthly_metrics (
    project_id,period,revenue_target,budget,revenue,spend,paid_orders,sessions,as_of,source,notes,revision,updated_by
  ) values (
    p_project_id,p_period,(p_snapshot->>'revenue_target')::numeric,(p_snapshot->>'budget')::numeric,
    (p_snapshot->>'revenue')::numeric,(p_snapshot->>'spend')::numeric,
    (p_snapshot->>'paid_orders')::bigint,(p_snapshot->>'sessions')::bigint,
    (p_snapshot->>'as_of')::date,coalesce(p_snapshot->>'source','manual'),coalesce(p_snapshot->>'notes',''),
    coalesce(old_revision,0)+1,auth.uid()
  )
  on conflict (project_id,period) do update set
    revenue_target=excluded.revenue_target,budget=excluded.budget,revenue=excluded.revenue,
    spend=excluded.spend,paid_orders=excluded.paid_orders,sessions=excluded.sessions,
    as_of=excluded.as_of,source=excluded.source,notes=excluded.notes,
    revision=excluded.revision,updated_at=now(),updated_by=excluded.updated_by
  returning * into saved;
  insert into cockpit_private.metric_history(project_id,period,revision,snapshot)
    values(p_project_id,p_period,saved.revision,to_jsonb(saved));
  return to_jsonb(saved);
end;
$$;

create function cockpit_private.history(p_project_id bigint,p_period date)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not cockpit_private.can_access(p_project_id) then raise exception 'Projeto não autorizado' using errcode='42501'; end if;
  return coalesce((select jsonb_agg(t.snapshot order by t.revision desc) from (
    select snapshot,revision from cockpit_private.metric_history
    where project_id=p_project_id and period=p_period order by revision desc limit 20
  ) t),'[]'::jsonb);
end;
$$;

revoke all on all functions in schema cockpit_private from public, anon, authenticated;
grant execute on function cockpit_private.read_month(date),
  cockpit_private.save_month(bigint,date,jsonb,integer),cockpit_private.history(bigint,date) to authenticated;

create function public.cockpit_read_month(p_period date)
returns jsonb language sql security invoker set search_path = '' as $$
  select cockpit_private.read_month(p_period);
$$;
create function public.cockpit_save_month(p_project_id bigint,p_period date,p_snapshot jsonb,p_expected_revision integer)
returns jsonb language sql security invoker set search_path = '' as $$
  select cockpit_private.save_month(p_project_id,p_period,p_snapshot,p_expected_revision);
$$;
create function public.cockpit_history(p_project_id bigint,p_period date)
returns jsonb language sql security invoker set search_path = '' as $$
  select cockpit_private.history(p_project_id,p_period);
$$;
revoke all on function public.cockpit_read_month(date),public.cockpit_save_month(bigint,date,jsonb,integer),
  public.cockpit_history(bigint,date) from public,anon;
grant execute on function public.cockpit_read_month(date),public.cockpit_save_month(bigint,date,jsonb,integer),
  public.cockpit_history(bigint,date) to authenticated;
notify pgrst,'reload schema';

