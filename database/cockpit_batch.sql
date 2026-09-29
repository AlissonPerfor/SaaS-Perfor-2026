create function cockpit_private.save_batch(p_period date,p_rows jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare r jsonb; result jsonb := '[]'::jsonb;
begin
  if auth.uid() is null then raise exception 'Autenticação necessária' using errcode='42501'; end if;
  if jsonb_typeof(p_rows) is distinct from 'array' then raise exception 'Lote inválido'; end if;
  if jsonb_array_length(p_rows)<1 or jsonb_array_length(p_rows)>1000 then raise exception 'Tamanho de lote inválido'; end if;
  if exists (select 1 from jsonb_array_elements(p_rows) x group by x->>'project_id' having count(*)>1) then
    raise exception 'Projeto repetido no lote';
  end if;
  -- Stable project order avoids deadlocks between overlapping import batches.
  for r in select value from jsonb_array_elements(p_rows) order by (value->>'project_id')::bigint loop
    result := result || jsonb_build_array(cockpit_private.save_month(
      (r->>'project_id')::bigint,p_period,r->'snapshot',(r->>'expected_revision')::integer));
  end loop;
  return result;
end;
$$;
revoke all on function cockpit_private.save_batch(date,jsonb) from public,anon;
grant execute on function cockpit_private.save_batch(date,jsonb) to authenticated;
create function public.cockpit_save_batch(p_period date,p_rows jsonb)
returns jsonb language sql security invoker set search_path = '' as $$
  select cockpit_private.save_batch(p_period,p_rows);
$$;
revoke all on function public.cockpit_save_batch(date,jsonb) from public,anon;
grant execute on function public.cockpit_save_batch(date,jsonb) to authenticated;
notify pgrst,'reload schema';
