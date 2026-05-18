"""
modules/planejamento_anual.py
Módulo de Planejamento Anual — replica a estrutura de tabela KEY/DRIVER
com geração de planejamento via IA especializada (PLANEJAMENTO_ANUAL agent).
"""

import os
from datetime import date
from typing import Optional

import streamlit as st

from core.context import get_active_project, get_project_display_name, render_cargo_badge
from core.sheets import _get_gc, MESES_ABREV


# ── Constantes ────────────────────────────────────────────────────────────────

ANO_ATUAL = date.today().year

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# (label, tipo_key, badge, is_indent, is_category)
ESTRUTURA = [
    ("RECEITA",            None,               None,     False, True),
    ("Receita Captada",    "receita_captada",  "KEY",    False, False),
    ("  Aquisição",        "rec_aquisicao",    None,     True,  False),
    ("  Retenção",         "rec_retencao",     None,     True,  False),
    ("% Retenção",         "pct_retencao",     "DRIVER", False, False),
    ("Receita Faturada",   "receita_faturada", "KEY",    False, False),
    ("% Aprovação",        "pct_aprovacao",    "DRIVER", False, False),

    ("PEDIDOS",            None,               None,     False, True),
    ("Pedidos Captados",   "ped_captados",     "KEY",    False, False),
    ("  Aquisição",        "ped_aquisicao",    None,     True,  False),
    ("  Retenção",         "ped_retencao",     None,     True,  False),
    ("Pedidos Faturados",  "ped_faturados",    "KEY",    False, False),
    ("Ticket Médio",       "ticket_medio",     "DRIVER", False, False),
    ("Taxa Conversão",     "taxa_conversao",   "DRIVER", False, False),

    ("INVESTIMENTOS",      None,               None,     False, True),
    ("Investimento Total", "invest_total",     "KEY",    False, False),
    ("  Mídia Paga",       "invest_midia",     "DRIVER", True,  False),
    ("  Grupos VIP",       "invest_vip",       "DRIVER", True,  False),
    ("  Impulsionamento",  "invest_impulso",   "DRIVER", True,  False),

    ("TRÁFEGO",            None,               None,     False, True),
    ("Sessões Totais",     "sessoes_totais",   None,     False, False),
    ("  Orgânicas",        "sessoes_org",      "DRIVER", True,  False),
    ("CPS Mídia",          "cps_midia",        "DRIVER", False, False),

    ("EFICIÊNCIA",         None,               None,     False, True),
    ("ROAS Captado",       "roas_captado",     "KEY",    False, False),
    ("ROAS Faturado",      "roas_faturado",    "KEY",    False, False),
    ("Comp. Mês a Mês",    "comp_mom",         None,     False, False),
    ("Comp. Ano a Ano",    "comp_yoy",         None,     False, False),
    ("AdCost",             "adcost",           None,     False, False),
    ("Peso / Mês",         "peso_mes",         None,     False, False),
]

# Classificação de tipo para step/format
TIPO_PCT    = {"pct_retencao","pct_aprovacao","taxa_conversao","comp_mom","comp_yoy","adcost","peso_mes"}
TIPO_BRL    = {"receita_captada","rec_aquisicao","rec_retencao","receita_faturada",
               "invest_total","invest_midia","invest_vip","invest_impulso","ticket_medio","cps_midia"}
TIPO_INT    = {"ped_captados","ped_aquisicao","ped_retencao","ped_faturados","sessoes_totais","sessoes_org"}
TIPO_ROAS   = {"roas_captado","roas_faturado"}

# Backgrounds das linhas por badge
BG_KEY    = "rgba(37,99,235,0.06)"
BG_DRIVER = "rgba(0,213,146,0.05)"
BG_INDENT = "rgba(255,255,255,0.01)"

QUARTERS = [
    ("Q1", [0,1,2],   "#3A7D44"),
    ("Q2", [3,4,5],   "#2563EB"),
    ("Q3", [6,7,8],   "#D97706"),
    ("Q4", [9,10,11], "#DC2626"),
]


# ── Session state helpers ─────────────────────────────────────────────────────

def _plan_state_key(pid: str) -> str:
    return f"plan_data_{pid}_{ANO_ATUAL}"


def _get_plan_data(pid: str) -> dict:
    k = _plan_state_key(pid)
    if k not in st.session_state:
        st.session_state[k] = {
            mes: {tipo: None for _, tipo, _, _, cat in ESTRUTURA if tipo and not cat}
            for mes in MESES
        }
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

    # ── Barra de controles ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])

    with c1:
        view = st.radio(
            "view", ["Quarters", "Completo", "Mês"],
            horizontal=True, key="plan_view", label_visibility="collapsed"
        )
    with c2:
        details = st.checkbox("Mostrar detalhes", key="plan_details")
    with c3:
        btn_ia = st.button(
            "✦ Gerar com I.A Especializada",
            key="btn_plan_ia", type="primary", use_container_width=True
        )
    with c4:
        st.markdown(
            "<div style='color:#4b5563;font-size:0.7rem;padding-top:10px;'>Salvo</div>",
            unsafe_allow_html=True
        )

    # ── Botão IA ──────────────────────────────────────────────────────────────
    ia_res_key   = f"ia_res_{pid}"
    ia_modal_key = f"ia_modal_{pid}"

    if btn_ia:
        if not sheet_id:
            st.error("❌ Projeto sem `google_sheet_id` configurado.")
        else:
            with st.spinner("🤖 Coletando histórico e gerando planejamento com IA..."):
                resultado = _gerar_ia(sheet_id, projeto)
            st.session_state[ia_res_key]   = resultado
            st.session_state[ia_modal_key] = True

    if st.session_state.get(ia_modal_key):
        _render_modal(ia_res_key, ia_modal_key)

    # ── Tabela ────────────────────────────────────────────────────────────────
    plan_data = _get_plan_data(pid)

    hoje = date.today()
    if view == "Mês":
        meses_vis = [MESES[hoje.month - 1]]
    else:
        meses_vis = MESES

    _render_header(meses_vis, view, hoje)

    for label, tipo, badge, indent, is_cat in ESTRUTURA:
        if is_cat:
            _render_cat(label)
        elif tipo:
            if indent and not details and badge is None:
                continue
            _render_row(label, tipo, badge, indent, meses_vis, plan_data, pid)


# ── Header da tabela ──────────────────────────────────────────────────────────

def _render_header(meses_vis: list, view: str, hoje: date):
    n = len(meses_vis)

    # Quarter bar (apenas no modo Quarters e Completo)
    if view in ("Quarters", "Completo"):
        q_cols = st.columns([2.2] + [1] * n)
        q_cols[0].markdown(" ")
        ci = 1
        for qname, idxs, color in QUARTERS:
            meses_q = [MESES[i] for i in idxs if MESES[i] in meses_vis]
            if not meses_q:
                continue
            ativo = any(MESES.index(m) == hoje.month - 1 for m in meses_q)
            txt   = f"✓ {qname}" if ativo else f"› {qname}"
            span  = len(meses_q)
            # Agrupa colunas do quarter num único HTML
            with q_cols[ci]:
                st.markdown(
                    f"<div style='background:{color};color:#fff;text-align:center;"
                    f"border-radius:6px 6px 0 0;padding:5px 0;font-size:0.72rem;"
                    f"font-weight:700;letter-spacing:1px;grid-column:span {span};'>{txt}</div>",
                    unsafe_allow_html=True
                )
            ci += span

    # Meses header
    h_cols = st.columns([2.2] + [1] * n)
    h_cols[0].markdown(
        "<div style='color:#4b5563;font-size:0.68rem;font-weight:700;"
        "letter-spacing:1.5px;padding-top:6px;'>MÉTRICA</div>",
        unsafe_allow_html=True
    )
    for i, (col, mes) in enumerate(zip(h_cols[1:], meses_vis)):
        idx   = MESES.index(mes)
        atual = idx == hoje.month - 1
        col.markdown(
            f"<div style='text-align:center;color:{'#00d592' if atual else '#6b7280'};"
            f"font-size:0.75rem;font-weight:{'700' if atual else '400'};"
            f"padding-top:6px;'>{mes}</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06);margin:4px 0 8px 0;'></div>",
                unsafe_allow_html=True)


# ── Linha de categoria ────────────────────────────────────────────────────────

def _render_cat(label: str):
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.03);border-left:3px solid rgba(0,213,146,0.5);"
        f"padding:7px 14px;margin:10px 0 2px 0;border-radius:0 6px 6px 0;'>"
        f"<span style='color:#9CA3AF;font-size:0.68rem;font-weight:700;"
        f"letter-spacing:1.8px;text-transform:uppercase;'>{label}</span></div>",
        unsafe_allow_html=True
    )


# ── Linha de métrica ──────────────────────────────────────────────────────────

def _render_row(label, tipo, badge, indent, meses_vis, plan_data, pid):
    n = len(meses_vis)

    # Cor de fundo da linha por badge
    if badge == "KEY":
        bg = BG_KEY
    elif badge == "DRIVER":
        bg = BG_DRIVER
    elif indent:
        bg = BG_INDENT
    else:
        bg = "transparent"

    # Badge HTML
    badge_html = ""
    if badge == "KEY":
        badge_html = ("<span style='background:#1e3a5f;color:#60a5fa;font-size:0.5rem;"
                      "font-weight:700;padding:1px 5px;border-radius:3px;margin-left:5px;"
                      "vertical-align:middle;'>KEY</span>")
    elif badge == "DRIVER":
        badge_html = ("<span style='background:#14291a;color:#4ade80;font-size:0.5rem;"
                      "font-weight:700;padding:1px 5px;border-radius:3px;margin-left:5px;"
                      "vertical-align:middle;'>DRIVER</span>")

    font_color  = "#9CA3AF" if indent else "#E5E7EB"
    font_size   = "0.77rem" if indent else "0.82rem"
    font_weight = "400" if indent else "500"
    pad_left    = "24px" if indent else "12px"

    # Container com background
    st.markdown(
        f"<div style='background:{bg};border-radius:4px;margin-bottom:1px;'>",
        unsafe_allow_html=True
    )

    cols = st.columns([2.2] + [1] * n)

    # Label
    with cols[0]:
        st.markdown(
            f"<div style='padding-left:{pad_left};padding-top:6px;min-height:32px;'>"
            f"<span style='color:{font_color};font-size:{font_size};font-weight:{font_weight};'>{label.strip()}</span>"
            f"{badge_html}</div>",
            unsafe_allow_html=True
        )

    # Inputs por mês
    for col, mes in zip(cols[1:], meses_vis):
        val = (plan_data.get(mes) or {}).get(tipo)
        ikey = f"pi_{pid}_{mes}_{tipo}"

        with col:
            if tipo in TIPO_PCT:
                v = st.number_input("", value=float(val or 0), min_value=0.0,
                                    max_value=9999.0, step=0.5, format="%.2f",
                                    key=ikey, label_visibility="collapsed")
            elif tipo in TIPO_BRL:
                v = st.number_input("", value=float(val or 0), min_value=0.0,
                                    step=100.0, format="%.0f",
                                    key=ikey, label_visibility="collapsed")
            elif tipo in TIPO_INT:
                v = st.number_input("", value=int(val or 0), min_value=0, step=1,
                                    key=ikey, label_visibility="collapsed")
            elif tipo in TIPO_ROAS:
                v = st.number_input("", value=float(val or 0), min_value=0.0,
                                    step=0.1, format="%.2f",
                                    key=ikey, label_visibility="collapsed")
            else:
                v = st.number_input("", value=float(val or 0), step=0.01,
                                    key=ikey, label_visibility="collapsed")

        if mes not in plan_data:
            plan_data[mes] = {}
        plan_data[mes][tipo] = v

    st.markdown("</div>", unsafe_allow_html=True)


# ── Modal resultado IA ────────────────────────────────────────────────────────

def _render_modal(ia_res_key: str, ia_modal_key: str):
    resultado = st.session_state.get(ia_res_key, "")

    with st.expander("✦ Planejamento Gerado com I.A Especializada", expanded=True):
        st.markdown(
            "<div style='background:rgba(0,213,146,0.06);border:1px solid rgba(0,213,146,0.25);"
            "border-radius:10px;padding:18px 22px;margin-bottom:12px;'>"
            "<p style='color:#00d592;font-size:0.78rem;font-weight:700;margin:0 0 4px 0;'>"
            "✦ PLANEJAMENTO GERADO COM IA ESPECIALIZADA</p>"
            "<p style='color:#6b7280;font-size:0.72rem;margin:0;'>Resumo executivo da projeção gerada</p>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(resultado)

        if st.button("✕ Fechar", key="close_ia_modal"):
            st.session_state[ia_modal_key] = False
            st.rerun()


# ── Geração IA ────────────────────────────────────────────────────────────────

def _get_all_gps_tabs(sheet_id: str) -> dict:
    """Retorna dict {ano: [[linhas]]} de todas as abas '🏆 GPS /'."""
    try:
        gc = _get_gc()
        sh = gc.open_by_key(sheet_id)
        result = {}
        for ws in sh.worksheets():
            title = ws.title
            if "🏆 GPS /" in title:
                parts = title.split("/")
                ano_raw = parts[-1].strip()
                ano = f"20{ano_raw}" if len(ano_raw) == 2 else ano_raw
                try:
                    result[ano] = ws.get_all_values()
                except Exception:
                    pass
        return result
    except Exception as e:
        return {"erro": str(e)}


def _historico_para_texto(tabs: dict) -> str:
    if not tabs or "erro" in tabs:
        err = tabs.get("erro", "sem dados") if tabs else "sem dados"
        return f"Erro ao carregar histórico: {err}"
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


def _gerar_ia(sheet_id: str, projeto: dict) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        return "❌ Biblioteca `google-genai` não instalada. Rode: `pip install google-genai`"

    # API Key
    api_key = None
    try:
        api_key = st.secrets["gemini"]["api_key"]
    except Exception:
        pass
    if not api_key:
        return "❌ Chave Gemini não configurada. Adicione `[gemini]\napi_key = 'SUA_CHAVE'` em `.streamlit/secrets.toml`."

    genai.configure(api_key=api_key)

    nome  = get_project_display_name(projeto)
    nicho = projeto.get("nicho") or projeto.get("categoria") or "E-commerce"

    tabs = _get_all_gps_tabs(sheet_id)
    historico = _historico_para_texto(tabs)
    anos_disponiveis = [a for a in tabs.keys() if a != "erro"]

    # Carrega o guia do agente
    guide = ""
    try:
        with open(os.path.join("intelligence_guides", "PLANEJAMENTO_ANUAL.md"), "r", encoding="utf-8") as f:
            guide = f.read()[:9000]
    except Exception:
        guide = "Guia não encontrado."

    prompt = f"""Você é o AGENTE ARQUITETO DE PLANEJAMENTO ANUAL especializado em e-commerce.

CLIENTE: {nome}
NICHO: {nicho}
ANO DO PLANEJAMENTO: {ANO_ATUAL}
ANOS COM HISTÓRICO DISPONÍVEL: {', '.join(anos_disponiveis) if anos_disponiveis else 'Nenhum'}

=== GUIA DO AGENTE (METODOLOGIA COMPLETA) ===
{guide}

=== HISTÓRICO REAL DO CLIENTE (Planilhas GPS) ===
{historico[:5500]}

=== INSTRUÇÃO FINAL ===
Com base no histórico real acima, gere o PLANEJAMENTO ANUAL COMPLETO para {ANO_ATUAL}.
Siga o formato de saída do guia: Diagnóstico → Tabela dos 9 Drivers (Jan-Dez) → Red Flags → Insight Estratégico.
Use os dados históricos para calibrar sazonalidade. Responda em português brasileiro.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        resp  = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"❌ Erro na API Gemini: {str(e)}"


# ── CSS ───────────────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown("""
    <style>
    /* Inputs compactos na tabela */
    [data-testid="stNumberInput"] {
        margin-bottom: 0 !important;
    }
    [data-testid="stNumberInput"] > label { display: none !important; }
    [data-testid="stNumberInput"] input {
        font-size: 0.76rem !important;
        padding: 4px 6px !important;
        text-align: right !important;
        height: 28px !important;
        background: rgba(255,255,255,0.025) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 4px !important;
        color: #D1D5DB !important;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: rgba(0,213,146,0.5) !important;
        background: rgba(0,213,146,0.04) !important;
        outline: none !important;
    }
    /* Esconde botões +/- */
    [data-testid="stNumberInput"] button {
        display: none !important;
    }
    /* Remove espaço extra dos containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        gap: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)
