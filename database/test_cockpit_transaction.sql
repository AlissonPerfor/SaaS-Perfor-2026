begin;
do $$
declare actor uuid; pid bigint; v_period date := date_trunc('month',current_date)::date; saved jsonb; expected int; before_rows jsonb; after_rows jsonb;
begin
  select a.id into actor from auth.users a join public.usuarios u on lower(trim(u.email))=lower(trim(a.email)) where lower(trim(u.cargo))='ceo' limit 1;
  if actor is null then raise exception 'No authorized test actor'; end if;
  select id into pid from public.projetos order by id limit 1;
  select coalesce(max(revision),0) into expected from cockpit_private.monthly_metrics m where m.project_id=pid and m.period=v_period;
  perform set_config('request.jwt.claims',jsonb_build_object('sub',actor,'role','authenticated')::text,true);
  execute 'set local role authenticated';
  before_rows := public.cockpit_read_month(v_period);
  begin
    perform public.cockpit_save_batch(v_period,jsonb_build_array(
      jsonb_build_object('project_id',pid,'snapshot',jsonb_build_object('revenue_target',1000),'expected_revision',expected),
      jsonb_build_object('project_id',9223372036854775806,'snapshot','{}'::jsonb,'expected_revision',0)
    ));
    raise exception 'unauthorized batch not rejected';
  exception when insufficient_privilege then null;
  end;
  after_rows := public.cockpit_read_month(v_period);
  if before_rows<>after_rows then raise exception 'partial batch persisted'; end if;
  saved := public.cockpit_save_batch(v_period,jsonb_build_array(
    jsonb_build_object('project_id',pid,'snapshot',jsonb_build_object('revenue_target',1000,'revenue',100,'spend',20,'as_of',current_date,'source','csv'),'expected_revision',expected)
  ));
  if (saved->0->>'revision')::int<>expected+1 then raise exception 'revision mismatch'; end if;
  if jsonb_array_length(public.cockpit_history(pid,v_period))<1 then raise exception 'history missing'; end if;
  begin
    perform public.cockpit_save_month(pid,v_period,'{}'::jsonb,expected);
    raise exception 'conflict not rejected';
  exception when serialization_failure then null;
  end;
  begin
    perform 1 from cockpit_private.monthly_metrics;
    raise exception 'direct table access not blocked';
  exception when insufficient_privilege then null;
  end;
  perform set_config('request.jwt.claims',jsonb_build_object('sub',gen_random_uuid(),'role','authenticated')::text,true);
  if public.cockpit_read_month(v_period)<>'[]'::jsonb then raise exception 'unknown actor can read projects'; end if;
  perform set_config('request.jwt.claims','{}',true);
  begin
    perform public.cockpit_read_month(v_period);
    raise exception 'anonymous not rejected';
  exception when insufficient_privilege then null;
  end;
  execute 'reset role';
end $$;
rollback;
