"""
modules/squad_dashboard.py
Dashboard intermediário de Squad — exibe KPIs agregados e lista de clientes.
Inspirado na tela de Squad da referência Axoly.
"""

import streamlit as st

from core.context import (
    get_projects_by_squad,
    get_all_projects,
    get_user_cargo,
    get_user_squad,
    get_project_display_name,
    navigate_to_project,
    is_ceo,
)
from core.sheets import get_gps_data, fmt_brl, MESES_ABREV
from datetime import date


def render_squad_dashboard(squad_name: str | None = None) -> None:
    """
    Renderiza o dashboard de um squad específico ou a visão geral da agência.
    Mostra KPIs agregados + lista de clientes como cards clicáveis.
    """
    cargo = get_user_cargo()

    if squad_name:
        projetos = get_projects_by_squad(squad_name)
        titulo = f"Squad {squad_name}"
        subtitulo = "Gestão de Clientes"
    else:
        projetos = get_all_projects()
        titulo = "Visão Geral"
        subtitulo = "Todos os projetos da agência"

    # ── Header do Squad ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-size:1.8rem; font-weight:700; color:#FAFAFA; margin:0 0 4px 0; letter-spacing:-0.5px;">
            {titulo}
        </h1>
        <p style="color:#4b5563; font-size:0.88rem; margin:0;">
            {subtitulo} · {len(projetos)} cliente(s) ativo(s)
        </p>
        <hr style="border:none; border-top:1px solid #1f2937; margin-top:16px;">
    </div>
    """, unsafe_allow_html=True)

    if not projetos:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:48px 32px;">
            <div style="font-size:3rem; margin-bottom:16px;">📭</div>
            <h3 style="color:#FAFAFA; margin:0 0 8px 0;">Nenhum cliente encontrado</h3>
            <p style="color:#6b7280; font-size:0.88rem; margin:0;">Este squad não possui projetos vinculados.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── KPIs do Squad ─────────────────────────────────────────────────────────
    _render_squad_kpis(projetos)

    # ── Lista de Clientes ─────────────────────────────────────────────────────
    st.markdown("""
    <p style="color:#4b5563; font-size:0.68rem; letter-spacing:1.5px;
    margin-top:28px; margin-bottom:12px;">📋 CLIENTES</p>
    """, unsafe_allow_html=True)

    for projeto in projetos:
        _render_client_card(projeto)


def _render_squad_kpis(projetos: list[dict]) -> None:
    """Renderiza KPIs rápidos do squad."""
    total_clientes = len(projetos)
    com_sheet = sum(1 for p in projetos if p.get("google_sheet_id"))
    com_meta = sum(1 for p in projetos if p.get("meta_account_id"))
    sem_config = total_clientes - com_sheet

    kpis = [
        ("👥", "CLIENTES", str(total_clientes), "#00C853"),
        ("📊", "COM GPS", str(com_sheet), "#3B82F6"),
        ("📱", "COM META", str(com_meta), "#8B5CF6"),
        ("⚠️", "PENDENTES", str(sem_config), "#FCD34D" if sem_config > 0 else "#6b7280"),
    ]

    cols = st.columns(4, gap="medium")
    for col, (icon, label, value, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:18px 12px;">
                <div style="font-size:1.4rem; margin-bottom:6px;">{icon}</div>
                <p style="font-size:1.6rem; font-weight:700; color:{color}; margin:0 0 4px 0;">{value}</p>
                <p style="color:#4b5563; font-size:0.65rem; letter-spacing:1.5px; margin:0; font-weight:600;">{label}</p>
            </div>
            """, unsafe_allow_html=True)


def _render_client_card(projeto: dict) -> None:
    """Renderiza um card de cliente clicável."""
    nome = get_project_display_name(projeto)
    categoria = projeto.get("nicho") or projeto.get("categoria") or "—"
    squad = projeto.get("squad") or "—"
    has_sheet = bool(projeto.get("google_sheet_id"))
    has_meta = bool(projeto.get("meta_account_id"))

    # Status badges
    badges_html = ""
    if has_sheet:
        badges_html += '<span style="background:rgba(59,130,246,0.15); color:#3B82F6; border:1px solid rgba(59,130,246,0.3); border-radius:12px; padding:2px 8px; font-size:0.65rem; font-weight:500;">GPS</span> '
    if has_meta:
        badges_html += '<span style="background:rgba(139,92,246,0.15); color:#8B5CF6; border:1px solid rgba(139,92,246,0.3); border-radius:12px; padding:2px 8px; font-size:0.65rem; font-weight:500;">Meta</span> '
    if not has_sheet and not has_meta:
        badges_html += '<span style="background:rgba(251,191,36,0.15); color:#FCD34D; border:1px solid rgba(251,191,36,0.3); border-radius:12px; padding:2px 8px; font-size:0.65rem; font-weight:500;">Pendente</span>'

    # Initial avatar
    inicial = nome[0].upper() if nome else "?"

    st.markdown(f"""
    <div class="glass-card" style="padding:16px 20px; cursor:pointer;" id="client-{projeto.get('id', '')}">
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="width:42px; height:42px; border-radius:10px; background:rgba(0,200,83,0.12); border:1px solid rgba(0,200,83,0.25); display:flex; align-items:center; justify-content:center; font-weight:700; color:#00C853; font-size:1.1rem; flex-shrink:0;">
                {inicial}
            </div>
            <div style="flex:1; min-width:0;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <p style="font-size:0.95rem; font-weight:600; color:#FAFAFA; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{nome}</p>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#6b7280; font-size:0.75rem;">{categoria}</span>
                    <span style="color:#2d3748;">·</span>
                    {badges_html}
                </div>
            </div>
            <div style="color:#4b5563; font-size:1rem;">›</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botão Streamlit real para capturar o click
    if st.button(
        f"Abrir {nome}",
        key=f"open_project_{projeto.get('id', nome)}",
        use_container_width=True,
        type="secondary",
    ):
        navigate_to_project(projeto)
