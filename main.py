import base64
import os

import streamlit as st
from streamlit_option_menu import option_menu

from core.styles import apply_global_styles
import core.auth as auth


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
            /* 1. Esconde Menu e Rodapé padrão */
            #MainMenu {display: none !important;}
            footer {display: none !important;}

            /* 2. Deixa o header transparente, mas NÃO esconde nem quebra a estrutura dele */
            header[data-testid="stHeader"] {
                background-color: transparent !important;
                box-shadow: none !important;
            }

            /* 3. FORÇA A SETA DE ABRIR A SIDEBAR A APARECER */
            /* Quando a sidebar fecha, o Streamlit usa o collapsedControl no lugar do botão padrão */
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"] {
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                z-index: 999999 !important;
            }
            
            [data-testid="collapsedControl"] svg,
            [data-testid="stSidebarCollapsedControl"] svg {
                fill: #00C853 !important; /* Força a cor Verde Perfor na setinha SVG */
                color: #00C853 !important;
            }

            /* 4. Esconde APENAS OS ÍCONES da Toolbar no Canto Superior Direito (Deploy, Fork) */
            /* Se escondermos a stToolbar inteira, a seta some junto em algumas versões! */
            [data-testid="stActionMenu"],
            [data-testid="stToolbarActions"],
            .stAppDeployButton,
            header[data-testid="stHeader"] a {
                display: none !important;
                visibility: hidden !important;
            }

            /* 4. BALAS DE PRATA CONTRA STREAMLIT CLOUD BADGES (Canto Inferior Direito) */
            /* Esconde o Status Widget, "Hosted with Streamlit" e linha decorativa */
            [data-testid="stStatusWidget"],
            [data-testid="stConnectionStatus"],
            [data-testid="stDecoration"] {
                display: none !important;
            }

            /* Esconde explicitamente os avatares e selos flutuantes injetados pelo Cloud */
            div[class*="viewerBadge"],
            div[class^="viewerBadge"],
            .viewerBadge_container__17m9G,
            .viewerBadge_link__1S137,
            a[href*="streamlit.io/cloud"],
            a[href*="github.com/streamlit"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }
            
            /* Remove a margem extra do rodapé para o app ocupar tudo */
            .stApp {
                margin-bottom: -2rem !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ── Estilos Globais ───────────────────────────────────────────────────────────
apply_global_styles()

# ── Roteamento Principal ──────────────────────────────────────────────────────
# Guard: mostra login e interrompe se não autenticado
if not auth.check_login():
    auth.show_login_page()
    st.stop()

# ── Usuário autenticado — painel principal ────────────────────────────────────
if True:
    def render_header():
        """Renderiza o botão de perfil/logout fixo no canto superior direito."""
        user_data = st.session_state.get("user_data") or {}
        nome = user_data.get("nome", "Usuário")
        inicial = nome[0].upper() if nome else "U"
        
        # Envolvemos tudo em um container para mirar e mover TODO o bloco para o topo direito
        with st.container():
            st.markdown(f"""
                <style>
                /* 1. Mira o container vertical exato e joga para o topo direito */
                div[data-testid="stVerticalBlock"]:has(#profile-anchor-hook) {{
                    position: fixed !important;
                    top: 15px !important;
                    right: 25px !important;
                    z-index: 999999 !important;
                    width: 45px !important;
                    height: 45px !important;
                    gap: 0 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                
                /* 2. Formata a bolinha (O botão do popover) */
                div[data-testid="stVerticalBlock"]:has(#profile-anchor-hook) div[data-testid="stPopover"] > div > button {{
                    width: 45px !important;
                    height: 45px !important;
                    border-radius: 50% !important;
                    background: rgba(18, 18, 18, 0.6) !important;
                    backdrop-filter: blur(10px) !important;
                    border: 2px solid #00C853 !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
                }}
                
                /* 3. A inicial dentro do botão */
                div[data-testid="stVerticalBlock"]:has(#profile-anchor-hook) div[data-testid="stPopover"] > div > button p {{
                    color: #00C853 !important;
                    font-weight: 700 !important;
                    font-family: 'Lexend', sans-serif !important;
                    font-size: 18px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                
                /* 4. Esconde o SVG (seta do popover) */
                div[data-testid="stVerticalBlock"]:has(#profile-anchor-hook) div[data-testid="stPopover"] > div > button svg {{
                    display: none !important;
                }}
                
                /* 5. Hover da bolinha */
                div[data-testid="stVerticalBlock"]:has(#profile-anchor-hook) div[data-testid="stPopover"] > div > button:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 0 20px rgba(0, 200, 83, 0.5) !important;
                    background: rgba(18, 18, 18, 0.9) !important;
                }}

                /* 6. Estilo GLOBAL do menu Popover quando aberto */
                div[data-testid="stPopoverBody"] {{
                    background: rgba(20, 20, 20, 0.85) !important;
                    backdrop-filter: blur(10px) saturate(180%) !important;
                    border: 1px solid rgba(0, 200, 83, 0.4) !important;
                    border-radius: 16px !important;
                    padding: 15px !important;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
                    min-width: 200px !important;
                }}
                
                /* 7. Botão Sair transparente dentro do popover */
                div[data-testid="stElementContainer"]:has(#logout-anchor) + div[data-testid="stElementContainer"] button {{
                    background: transparent !important;
                    border: none !important;
                    color: #ff4444 !important;
                    padding: 8px 10px !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    font-family: 'Lexend', sans-serif !important;
                    width: 100% !important;
                    display: flex !important;
                    justify-content: flex-start !important;
                    box-shadow: none !important;
                    transition: all 0.2s ease !important;
                }}
                div[data-testid="stElementContainer"]:has(#logout-anchor) + div[data-testid="stElementContainer"] button:hover {{
                    background: rgba(255, 68, 68, 0.1) !important;
                    border-radius: 8px !important;
                }}
                </style>
                <div id="profile-anchor-hook"></div>
            """, unsafe_allow_html=True)
            
            with st.popover(inicial):
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <div style="width: 36px; height: 36px; border-radius: 50%; background: #00C853; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #000; font-size: 16px; font-family: 'Lexend', sans-serif;">
                            {inicial}
                        </div>
                        <span style="color: #fff; font-weight: 500; font-family: 'Lexend', sans-serif; font-size: 15px;">{nome}</span>
                    </div>
                    <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.1); margin: 10px 0;">
                    <div id="logout-anchor"></div>
                """, unsafe_allow_html=True)
                st.button("Sair da conta", on_click=auth.logout, key="btn_logout_popover")

    # Chama o header customizado
    render_header()

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
