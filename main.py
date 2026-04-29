import base64
import os

import streamlit as st
from streamlit_option_menu import option_menu

from core.styles import apply_global_styles
from core.auth import check_login, show_login_page


def get_image_as_base64(file_path: str) -> str:
    """Converte imagem local em Base64 para injeção segura via HTML."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ── Configuração da Página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perfor SaaS",
    page_icon="assets/icone_p.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_st_style = """
            <style>
            /* 1. Esconde o lixo mas deixa o Header vivo para a seta funcionar */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display: none !important;}
            div[data-testid="stStatusWidget"] {display: none !important;}
            
            /* 2. Força a seta (sidebar button) a ficar visível e com cor contrastante */
            button[kind="header"] {
                visibility: visible !important;
                color: #00C853 !important; /* Cor verde Perfor na seta */
            }

            /* 3. Garante que o fundo do header não atrapalhe */
            header[data-testid="stHeader"] {
                background-color: rgba(0,0,0,0) !important;
                visibility: visible !important;
            }

            /* 4. Remove a linha colorida do topo */
            div[data-testid="stDecoration"] {display: none !important;}
            
            /* 5. Ajuste de respiro do topo */
            .block-container {
                padding-top: 1rem !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ── Estilos Globais ───────────────────────────────────────────────────────────
apply_global_styles()

# ── Roteamento Principal ──────────────────────────────────────────────────────
# Guard: mostra login e interrompe se não autenticado
if not check_login():
    show_login_page()
    st.stop()

# ── Usuário autenticado — painel principal ────────────────────────────────────
if True:

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # Logo via Base64 — sem botão de expandir, nitidez máxima
        _logo_b64 = get_image_as_base64("assets/logo_perfor.png")
        if _logo_b64:
            st.markdown(
                f'<img src="data:image/png;base64,{_logo_b64}" '
                'style="width:180px; display:block; margin-top:5px; margin-bottom:30px; margin-left:15px;">',
                unsafe_allow_html=True,
            )

        # Menu de navegação principal
        selected = option_menu(
            menu_title=None,
            options=["Visão Geral", "Brain", "Criativos", "Financeiro"],
            icons=["grid-1x2", "lightbulb", "play-btn", "wallet2"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#8B8D97", "font-size": "18px"},
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#D1D5DB",
                    "--hover-color": "#1A1A1A",
                },
                "nav-link-selected": {
                    "background-color": "rgba(0, 200, 83, 0.1)",
                    "color": "#00C853",
                    "border-left": "3px solid #00C853",
                    "font-weight": "600",
                },
            },
        )

        # Rodapé da sidebar
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#374151; font-size:0.7rem; text-align:center;"
            "letter-spacing:0.5px;'>© 2026 Perfor Agency · v2.0</p>",
            unsafe_allow_html=True,
        )

    # ── Painel Principal ──────────────────────────────────────────────────────
    # Header da página
    st.markdown(
        f"""
        <div style='margin-bottom: 32px;'>
            <h1 style='font-size:2rem; font-weight:700; color:#FAFAFA;
                       letter-spacing:-0.5px; margin-bottom:4px;'>
                {selected}
            </h1>
            <p style='color:#4b5563; font-size:0.9rem; margin:0;'>
                Performance Intelligence · Perfor Agency
            </p>
            <hr style='border:none; border-top:1px solid #1f2937; margin-top:16px;'>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Roteamento entre módulos ──────────────────────────────────────────────
    if selected == "Visão Geral":
        # Card de status
        st.markdown(
            """
            <div class="glass-card highlight">
                <h3>✦ Estrutura Modular Ativa</h3>
                <p>
                    Todos os módulos foram carregados com sucesso.
                    Navegue pelos itens do menu lateral para acessar
                    <strong style="color:#e5e7eb;">Brain</strong>,
                    <strong style="color:#e5e7eb;">Criativos</strong> e
                    <strong style="color:#e5e7eb;">Financeiro</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # KPIs placeholder
        col1, col2, col3, col4 = st.columns(4)
        kpis = [
            ("Receita MRR", "R$ —", "Aguardando dados"),
            ("Clientes Ativos", "—", "Aguardando dados"),
            ("Churn Rate", "— %", "Aguardando dados"),
            ("NPS Score", "—", "Aguardando dados"),
        ]
        for col, (label, value, sub) in zip([col1, col2, col3, col4], kpis):
            with col:
                st.markdown(
                    f"""
                    <div class="glass-card" style="text-align:center;">
                        <p style="color:#6b7280; font-size:0.75rem;
                                  letter-spacing:1px; margin-bottom:8px;">
                            {label.upper()}
                        </p>
                        <p style="font-size:1.8rem; font-weight:700;
                                  color:#FAFAFA; margin:0 0 4px 0;">
                            {value}
                        </p>
                        <p style="color:#374151; font-size:0.72rem; margin:0;">
                            {sub}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    elif selected == "Brain":
        st.markdown(
            """<div class="glass-card">
                <h3>🧠 Brain — Estratégia &amp; Insights</h3>
                <p>Módulo em construção. Aqui ficarão as análises estratégicas,
                recomendações de budget e alertas de performance por cliente.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    elif selected == "Criativos":
        st.markdown(
            """<div class="glass-card">
                <h3>🎨 Análise de Criativos</h3>
                <p>Módulo em construção. Comparativo de CTR, Hook Rate e
                performance por formato criativo.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    elif selected == "Financeiro":
        st.markdown(
            """<div class="glass-card">
                <h3>💳 Financeiro</h3>
                <p>Módulo em construção. MRR, churn, LTV e projeções de receita.</p>
            </div>""",
            unsafe_allow_html=True,
        )
