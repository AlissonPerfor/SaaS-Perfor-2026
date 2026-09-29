"""Cockpit da Carteira: consolidação mensal e manutenção dos dados."""
import hashlib
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core.portfolio import FIELDS, LABELS, export_csv, indicators, parse_csv, summarize, validate_snapshot
from core import portfolio_repository as repository
from core.context import navigate_to_project

MONTHS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
COLORS = {"Crítico": "🔴", "Atenção": "🟡", "No ritmo": "🟢", "Dados pendentes": "⚪", "Desatualizado": "🟠", "Planejado": "🔵"}


def money(value):
    if value is None:
        return "—"
    return (f"R$ {value:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")


def failure(exc):
    if "CONFLICT" in str(exc) or "40001" in str(exc):
        return "Outra sessão alterou estes dados. Feche e reabra a edição para carregar a versão mais recente."
    return "Não foi possível concluir. Verifique sua conexão e tente novamente. Seus dados não foram confirmados."


@st.dialog("Atualizar dados do mês", width="large")
def edit_project(project, period):
    snapshot = project.get("snapshot") or {}
    st.subheader(project["nome_cliente"])
    st.caption(f"{MONTHS[period.month-1]} / {period.year} · versão {snapshot.get('revision', 0)}")
    st.info("Campos vazios significam dado ainda não informado. Use zero apenas quando o resultado for realmente zero.")
    with st.form(f"cockpit_edit_{project['id']}_{period}"):
        values = {}
        cols = st.columns(2)
        for i, key in enumerate(FIELDS):
            value = snapshot.get(key)
            text = "" if value is None else str(value).replace(".", ",")
            values[key] = cols[i % 2].text_input(LABELS[key], value=text, key=f"cockpit_value_{project['id']}_{period}_{key}")
        values["as_of"] = st.date_input("Resultados apurados até", value=date.fromisoformat(snapshot["as_of"]) if snapshot.get("as_of") else None,
                                       format="DD/MM/YYYY", key=f"cockpit_date_{project['id']}_{period}")
        values["notes"] = st.text_area("Observações / próxima ação", value=snapshot.get("notes", ""), max_chars=1000)
        saved = st.form_submit_button("Salvar dados", type="primary", use_container_width=True)
    if saved:
        try:
            valid = validate_snapshot(values, period)
            repository.save_month(project["id"], period, valid, snapshot.get("revision", 0))
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(failure(exc))
        else:
            st.session_state["cockpit_notice"] = f"Dados de {project['nome_cliente']} salvos."
            st.rerun()
    if snapshot:
        with st.expander("Histórico de alterações"):
            try:
                rows = repository.history(project["id"], period)
                st.dataframe(pd.DataFrame([{"Versão": r["revision"], "Atualizado em": r["updated_at"],
                    "Origem": r["source"], "Receita": r["revenue"], "Investimento": r["spend"],
                    "Apuração": r["as_of"], "Observação": r["notes"]} for r in rows]), hide_index=True)
            except Exception:
                st.caption("Histórico indisponível no momento.")


def render_import(projects, period):
    st.caption("Baixe o modelo, preencha os resultados e importe. IDs e competência precisam corresponder à carteira disponível. Valores vazios substituem dados anteriores por 'não informado'.")
    st.download_button("Baixar modelo / dados atuais", export_csv(projects, period),
                       file_name=f"carteira-{period:%Y-%m}.csv", mime="text/csv", key="cockpit_model")
    upload = st.file_uploader("Importar CSV preenchido", type=["csv"], key=f"cockpit_upload_{period}")
    if upload is None:
        return
    content = upload.getvalue()
    scope = ",".join(str(p["id"]) for p in projects)
    fingerprint = hashlib.sha256(content + str(period).encode() + scope.encode()).hexdigest()
    try:
        preview = st.session_state.get("_cockpit_import_preview")
        if not preview or preview["fingerprint"] != fingerprint:
            parsed = parse_csv(content, projects, period)
            preview = {"fingerprint": fingerprint, "rows": [
                {"project_id": p["id"], "name": p["nome_cliente"], "snapshot": s,
                 "expected_revision": (p.get("snapshot") or {}).get("revision", 0)} for p, s in parsed]}
            st.session_state["_cockpit_import_preview"] = preview
        st.dataframe(pd.DataFrame([{"Cliente": r["name"], **r["snapshot"]} for r in preview["rows"]]), hide_index=True)
        st.warning(f"A gravação substituirá os dados de {len(preview['rows'])} projeto(s) nesta competência. O lote é gravado integralmente ou não é gravado.")
        if st.button("Gravar lote importado", type="primary"):
            repository.save_batch(period, preview["rows"])
            st.session_state.pop("_cockpit_import_preview", None)
            st.session_state["cockpit_notice"] = "Lote importado e registrado no histórico."
            st.rerun()
        if st.button("Recarregar prévia com versões atuais"):
            st.session_state.pop("_cockpit_import_preview", None)
            st.rerun()
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(failure(exc))


def render_portfolio():
    today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    st.caption("PERFOR / GESTÃO DA CARTEIRA")
    st.title("Cockpit da Carteira")
    st.write("Toda a carteira. Um mês. Uma visão para decidir onde agir.")
    if notice := st.session_state.pop("cockpit_notice", None):
        st.success(notice)
    a, b, c = st.columns([2, 1, 2])
    month = a.selectbox("Competência", range(1, 13), index=today.month-1, format_func=lambda x: MONTHS[x-1], key="cockpit_month")
    year = b.number_input("Ano", min_value=2020, max_value=2100, value=today.year, step=1, key="cockpit_year")
    period = date(int(year), month, 1)
    c.caption("Atualização sob demanda · valores em R$")
    c.button("Atualizar carteira", key="cockpit_refresh", use_container_width=True)
    try:
        projects = repository.read_month(period)
    except Exception:
        st.error("Não foi possível carregar a carteira. Verifique a conexão e atualize a página.")
        return
    if not projects:
        st.info("Nenhum projeto disponível para o seu acesso.")
        return
    a, b, c = st.columns([1.2, 1.2, 2])
    squad = a.selectbox("Squad", ["Todos"] + sorted({p.get("squad") or "Sem squad" for p in projects}))
    analyst = b.selectbox("Responsável", ["Todos"] + sorted({p.get("analista_email") or "Sem responsável" for p in projects}))
    search = c.text_input("Buscar cliente", placeholder="Nome do cliente…")
    selected = [p for p in projects if (squad == "Todos" or (p.get("squad") or "Sem squad") == squad)
                and (analyst == "Todos" or (p.get("analista_email") or "Sem responsável") == analyst)
                and search.casefold() in p["nome_cliente"].casefold()]
    summary = summarize(selected, period, today)
    cols = st.columns(5)
    cols[0].metric("Clientes na visão", len(selected))
    cols[1].metric("Receita faturada", money(summary["revenue"]))
    cols[2].metric("Investimento", money(summary["spend"]))
    cols[3].metric("ROAS consolidado", "—" if summary["roas"] is None else f"{summary['roas']:.2f}x")
    cols[4].metric("Meta de receita", money(summary["target"]))
    st.caption(f"Cobertura de receita + investimento: {summary['covered']}/{len(selected)} clientes. Totais incluem somente valores informados; ROAS usa apenas clientes com receita e investimento, sem média de ROAS individuais.")
    if summary["covered"] < len(selected):
        st.warning("Consolidação parcial: há clientes sem resultados. Nenhum valor foi estimado para preencher lacunas.")
    tabs = st.tabs(["Carteira", "Pendências", "Importar / exportar"])
    with tabs[0]:
        status_filter = st.multiselect("Situação", list(COLORS), placeholder="Todas as situações")
        rows = []
        for p in selected:
            s = p.get("snapshot") or {}
            k = indicators(s, period, today)
            if status_filter and k["status"] not in status_filter:
                continue
            rows.append({"Cliente": p["nome_cliente"], "Squad": p.get("squad") or "—",
                "Situação": f"{COLORS[k['status']]} {k['status']}", "Receita": s.get("revenue"),
                "Meta": s.get("revenue_target"), "Investimento": s.get("spend"), "Orçamento": s.get("budget"),
                "ROAS": k["roas"], "Projeção de receita": k["projection"],
                "Ritmo / meta (%)": None if k["pace"] is None else round(k["pace"]*100, 1),
                "Apurado até": s.get("as_of"), "Origem": s.get("source", "Não informado")})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
            column_config={key: st.column_config.NumberColumn(format="R$ %.2f") for key in ("Receita", "Meta", "Investimento", "Orçamento", "Projeção de receita")})
        st.caption("Ritmo compara a projeção linear da receita com a meta mensal: crítico <90%, atenção <100%. Apuração defasada em mais de 2 dias aparece como desatualizada. Projeção é uma estimativa, não uma previsão garantida.")
        if selected:
            choice = st.selectbox("Cliente para detalhar", [p["id"] for p in selected], format_func=lambda pid: next(p["nome_cliente"] for p in selected if p["id"] == pid))
            project = next(p for p in selected if p["id"] == choice)
            a, b = st.columns(2)
            if a.button("Atualizar metas e resultados", type="primary", use_container_width=True):
                edit_project(project, period)
            if b.button("Abrir painel do projeto", use_container_width=True):
                navigate_to_project(project)
    with tabs[1]:
        pending = []
        for p in selected:
            s = p.get("snapshot") or {}
            missing = [LABELS[k] for k in ("revenue_target", "budget", "revenue", "spend") if s.get(k) is None]
            if indicators(s, period, today)["stale"]:
                missing.append("Atualizar data de apuração / resultados")
            if missing:
                pending.append({"Cliente": p["nome_cliente"], "Responsável": p.get("analista_email"), "Pendência": "; ".join(missing)})
        if pending:
            st.dataframe(pd.DataFrame(pending), hide_index=True, use_container_width=True)
        else:
            st.success("Nenhuma pendência nos campos principais desta visão.")
    with tabs[2]:
        render_import(selected, period)
