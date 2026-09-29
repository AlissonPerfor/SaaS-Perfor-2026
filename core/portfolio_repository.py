"""Acesso autenticado ao armazenamento privado do Cockpit via RPC."""
from core.database import get_supabase
from core.portfolio import validate_snapshot


def read_month(period):
    return get_supabase().rpc("cockpit_read_month", {"p_period": period.isoformat()}).execute().data or []


def save_month(project_id, period, snapshot, expected_revision):
    return get_supabase().rpc("cockpit_save_month", {
        "p_project_id": int(project_id), "p_period": period.isoformat(),
        "p_snapshot": validate_snapshot(snapshot, period),
        "p_expected_revision": int(expected_revision),
    }).execute().data


def history(project_id, period):
    return get_supabase().rpc("cockpit_history", {
        "p_project_id": int(project_id), "p_period": period.isoformat(),
    }).execute().data or []


def save_batch(period, rows):
    return get_supabase().rpc("cockpit_save_batch", {
        "p_period": period.isoformat(), "p_rows": [
            {"project_id": int(r["project_id"]),
             "snapshot": validate_snapshot(r["snapshot"], period),
             "expected_revision": int(r["expected_revision"])} for r in rows]
    }).execute().data
