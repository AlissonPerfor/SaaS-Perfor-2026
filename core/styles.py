import streamlit as st


def apply_global_styles():
    """
    CSS global da Perfor.ia — identidade Moderna, Tecnológica e Dinâmica.
    Fonte: Lexend (Google Fonts) · Glassmorphism com vidro fosco premium.
    Inclui estilos para a sidebar dinâmica de navegação por níveis.
    """
    st.markdown(
        """
        <style>
            /* ── Google Fonts — Lexend + Material Symbols (ícones do Streamlit) ── */
            @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

            /* ── Restaura a fonte de ícones nativos do Streamlit ── */
            .material-symbols-rounded,
            span[class*="material-symbols"],
            [data-testid="stSidebarCollapsedControl"] * {
                font-family: 'Material Symbols Rounded' !important;
            }

            /* ── Elementos padrão do Streamlit ── */
            #MainMenu  { visibility: hidden; }
            footer     { visibility: hidden; }
            header     { background-color: transparent !important; border: none !important; box-shadow: none !important; }

            /* ── Remove espaço em branco que sobra após esconder o header ── */
            .block-container {
                padding-top: 2rem !important;
            }

            /* ── Tipografia global segura (sem span para não matar ícones) ── */
            .stApp, p, div, label, button,
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Lexend', sans-serif;
            }

            /* ── Proteção absoluta dos ícones nativos do Streamlit ── */
            span[class*="material-symbols"],
            .material-symbols-rounded,
            [data-testid="stSidebarCollapsedControl"] * {
                font-family: 'Material Symbols Rounded' !important;
            }

            /* ── Fundo global ── */
            .stApp {
                background-color: #0E0E0E;
            }

            /* ── Sidebar ── */
            [data-testid="stSidebar"] {
                background-color: #121212 !important;
            }

            /* ── Card Glassmorphism — Vidro Fosco Premium ── */
            .glass-card {
                background: linear-gradient(
                    135deg,
                    rgba(18, 18, 18, 0.85) 0%,
                    rgba(12, 12, 12, 0.60) 100%
                );
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 0.5px solid rgba(0, 200, 83, 0.30);
                border-radius: 12px;
                padding: 22px 24px;
                margin-bottom: 16px;
                color: #FAFAFA;
                transition: border-color 0.25s ease, box-shadow 0.25s ease;
            }

            /* ── Hover sutil nos cards ── */
            .glass-card:hover {
                border-color: rgba(0, 200, 83, 0.55);
                box-shadow: 0 0 24px rgba(0, 200, 83, 0.06);
            }

            /* ── Variante de destaque ── */
            .glass-card.highlight {
                background: linear-gradient(
                    135deg,
                    rgba(0, 200, 83, 0.10) 0%,
                    rgba(0, 200, 83, 0.02) 100%
                );
                border: 0.5px solid rgba(0, 200, 83, 0.50);
                box-shadow: 0 0 28px rgba(0, 200, 83, 0.08);
            }

            /* ── Tipografia interna dos cards ── */
            .glass-card h3 {
                margin: 0 0 10px 0;
                font-size: 0.95rem;
                font-weight: 600;
                color: #00C853;
                letter-spacing: 0.3px;
            }

            .glass-card p {
                margin: 0;
                font-size: 0.875rem;
                line-height: 1.7;
                color: #9CA3AF;
                font-weight: 300;
            }

            /* ── KPI Cards ── */
            .glass-card.kpi {
                text-align: center;
                padding: 20px 16px;
            }

            /* ══════════════════════════════════════════════════════════════════
               SIDEBAR DINÂMICA — Navegação por Níveis (Estilo Axoly)
               ══════════════════════════════════════════════════════════════════ */

            /* ── Seção label (SQUADS, PERFORMANCE, GESTÃO) ── */
            .sidebar-section-label {
                color: #4b5563;
                font-size: 0.65rem;
                font-weight: 600;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin: 24px 0 8px 4px;
                padding: 0;
            }

            /* ── Item de navegação da sidebar ── */
            .nav-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 14px;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                margin-bottom: 2px;
            }

            .nav-item:hover {
                background: rgba(255, 255, 255, 0.04);
            }

            .nav-item.active {
                background: rgba(0, 200, 83, 0.10);
                border-left: 3px solid #00C853;
            }

            .nav-item .nav-icon {
                font-size: 1.1rem;
                width: 24px;
                text-align: center;
                flex-shrink: 0;
            }

            .nav-item .nav-label {
                font-size: 0.88rem;
                color: #D1D5DB;
                font-weight: 400;
                white-space: nowrap;
            }

            .nav-item.active .nav-label {
                color: #00C853;
                font-weight: 600;
            }

            /* ── Squad expandível ── */
            .squad-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 8px 14px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .squad-header:hover {
                background: rgba(255, 255, 255, 0.04);
            }

            .squad-client {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 14px 8px 38px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .squad-client:hover {
                background: rgba(0, 200, 83, 0.08);
            }

            .squad-client .client-name {
                font-size: 0.82rem;
                color: #9CA3AF;
                font-weight: 400;
            }

            .squad-client.active .client-name {
                color: #00C853;
                font-weight: 500;
            }

            /* ── Projeto header na sidebar nível projeto ── */
            .project-header {
                padding: 16px 14px;
                margin-bottom: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }

            .project-header .project-name {
                font-size: 1.05rem;
                font-weight: 600;
                color: #FAFAFA;
                margin: 0 0 4px 0;
            }

            .project-header .project-category {
                font-size: 0.75rem;
                color: #6b7280;
                margin: 0;
            }

            /* ── Botão Voltar ── */
            .back-button {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 14px;
                margin-top: 16px;
                border-top: 1px solid rgba(255, 255, 255, 0.06);
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .back-button:hover {
                background: rgba(255, 255, 255, 0.04);
                border-radius: 8px;
            }

            .back-button span {
                font-size: 0.82rem;
                color: #6b7280;
                font-weight: 400;
            }

            /* ── Esconde botões do Streamlit dentro de nav items ── */
            /* Estilo para botões Streamlit usados como nav items */
            .stButton > button[kind="secondary"] {
                background: transparent !important;
                border: none !important;
                text-align: left !important;
                padding: 0 !important;
                box-shadow: none !important;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )
