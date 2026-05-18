"""
modules/planejamento_anual.py
Planejamento Anual — apenas DRIVERs editáveis, KEYs calculados pela cascata.
"""

import os
from datetime import date
from typing import Optional

import streamlit as st

from core.context import get_active_project, get_project_display_name, render_cargo_badge
from core.sheets import _get_gc

# ── Constantes ────────────────────────────────────────────────────────────────

ANO_ATUAL = date.today().year
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

QUARTERS = [
    ("Q1", [0, 1, 2],   "#2d6a3f"),
    ("Q2", [3, 4, 5],   "#1e3a8a"),
    ("Q3", [6, 7, 8],   "#92400e"),
    ("Q4", [9, 10, 11], "#7f1d1d"),
]

# ── Os 9 DRIVERs editáveis ────────────────────────────────────────────────────
# (key, label, step, fmt, min_val, max_val)
DRIVERS = [
    ("pct_retencao",   "% Retenção",        0.5,  "%.2f",  0.0,   100.0),
    ("pct_aprovacao",  "% Aprovação",        0.5,  "%.2f",  0.0,   100.0),
    ("ticket_medio",   "Ticket Médio",       10.0, "%.0f",  0.0,   99999.0),
    ("taxa_conversao", "Taxa Conversão",     0.05, "%.2f",  0.0,   100.0),
    ("invest_midia",   "Mídia Paga",         500.0,"%.0f",  0.0,   9999999.0),
    ("invest_vip",     "Grupos VIP",         100.0,"%.0f",  0.0,   9999999.0),
    ("invest_impulso", "Impulsionamento",    100.0,"%.0f",  0.0,   9999999.0),
    ("sessoes_org",    "Sessões Orgânicas",  100.0,"%.0f",  0.0,   9999999.0),
    ("cps_midia",      "CPS Mídia",          0.05, "%.2f",  0.0,   999.0),
]

DRIVER_KEYS = {d[0] for d in DRIVERS}


# ── Cascata de cálculo ────────────────────────────────────────────────────────

def _calcular(drivers: dict, receita_anual: float = 0.0) -> dict:
    """Aplica a cascata completa a partir dos 9 drivers e retorna todas as métricas."""
    pct_ret  = drivers.get("pct_retencao",   0.0) or 0.0
    pct_apr  = drivers.get("pct_aprovacao",  0.0) or 0.0
    ticket   = drivers.get("ticket_medio",   0.0) or 0.0
    conv     = drivers.get("taxa_conversao", 0.0) or 0.0
    i_midia  = drivers.get("invest_midia",   0.0) or 0.0
    i_vip    = drivers.get("invest_vip",     0.0) or 0.0
    i_imp    = drivers.get("invest_impulso", 0.0) or 0.0
    s_org    = drivers.get("sessoes_org",    0.0) or 0.0
    cps      = drivers.get("cps_midia",      0.0) or 0.0

    # Tráfego
    invest_total = i_midia + i_vip + i_imp
    sessoes_midia = (i_midia / cps) if cps > 0 else 0.0
    sessoes_totais = sessoes_midia + s_org

    # Pedidos
    ped_captados  = int(sessoes_totais * conv / 100)
    ped_aquisicao = int(ped_captados * (1 - pct_ret / 100))
    ped_retencao  = int(ped_captados * pct_ret / 100)
    ped_faturados = int(ped_captados * pct_apr / 100)

    # Receita
    rec_captada   = ped_captados * ticket
    rec_aquisicao = ped_aquisicao * ticket
    rec_retencao  = ped_retencao * ticket
    rec_faturada  = rec_captada * pct_apr / 100

    # Eficiência
    roas_captado  = (rec_captada / invest_total) if invest_total > 0 else 0.0
    roas_faturado = (rec_faturada / invest_total) if invest_total > 0 else 0.0
    adcost        = (invest_total / rec_faturada * 100) if rec_faturada > 0 else 0.0
    peso_mes      = (rec_captada / receita_anual * 100) if receita_anual > 0 else 0.0

    return {
        "invest_total":   invest_total,
        "sessoes_midia":  sessoes_midia,
        "sessoes_totais": sessoes_totais,
        "ped_captados":   ped_captados,
        "ped_aquisicao":  ped_aquisicao,
        "ped_retencao":   ped_retencao,
        "ped_faturados":  ped_faturados,
        "rec_captada":    rec_captada,
        "rec_aquisicao":  rec_aquisicao,
        "rec_retencao":   rec_retencao,
        "rec_faturada":   rec_faturada,
        "roas_captado":   roas_captado,
        "roas_faturado":  roas_faturado,
        "adcost":         adcost,
        "peso_mes":       peso_mes,
    }


# ── Formatadores ──────────────────────────────────────────────────────────────

def _brl(v) -> str:
    if v is None or v == 0:
        return "—"
    try:
        v = float(v)
        if v >= 1_000_000:
            return f"R$ {v/1_000_000:.2f}M".replace(".", ",")
        if v >= 1_000:
            return f"R$ {v:,.0f}".replace(",", ".")
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def _pct(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{float(v):,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def _num(v) -> str:
    if v is None or v == 0:
        return "—"
    try:
        return f"{int(v):,}".replace(",", ".")
    except Exception:
        return "—"


def _roas(v) -> str:
    if v is None or v == 0:
        return "—"
    try:
        return f"{float(v):.2f}x".replace(".", ",")
    except Exception:
        return "—"


# ── Session state ─────────────────────────────────────────────────────────────

def _drivers_key(pid: str) -> str:
    return f"drivers_{pid}_{ANO_ATUAL}"


def _get_drivers(pid: str) -> dict:
    k = _drivers_key(pid)
    if k not in st.session_state:
        st.session_state[k] = {mes: {d[0]: 0.0 for d in DRIVERS} for mes in MESES}
    return st.session_state[k]


# ── Render principal ──────────────────────────────────────────────────────────

def render_planejamento_anual() -> None:
    projeto = get_active_project()
    if not projeto:
        st.warning("Nenhum projeto selecionado.")
        return

    nome     = get_project_display_name(projeto)
    sheet_id = projeto.get("google_sheet_id")
    pid      = str(projeto.get("id", nome))

    render_cargo_badge("✦ Planejamento Anual", f"{nome} · {ANO_ATUAL}")
    _inject_css()

    # ── Controles ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        view = st.radio("view", ["Quarters", "Completo", "Mês"],
                        horizontal=True, key="plan_view", label_visibility="collapsed")
    with c2:
        details = st.checkbox("Mostrar detalhes", key="plan_details")
    with c3:
        btn_ia = st.button("✦ Gerar com I.A Especializada",
                           key="btn_plan_ia", type="primary", use_container_width=True)

    ia_res_key   = f"ia_res_{pid}"
    ia_modal_key = f"ia_modal_{pid}"

    if btn_ia:
        if not sheet_id:
            st.error("❌ Projeto sem `google_sheet_id` configurado.")
        else:
            with st.spinner("🤖 Analisando histórico e gerando planejamento com IA..."):
                resultado = _gerar_ia(sheet_id, projeto)
            st.session_state[ia_res_key]   = resultado
            st.session_state[ia_modal_key] = True
            st.rerun()

    if st.session_state.get(ia_modal_key):
        _render_modal(ia_res_key, ia_modal_key)

    # ── Dados ─────────────────────────────────────────────────────────────────
    all_drivers = _get_drivers(pid)

    hoje = date.today()
    meses_vis = [MESES[hoje.month - 1]] if view == "Mês" else MESES

    # Pré-calcula cascata de cada mês
    # Receita anual total (para peso/mês)
    receita_anual = sum(
        _calcular(all_drivers[m]).get("rec_captada", 0) for m in MESES
    )
    calc_por_mes = {
        m: _calcular(all_drivers[m], receita_anual) for m in MESES
    }

    # ── Tabela ────────────────────────────────────────────────────────────────
    _render_header(meses_vis, view, hoje)

    # === SEÇÃO: DRIVERS (editáveis) ==========================================
    _section("DRIVERS — OS 9 ALAVANCAS")
    _sub("RECEITA")
    _driver_row("% Retenção",        "pct_retencao",   "pct", meses_vis, all_drivers, pid)
    _driver_row("% Aprovação",       "pct_aprovacao",  "pct", meses_vis, all_drivers, pid)
    _sub("PEDIDOS")
    _driver_row("Ticket Médio",      "ticket_medio",   "brl", meses_vis, all_drivers, pid)
    _driver_row("Taxa Conversão",    "taxa_conversao", "pct", meses_vis, all_drivers, pid)
    _sub("INVESTIMENTOS")
    _driver_row("Mídia Paga",        "invest_midia",   "brl", meses_vis, all_drivers, pid)
    _driver_row("Grupos VIP",        "invest_vip",     "brl", meses_vis, all_drivers, pid)
    _driver_row("Impulsionamento",   "invest_impulso", "brl", meses_vis, all_drivers, pid)
    _sub("TRÁFEGO")
    _driver_row("Sessões Orgânicas", "sessoes_org",    "num", meses_vis, all_drivers, pid)
    _driver_row("CPS Mídia",         "cps_midia",      "brl", meses_vis, all_drivers, pid)

    # === SEÇÃO: RESULTADOS (calculados) ======================================
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _section("RESULTADOS — CALCULADOS AUTOMATICAMENTE")

    _sub("RECEITA")
    _key_row("Receita Captada",  meses_vis, calc_por_mes, "rec_captada",  "brl", "KEY")
    if details:
        _key_row("  Aquisição",  meses_vis, calc_por_mes, "rec_aquisicao","brl", None, indent=True)
        _key_row("  Retenção",   meses_vis, calc_por_mes, "rec_retencao", "brl", None, indent=True)
    _key_row("Receita Faturada", meses_vis, calc_por_mes, "rec_faturada", "brl", "KEY")

    _sub("PEDIDOS")
    _key_row("Pedidos Captados",  meses_vis, calc_por_mes, "ped_captados",  "num", "KEY")
    if details:
        _key_row("  Aquisição",   meses_vis, calc_por_mes, "ped_aquisicao", "num", None, indent=True)
        _key_row("  Retenção",    meses_vis, calc_por_mes, "ped_retencao",  "num", None, indent=True)
    _key_row("Pedidos Faturados", meses_vis, calc_por_mes, "ped_faturados", "num", "KEY")

    _sub("INVESTIMENTOS")
    _key_row("Investimento Total", meses_vis, calc_por_mes, "invest_total", "brl", "KEY")

    _sub("TRÁFEGO")
    _key_row("Sessões Totais",  meses_vis, calc_por_mes, "sessoes_totais", "num", None)

    _sub("EFICIÊNCIA")
    _key_row("ROAS Captado",   meses_vis, calc_por_mes, "roas_captado",  "roas", "KEY")
    _key_row("ROAS Faturado",  meses_vis, calc_por_mes, "roas_faturado", "roas", "KEY")
    _key_row("AdCost",         meses_vis, calc_por_mes, "adcost",        "pct",  None)
    _key_row("Peso / Mês",     meses_vis, calc_por_mes, "peso_mes",      "pct",  None)


# ── Header ────────────────────────────────────────────────────────────────────

def _render_header(meses_vis: list, view: str, hoje: date):
    n = len(meses_vis)

    if view in ("Quarters", "Completo"):
        q_cols = st.columns([2.5] + [1] * n)
        q_cols[0].markdown(" ")
        ci = 1
        for qname, idxs, color in QUARTERS:
            meses_q = [MESES[i] for i in idxs if MESES[i] in meses_vis]
            if not meses_q:
                continue
            ativo = any(MESES.index(m) == hoje.month - 1 for m in meses_q)
            txt = f"✓ {qname} (ativo)" if ativo else f"› {qname}"
            with q_cols[ci]:
                st.markdown(
                    f"<div style='background:{color};color:#fff;text-align:center;"
                    f"border-radius:5px 5px 0 0;padding:4px 0;font-size:0.68rem;"
                    f"font-weight:700;letter-spacing:0.8px;'>{txt}</div>",
                    unsafe_allow_html=True)
            ci += len(meses_q)

    h_cols = st.columns([2.5] + [1] * n)
    h_cols[0].markdown(
        "<div style='color:#4b5563;font-size:0.66rem;font-weight:700;"
        "letter-spacing:1.5px;padding-top:5px;'>MÉTRICA</div>",
        unsafe_allow_html=True)
    for col, mes in zip(h_cols[1:], meses_vis):
        idx   = MESES.index(mes)
        atual = idx == hoje.month - 1
        col.markdown(
            f"<div style='text-align:center;color:{'#00d592' if atual else '#6b7280'};"
            f"font-size:0.72rem;font-weight:{'700' if atual else '400'};"
            f"padding-top:5px;'>{mes}</div>",
            unsafe_allow_html=True)
    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.07);margin:4px 0 6px 0;'></div>",
                unsafe_allow_html=True)


def _section(label: str):
    st.markdown(
        f"<div style='background:rgba(0,213,146,0.08);border-left:3px solid #00d592;"
        f"padding:8px 16px;margin:12px 0 4px 0;border-radius:0 8px 8px 0;'>"
        f"<span style='color:#00d592;font-size:0.68rem;font-weight:800;"
        f"letter-spacing:2px;text-transform:uppercase;'>{label}</span></div>",
        unsafe_allow_html=True)


def _sub(label: str):
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.03);border-left:2px solid rgba(255,255,255,0.1);"
        f"padding:5px 14px;margin:8px 0 2px 0;'>"
        f"<span style='color:#6b7280;font-size:0.65rem;font-weight:700;"
        f"letter-spacing:1.5px;text-transform:uppercase;'>{label}</span></div>",
        unsafe_allow_html=True)


# ── Linha DRIVER (editável) ───────────────────────────────────────────────────

def _driver_row(label: str, key: str, fmt: str,
                meses_vis: list, all_drivers: dict, pid: str):
    n     = len(meses_vis)
    cols  = st.columns([2.5] + [1] * n)

    badge = ("<span style='background:#14291a;color:#4ade80;font-size:0.5rem;"
             "font-weight:700;padding:1px 5px;border-radius:3px;margin-left:5px;"
             "vertical-align:middle;'>DRIVER</span>")

    with cols[0]:
        st.markdown(
            f"<div style='padding:5px 4px 5px 12px;background:rgba(0,213,146,0.04);"
            f"border-radius:4px;min-height:32px;display:flex;align-items:center;'>"
            f"<span style='color:#E5E7EB;font-size:0.8rem;font-weight:500;'>{label}</span>"
            f"{badge}</div>",
            unsafe_allow_html=True)

    cfg = next((d for d in DRIVERS if d[0] == key), None)
    step    = cfg[2] if cfg else 1.0
    num_fmt = cfg[3] if cfg else "%.2f"

    for col, mes in zip(cols[1:], meses_vis):
        val  = (all_drivers.get(mes) or {}).get(key, 0.0)
        ikey = f"drv_{pid}_{mes}_{key}"

        with col:
            new_val = st.number_input(
                "", value=float(val or 0), min_value=0.0,
                step=step, format=num_fmt,
                key=ikey, label_visibility="collapsed"
            )

        if mes not in all_drivers:
            all_drivers[mes] = {}
        all_drivers[mes][key] = new_val


# ── Linha KEY (somente leitura) ───────────────────────────────────────────────

def _key_row(label: str, meses_vis: list, calc: dict,
             metric: str, fmt: str, badge_type: Optional[str],
             indent: bool = False):
    n    = len(meses_vis)
    cols = st.columns([2.5] + [1] * n)

    badge_html = ""
    if badge_type == "KEY":
        badge_html = ("<span style='background:#1e3a5f;color:#60a5fa;font-size:0.5rem;"
                      "font-weight:700;padding:1px 5px;border-radius:3px;margin-left:5px;"
                      "vertical-align:middle;'>KEY</span>")

    pad     = "22px" if indent else "12px"
    f_color = "#9CA3AF" if indent else "#E5E7EB"
    f_size  = "0.76rem" if indent else "0.8rem"
    f_w     = "400" if indent else "500"

    with cols[0]:
        st.markdown(
            f"<div style='padding:5px 4px 5px {pad};min-height:32px;display:flex;align-items:center;'>"
            f"<span style='color:{f_color};font-size:{f_size};font-weight:{f_w};'>{label.strip()}</span>"
            f"{badge_html}</div>",
            unsafe_allow_html=True)

    for col, mes in zip(cols[1:], meses_vis):
        val = (calc.get(mes) or {}).get(metric, 0)
        if fmt == "brl":
            txt = _brl(val)
        elif fmt == "pct":
            txt = _pct(val)
        elif fmt == "num":
            txt = _num(val)
        elif fmt == "roas":
            txt = _roas(val)
        else:
            txt = str(val)

        val_color = "#9CA3AF" if indent else "#D1D5DB"
        with col:
            st.markdown(
                f"<div style='text-align:right;padding:5px 6px;min-height:32px;"
                f"display:flex;align-items:center;justify-content:flex-end;'>"
                f"<span style='color:{val_color};font-size:0.74rem;'>{txt}</span></div>",
                unsafe_allow_html=True)


# ── Modal resultado IA ────────────────────────────────────────────────────────

def _render_modal(ia_res_key: str, ia_modal_key: str):
    resultado = st.session_state.get(ia_res_key, "")
    with st.expander("✦ Planejamento Gerado com I.A Especializada", expanded=True):
        st.markdown(
            "<div style='background:rgba(0,213,146,0.07);border:1px solid rgba(0,213,146,0.3);"
            "border-radius:10px;padding:14px 20px;margin-bottom:14px;'>"
            "<p style='color:#00d592;font-size:0.78rem;font-weight:700;margin:0 0 2px 0;'>"
            "✦ PLANEJAMENTO GERADO COM IA ESPECIALIZADA</p>"
            "<p style='color:#6b7280;font-size:0.72rem;margin:0;'>Resumo executivo da projeção</p>"
            "</div>",
            unsafe_allow_html=True)
        st.markdown(resultado)
        if st.button("✕ Fechar", key="close_ia_modal"):
            st.session_state[ia_modal_key] = False
            st.rerun()


# ── Histórico das abas GPS ────────────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def _get_all_gps_tabs(sheet_id: str) -> dict:
    try:
        gc = _get_gc()
        sh = gc.open_by_key(sheet_id)
        result = {}
        for ws in sh.worksheets():
            title = ws.title
            if "🏆 GPS /" in title:
                parts  = title.split("/")
                ano_raw = parts[-1].strip()
                ano    = f"20{ano_raw}" if len(ano_raw) == 2 else ano_raw
                try:
                    result[ano] = ws.get_all_values()
                except Exception:
                    pass
        return result
    except Exception as e:
        return {"erro": str(e)}


def _historico_texto(tabs: dict) -> str:
    if not tabs or "erro" in tabs:
        return f"Erro ao carregar histórico: {tabs.get('erro', 'sem dados') if tabs else 'sem dados'}"
    linhas = []
    for ano in sorted(tabs.keys()):
        data = tabs[ano]
        if not data or len(data) < 5:
            continue
        linhas.append(f"\n=== ANO {ano} ===")
        header = data[3] if len(data) > 3 else []
        linhas.append("Cabeçalho: " + " | ".join(str(c) for c in header[:16]))
        for row in data[4:50]:
            if row and str(row[0]).strip():
                linhas.append(" | ".join(str(c) for c in row[:16]))
    return "\n".join(linhas) or "Sem histórico disponível."


# ── Geração IA (google-genai SDK) ─────────────────────────────────────────────

def _gerar_ia(sheet_id: str, projeto: dict) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "❌ Biblioteca `google-genai` não instalada. Rode: `pip install google-genai`"

    api_key = None
    try:
        api_key = st.secrets["gemini"]["api_key"]
    except Exception:
        pass
    if not api_key:
        return ("❌ Chave Gemini não configurada.\n\n"
                "Adicione em `.streamlit/secrets.toml`:\n```\n[gemini]\napi_key = 'SUA_CHAVE'\n```")

    nome  = get_project_display_name(projeto)
    nicho = projeto.get("nicho") or projeto.get("categoria") or "E-commerce"
    tabs  = _get_all_gps_tabs(sheet_id)
    anos  = [a for a in tabs.keys() if a != "erro"]
    hist  = _historico_texto(tabs)

    guide = ""
    try:
        with open(os.path.join("intelligence_guides", "PLANEJAMENTO_ANUAL.md"), "r", encoding="utf-8") as f:
            guide = f.read()[:9000]
    except Exception:
        pass

    prompt = f"""Você é o AGENTE ARQUITETO DE PLANEJAMENTO ANUAL especializado em e-commerce.

CLIENTE: {nome}
NICHO: {nicho}
ANO DO PLANEJAMENTO: {ANO_ATUAL}
ANOS COM HISTÓRICO: {', '.join(anos) if anos else 'Nenhum'}

=== GUIA DO AGENTE ===
{guide}

=== HISTÓRICO REAL DO CLIENTE ===
{hist[:5500]}

=== INSTRUÇÃO ===
Com base no histórico acima, gere o PLANEJAMENTO ANUAL COMPLETO para {ANO_ATUAL}.
Formato: Diagnóstico → Tabela dos 9 Drivers (Jan-Dez) → Red Flags → Insight Estratégico.
Responda em português brasileiro.
"""

    try:
        client   = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ Erro na API Gemini: {str(e)}"


# ── CSS ───────────────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown("""
    <style>
    [data-testid="stNumberInput"] > label { display: none !important; }
    [data-testid="stNumberInput"] { margin-bottom: 0 !important; }
    [data-testid="stNumberInput"] input {
        font-size: 0.75rem !important;
        padding: 4px 6px !important;
        text-align: right !important;
        height: 30px !important;
        background: rgba(0,213,146,0.04) !important;
        border: 1px solid rgba(0,213,146,0.15) !important;
        border-radius: 4px !important;
        color: #D1D5DB !important;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: rgba(0,213,146,0.5) !important;
        background: rgba(0,213,146,0.07) !important;
        outline: none !important;
    }
    [data-testid="stNumberInput"] button { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
