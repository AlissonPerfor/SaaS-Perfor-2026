"""
modules/dashboard.py
Módulo 'Visão Geral' do dashboard Perfor.IA.
Exibe métricas GPS reais via Google Sheets.

Multi-tenancy:
  - CEO (projeto_ativo=None): Visão Agregada de todos os projetos.
  - Head/Analista: Visão Individual do projeto selecionado na sidebar.
"""

import calendar
import textwrap
from datetime import date
from typing import Optional

import streamlit as st

from core.context import (
    get_active_project,
    get_all_projects,
    is_ceo,
    render_cargo_badge,
)
from core.sheets import (
    MESES_ABREV,
    METRICAS,
    get_gps_data,
    fmt_brl,
    fmt_pct,
    fmt_metrica,
)


# ── Ícones e rótulos das Alavancas ───────────────────────────────────────────

ALAVANCAS = [
    {
        "key":    "Custo por Sessão",
        "icon":   "🖥️",
        "label":  "Custo por Sessão",
        "hint":   "CPS",
        "tipo":   "brl",
        "invert": True,   # menor = melhor
    },
    {
        "key":    "Ticket Médio",
        "icon":   "🎫",
        "label":  "Ticket Médio",
        "hint":   "TMD",
        "tipo":   "brl",
        "invert": False,  # maior = melhor
    },
    {
        "key":    "Taxa de Conversão",
        "icon":   "🔄",
        "label":  "Taxa de Conversão",
        "hint":   "CVR",
        "tipo":   "pct",
        "invert": False,  # maior = melhor
    },
]


# ── Função pública principal ──────────────────────────────────────────────────

def render_visao_geral() -> None:
    """
    Renderiza toda a tela 'Visão Geral':
    - Badge de cargo (centralizado via core.context)
    - Seletor de mês
    - CEO sem projeto selecionado → Visão Agregada
    - Demais → Visão Individual do projeto ativo
    """
    render_cargo_badge(
        "✦ Performance GPS",
        "Dados em tempo real via Google Sheets · Aba 🏆 GPS / 26",
    )

    projetos = get_all_projects()
    if not projetos:
        _render_sem_projetos()
        return

    # ── Seletor de Mês ────────────────────────────────────────────────────────
    mes_sel = _render_month_selector()

    # ── Roteamento por contexto ───────────────────────────────────────────────
    projeto = get_active_project()

    if projeto is None and is_ceo():
        _render_visao_agregada(projetos, mes_sel)
    elif projeto is not None:
        _render_visao_individual(projeto, mes_sel)
    else:
        _render_sem_projetos()


# ── Seletor de Mês ───────────────────────────────────────────────────────────

def _render_month_selector() -> str:
    """Renderiza apenas o seletor de mês (projeto agora vive na sidebar)."""
    hoje = date.today()
    mes_padrao_idx = hoje.month - 1
    if hoje.day <= 5 and hoje.month > 1:
        mes_padrao_idx = hoje.month - 2

    _, _, col_mes = st.columns([2, 2, 1])
    with col_mes:
        mes_sel = st.selectbox(
            "📅 Mês",
            options=MESES_ABREV,
            index=mes_padrao_idx,
            key="sel_mes_dashboard",
        )
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    return mes_sel


# ── Visão Individual (projeto específico) ────────────────────────────────────

def _render_visao_individual(projeto: dict, mes_sel: str) -> None:
    """Renderiza o dashboard para um único projeto selecionado."""
    sheet_id: Optional[str] = projeto.get("google_sheet_id")

    if not sheet_id:
        _render_config_pendente(
            projeto.get("nome_cliente") or projeto.get("nome", "Projeto"),
            motivo="google_sheet_id não cadastrado para este projeto."
        )
        return

    with st.spinner(f"Conectando à planilha de {projeto.get('nome_cliente') or projeto.get('nome', '')}..."):
        dados = get_gps_data(sheet_id=sheet_id, mes_abrev=mes_sel)

    if dados.get("erro"):
        _render_config_pendente(
            projeto.get("nome_cliente") or projeto.get("nome", "Projeto"),
            motivo=dados["erro"]
        )
        return

    _render_alavancas(dados)
    _render_pacing(dados, mes_sel)
    _render_resumo_financeiro(dados)


# ── Visão Agregada (CEO — todos os projetos) ─────────────────────────────────

def _render_visao_agregada(projetos: list[dict], mes_sel: str) -> None:
    """
    Visão Agregada para o CEO: busca dados GPS de todos os projetos
    e calcula métricas consolidadas.

    Regras de agregação (aprovadas pelo usuário):
      - Soma: Receita Faturada, Investimento Total
      - Média Ponderada (por Investimento): CPS, Ticket Médio, CVR
      - Pacing: Soma Receita Realizada / Soma Receita Projetada
    """
    # Contadores
    projetos_ok = 0
    projetos_sem_config = 0
    nomes_sem_config: list[str] = []

    # Acumuladores para soma
    soma_receita_real = 0.0
    soma_receita_proj = 0.0
    soma_invest_real  = 0.0
    soma_invest_proj  = 0.0

    # Acumuladores para média ponderada (peso = investimento realizado)
    peso_total = 0.0
    wp_cps = 0.0   # weighted sum: CPS × peso
    wp_tmd = 0.0   # weighted sum: Ticket × peso
    wp_cvr = 0.0   # weighted sum: CVR × peso

    pacing_mes = 0.0

    with st.spinner("Agregando dados de todos os projetos..."):
        for p in projetos:
            sheet_id = p.get("google_sheet_id")
            if not sheet_id:
                projetos_sem_config += 1
                nomes_sem_config.append(p.get("nome_cliente") or p.get("nome", "?"))
                continue

            dados = get_gps_data(sheet_id=sheet_id, mes_abrev=mes_sel)
            if dados.get("erro"):
                projetos_sem_config += 1
                nomes_sem_config.append(p.get("nome_cliente") or p.get("nome", "?"))
                continue

            projetos_ok += 1
            pacing_mes = dados.get("pacing_mes", 0.0)

            # Soma direta
            r_real = dados["realizado"].get("Receita Faturada")
            r_proj = dados["projetado"].get("Receita Faturada")
            i_real = dados["realizado"].get("Investimento Total")
            i_proj = dados["projetado"].get("Investimento Total")

            if r_real is not None:
                soma_receita_real += r_real
            if r_proj is not None:
                soma_receita_proj += r_proj
            if i_real is not None:
                soma_invest_real += i_real
            if i_proj is not None:
                soma_invest_proj += i_proj

            # Média ponderada (peso = investimento realizado do projeto)
            peso = i_real if i_real and i_real > 0 else 0
            if peso > 0:
                peso_total += peso
                cps = dados["realizado"].get("Custo por Sessão")
                tmd = dados["realizado"].get("Ticket Médio")
                cvr = dados["realizado"].get("Taxa de Conversão")
                if cps is not None:
                    wp_cps += cps * peso
                if tmd is not None:
                    wp_tmd += tmd * peso
                if cvr is not None:
                    wp_cvr += cvr * peso

    if projetos_ok == 0:
        st.warning("Nenhum projeto com dados GPS disponíveis para agregar.")
        if nomes_sem_config:
            _render_log_sem_config(nomes_sem_config)
        return

    # ── Monta dict agregado no mesmo formato que get_gps_data retorna ─────
    avg_cps = (wp_cps / peso_total) if peso_total > 0 else None
    avg_tmd = (wp_tmd / peso_total) if peso_total > 0 else None
    avg_cvr = (wp_cvr / peso_total) if peso_total > 0 else None

    dados_agregados = {
        "realizado": {
            "Receita Faturada":   soma_receita_real or None,
            "Investimento Total": soma_invest_real or None,
            "Custo por Sessão":   avg_cps,
            "Ticket Médio":       avg_tmd,
            "Taxa de Conversão":  avg_cvr,
        },
        "projetado": {
            "Receita Faturada":   soma_receita_proj or None,
            "Investimento Total": soma_invest_proj or None,
            "Custo por Sessão":   None,
            "Ticket Médio":       None,
            "Taxa de Conversão":  None,
        },
        "pacing_mes": pacing_mes,
        "erro": None,
    }

    # Header informativo
    st.markdown(
        f"<p style='color:#6b7280; font-size:0.78rem; margin-bottom:16px;'>"
        f"📊 Visão Agregada · <strong style='color:#FAFAFA;'>{projetos_ok}</strong> "
        f"projetos consolidados</p>",
        unsafe_allow_html=True,
    )

    _render_alavancas(dados_agregados)
    _render_pacing(dados_agregados, mes_sel)
    _render_resumo_financeiro(dados_agregados)

    if nomes_sem_config:
        _render_log_sem_config(nomes_sem_config)


# ── Seções de Renderização (compartilhadas) ──────────────────────────────────

def _render_alavancas(dados: dict) -> None:
    """Renderiza os 3 cards grandes das Alavancas de Performance."""
    st.markdown(
        "<p style='color:#6b7280; font-size:0.72rem; letter-spacing:1.5px; "
        "margin-bottom:10px; margin-top:4px;'>⚡ ALAVANCAS DE PERFORMANCE</p>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3, gap="medium")

    for col, alav in zip(cols, ALAVANCAS):
        key      = alav["key"]
        realiz   = dados["realizado"].get(key)
        projet   = dados["projetado"].get(key)
        invert   = alav["invert"]

        val_str  = fmt_metrica(realiz, key)
        proj_str = fmt_metrica(projet, key)

        # Delta
        delta_str   = ""
        delta_color = "#6b7280"
        seta        = ""

        if realiz is not None and projet is not None and projet != 0:
            diff = realiz - projet
            pct  = (diff / projet) * 100

            if invert:
                positivo = diff <= 0   # menor custo = bom
            else:
                positivo = diff >= 0   # maior receita/conversão = bom

            delta_color = "#00C853" if positivo else "#EF4444"
            seta        = "▲" if diff >= 0 else "▼"
            delta_str   = f"{seta} {abs(pct):.1f}% vs Projetado".replace(".", ",")

        with col:
            html_card = f"""
<div class="glass-card" style="text-align:center; padding:28px 20px; position:relative; overflow:hidden;">
<div style="position:absolute; top:-30px; right:-30px; width:90px; height:90px; background:radial-gradient(circle, rgba(0,200,83,0.08) 0%, transparent 70%); border-radius:50%;"></div>
<div style="font-size:2rem; margin-bottom:6px;">{alav['icon']}</div>
<p style="color:#6b7280; font-size:0.7rem; letter-spacing:1.5px; margin-bottom:12px; font-weight:600;">{alav['label'].upper()}</p>
<p style="font-size:2.2rem; font-weight:700; color:#FAFAFA; margin:0 0 6px 0; letter-spacing:-1px;">{val_str}</p>
<p style="color:{delta_color}; font-size:0.8rem; margin:0 0 8px 0; font-weight:500;">{delta_str if delta_str else "Sem projetado"}</p>
<div style="background:rgba(255,255,255,0.04); border-radius:6px; padding:5px 10px; display:inline-block;">
<span style="color:#4b5563; font-size:0.7rem;">Projetado: </span>
<span style="color:#9CA3AF; font-size:0.75rem; font-weight:500;">{proj_str}</span>
</div>
</div>
"""
            st.markdown(html_card, unsafe_allow_html=True)


def _render_pacing(dados: dict, mes_sel: str) -> None:
    """Renderiza o indicador visual de Pacing de Faturamento."""
    pacing_mes   = dados.get("pacing_mes", 0.0)
    receita_real = dados["realizado"].get("Receita Faturada")
    receita_proj = dados["projetado"].get("Receita Faturada")

    # Calcula atingimento da receita
    ating: Optional[float] = None
    if receita_real is not None and receita_proj and receita_proj > 0:
        ating = receita_real / receita_proj

    # Determina status Verde/Vermelho
    if ating is not None and pacing_mes > 0:
        on_track = ating >= pacing_mes
    else:
        on_track = None

    # Cores e textos
    if on_track is True:
        status_color = "#00C853"
        status_bg    = "rgba(0,200,83,0.08)"
        status_bdr   = "rgba(0,200,83,0.35)"
        status_icon  = "🟢"
        status_text  = "Em Ritmo"
    elif on_track is False:
        status_color = "#EF4444"
        status_bg    = "rgba(239,68,68,0.08)"
        status_bdr   = "rgba(239,68,68,0.35)"
        status_icon  = "🔴"
        status_text  = "Abaixo do Ritmo"
    else:
        status_color = "#6b7280"
        status_bg    = "rgba(107,114,128,0.08)"
        status_bdr   = "rgba(107,114,128,0.35)"
        status_icon  = "⚪"
        status_text  = "Sem dados suficientes"

    pacing_pct  = f"{pacing_mes * 100:.1f}%".replace(".", ",")
    ating_pct   = f"{ating * 100:.1f}%".replace(".", ",") if ating is not None else "—"
    receita_str = fmt_brl(receita_real)
    proj_str    = fmt_brl(receita_proj)

    bar_pacing_w = min(pacing_mes * 100, 100)
    bar_ating_w  = min((ating or 0) * 100, 100)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6b7280; font-size:0.72rem; letter-spacing:1.5px; "
        "margin-bottom:10px;'>🎯 PACING DE FATURAMENTO</p>",
        unsafe_allow_html=True,
    )

    html_pacing = f"""
<div class="glass-card" style="background:linear-gradient(135deg, {status_bg} 0%, rgba(12,12,12,0.60) 100%); border-color:{status_bdr}; padding:24px 28px;">
<div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px; margin-bottom:20px;">
<div>
<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
<span style="font-size:1.5rem;">{status_icon}</span>
<span style="color:{status_color}; font-size:1.1rem; font-weight:700; letter-spacing:0.3px;">{status_text}</span>
</div>
<p style="color:#6b7280; font-size:0.82rem; margin:0;">Receita Realizado · <strong style="color:#FAFAFA;">{receita_str}</strong> &nbsp;/&nbsp; Projetado · <strong style="color:#9CA3AF;">{proj_str}</strong></p>
</div>
<div style="text-align:right;">
<p style="color:#6b7280; font-size:0.72rem; letter-spacing:1px; margin:0 0 4px 0;">ATINGIMENTO</p>
<p style="font-size:2rem; font-weight:700; color:{status_color}; margin:0; letter-spacing:-1px;">{ating_pct}</p>
</div>
</div>
<div style="margin-bottom:12px;">
<div style="display:flex; justify-content:space-between; margin-bottom:6px;">
<span style="color:#6b7280; font-size:0.72rem; letter-spacing:1px;">MÊS DECORRIDO ({mes_sel})</span>
<span style="color:#9CA3AF; font-size:0.75rem; font-weight:500;">{pacing_pct}</span>
</div>
<div style="background:rgba(255,255,255,0.06); border-radius:999px; height:10px; width:100%; position:relative; overflow:hidden;">
<div style="position:absolute; top:0; left:0; height:100%; width:{bar_ating_w:.1f}%; background:linear-gradient(90deg, {status_color}cc, {status_color}); border-radius:999px; transition:width 0.6s ease;"></div>
<div style="position:absolute; top:-2px; left:calc({bar_pacing_w:.1f}% - 1px); height:14px; width:2px; background:#FAFAFA; border-radius:2px; opacity:0.6;"></div>
</div>
<div style="display:flex; justify-content:space-between; margin-top:6px;">
<span style="color:{status_color}; font-size:0.68rem;">● Receita {ating_pct}</span>
<span style="color:#FAFAFA; font-size:0.68rem;">| Pacing {pacing_pct}</span>
</div>
</div>
</div>
"""
    st.markdown(html_pacing, unsafe_allow_html=True)


def _render_resumo_financeiro(dados: dict) -> None:
    """Card de resumo: Receita Faturada e Investimento Total lado a lado."""
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6b7280; font-size:0.72rem; letter-spacing:1.5px; "
        "margin-bottom:10px;'>💰 RESUMO FINANCEIRO</p>",
        unsafe_allow_html=True,
    )

    col_rec, col_inv = st.columns(2, gap="medium")

    resumo_items = [
        (col_rec, "💵", "Receita Faturada"),
        (col_inv, "📈", "Investimento Total"),
    ]

    for col, icon, metrica in resumo_items:
        realiz = dados["realizado"].get(metrica)
        projet = dados["projetado"].get(metrica)
        val_str  = fmt_brl(realiz)
        proj_str = fmt_brl(projet)

        # Atingimento
        ating_str   = "—"
        ating_color = "#6b7280"
        if realiz is not None and projet and projet > 0:
            ating = realiz / projet
            ating_str   = f"{ating * 100:.1f}%".replace(".", ",")
            ating_color = "#00C853" if ating >= 0.8 else "#EF4444"

        with col:
            html_resumo = f"""
<div class="glass-card" style="padding:20px 22px;">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
<span style="font-size:1.4rem;">{icon}</span>
<p style="color:#6b7280; font-size:0.72rem; letter-spacing:1.5px; margin:0; font-weight:600;">{metrica.upper()}</p>
</div>
<div style="display:flex; justify-content:space-between; align-items:flex-end;">
<div>
<p style="font-size:1.8rem; font-weight:700; color:#FAFAFA; margin:0 0 4px 0; letter-spacing:-0.5px;">{val_str}</p>
<p style="color:#6b7280; font-size:0.78rem; margin:0;">Projetado: <span style="color:#9CA3AF;">{proj_str}</span></p>
</div>
<div style="text-align:right;">
<p style="color:#4b5563; font-size:0.68rem; margin:0 0 2px 0; letter-spacing:1px;">ATING.</p>
<p style="font-size:1.3rem; font-weight:700; color:{ating_color}; margin:0;">{ating_str}</p>
</div>
</div>
</div>
"""
            st.markdown(html_resumo, unsafe_allow_html=True)


# ── Telas de estado vazio / erro ──────────────────────────────────────────────

def _render_sem_projetos() -> None:
    html_vazio = """
<div class="glass-card" style="text-align:center; padding:48px 32px;">
<div style="font-size:3rem; margin-bottom:16px;">📭</div>
<h3 style="color:#FAFAFA; margin:0 0 8px 0;">Nenhum projeto encontrado</h3>
<p style="color:#6b7280; font-size:0.88rem; margin:0;">Seu perfil de acesso não possui projetos vinculados.<br>Fale com o administrador do sistema.</p>
</div>
"""
    st.markdown(html_vazio, unsafe_allow_html=True)


def _render_config_pendente(nome_projeto: str, motivo: str = "") -> None:
    html_erro = f"""
<div class="glass-card" style="border-color:rgba(251,191,36,0.4); background:linear-gradient(135deg, rgba(251,191,36,0.06) 0%, rgba(12,12,12,0.70) 100%); padding:32px 28px; text-align:center;">
<div style="font-size:2.5rem; margin-bottom:14px;">⚙️</div>
<h3 style="color:#FCD34D; margin:0 0 8px 0; font-size:1rem;">Configuração da Planilha Pendente</h3>
<p style="color:#9CA3AF; font-size:0.85rem; max-width:480px; margin:0 auto 16px auto; line-height:1.7;">Não foi possível carregar os dados do GPS para <strong style="color:#FAFAFA;">{nome_projeto}</strong>.</p>
<div style="background:rgba(0,0,0,0.3); border:1px solid rgba(251,191,36,0.2); border-radius:8px; padding:10px 16px; display:inline-block; max-width:600px;">
<p style="color:#6b7280; font-size:0.75rem; margin:0; font-family:monospace; letter-spacing:0.3px;">{motivo}</p>
</div>
<p style="color:#4b5563; font-size:0.75rem; margin:16px 0 0 0;">Verifique o <code style="color:#FCD34D;">google_sheet_id</code> no Supabase e confirme que o Service Account tem acesso à planilha.</p>
</div>
"""
    st.markdown(html_erro, unsafe_allow_html=True)


def _render_log_sem_config(nomes: list[str]) -> None:
    """Log discreto no final da página informando projetos sem configuração."""
    count = len(nomes)
    lista = ", ".join(nomes[:5])
    if count > 5:
        lista += f" (+{count - 5} outros)"

    html_log = f"""
<div style="margin-top:24px; padding:12px 18px; background:rgba(251,191,36,0.05); border:1px solid rgba(251,191,36,0.15); border-radius:8px;">
<p style="color:#6b7280; font-size:0.75rem; margin:0;">
⚠️ <strong style="color:#FCD34D;">{count} projeto(s)</strong> não incluído(s) por falta de configuração: <span style="color:#9CA3AF;">{lista}</span>
</p>
</div>
"""
    st.markdown(html_log, unsafe_allow_html=True)
