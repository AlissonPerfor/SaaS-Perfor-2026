import streamlit as st


def apply_global_styles():
    """
    CSS global da Perfor.ia — identidade Moderna, Tecnológica e Dinâmica.
    Fonte: Inter (Google Fonts) · Bootstrap Icons (CDN) · Glassmorphism.
    """
    st.markdown(
        """
        <style>
            /* ── Google Fonts — Inter ── */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            /* ── Bootstrap Icons — CDN ── */
            @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

            /* ── Material Symbols (ícones nativos Streamlit) ── */
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

            .block-container {
                padding-top: 2rem !important;
            }

            /* ── Tipografia global — Inter (padrão SaaS premium) ── */
            .stApp, p, div, label, button,
            h1, h2, h3, h4, h5, h6,
            input, textarea, select, option {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            }

            /* ── Proteção absoluta dos ícones nativos do Streamlit ── */
            span[class*="material-symbols"],
            .material-symbols-rounded,
            [data-testid="stSidebarCollapsedControl"] * {
                font-family: 'Material Symbols Rounded' !important;
            }

            /* ── Proteção Bootstrap Icons ── */
            .bi, [class*="bi-"] {
                font-family: 'bootstrap-icons' !important;
            }

            /* ── Fundo global ── */
            .stApp {
                background-color: #0E0E0E;
            }

            /* ══════════════════════════════════════════════════════════════
               SIDEBAR — ESTÉTICA PREMIUM (Estilo Antigo Perfor)
               ══════════════════════════════════════════════════════════════ */

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0D1117 0%, #0A0E13 50%, #080B0F 100%) !important;
                border-right: 1px solid rgba(0, 200, 83, 0.08) !important;
            }

            [data-testid="stSidebar"] > div:first-child {
                padding-top: 0 !important;
            }

            /* ── Section Labels (NAVEGAÇÃO, CLIENTES, etc.) ── */
            .sidebar-section-label {
                color: #00d592;
                font-size: 0.62rem;
                font-weight: 700;
                letter-spacing: 2.5px;
                text-transform: uppercase;
                margin: 28px 0 10px 16px;
                padding: 0;
            }

            /* ── Project Header ── */
            .project-header {
                padding: 14px 16px;
                margin-bottom: 4px;
                border-bottom: 1px solid rgba(0, 200, 83, 0.08);
            }

            .project-header .project-name {
                font-size: 1rem;
                font-weight: 600;
                color: #FAFAFA;
                margin: 0 0 2px 0;
            }

            .project-header .project-category {
                font-size: 0.72rem;
                color: #4b5563;
                margin: 0;
                font-weight: 400;
            }

            /* ── Expander dentro da sidebar (Squads) ── */
            [data-testid="stSidebar"] [data-testid="stExpander"] {
                background: transparent !important;
                border: 1px solid rgba(255, 255, 255, 0.04) !important;
                border-radius: 8px !important;
                margin-bottom: 4px !important;
            }

            [data-testid="stSidebar"] [data-testid="stExpander"] summary {
                color: #9CA3AF !important;
                font-size: 0.82rem !important;
                font-weight: 500 !important;
                padding: 8px 14px !important;
            }

            [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
                color: #FAFAFA !important;
            }

            /* ── Selectbox na sidebar (dropdown de clientes) ── */
            [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
                color: #00d592 !important;
                font-size: 0.62rem !important;
                font-weight: 700 !important;
                letter-spacing: 2.5px !important;
                text-transform: uppercase !important;
            }

            [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
                background: rgba(0, 200, 83, 0.04) !important;
                border: 1px solid rgba(0, 200, 83, 0.15) !important;
                border-radius: 8px !important;
                color: #FAFAFA !important;
                font-size: 0.85rem !important;
            }

            [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div:hover {
                border-color: rgba(0, 200, 83, 0.35) !important;
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

            .glass-card:hover {
                border-color: rgba(0, 200, 83, 0.55);
                box-shadow: 0 0 24px rgba(0, 200, 83, 0.06);
            }

            .glass-card.highlight {
                background: linear-gradient(
                    135deg,
                    rgba(0, 200, 83, 0.10) 0%,
                    rgba(0, 200, 83, 0.02) 100%
                );
                border: 0.5px solid rgba(0, 200, 83, 0.50);
                box-shadow: 0 0 28px rgba(0, 200, 83, 0.08);
            }

            .glass-card h3 {
                margin: 0 0 10px 0;
                font-size: 0.95rem;
                font-weight: 600;
                color: #00d592;
                letter-spacing: 0.3px;
            }

            .glass-card p {
                margin: 0;
                font-size: 0.875rem;
                line-height: 1.7;
                color: #9CA3AF;
                font-weight: 300;
            }

            .glass-card.kpi {
                text-align: center;
                padding: 20px 16px;
            }

            /* ── Icon container (ícone em círculo colorido) ── */
            .icon-circle {
                width: 40px;
                height: 40px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }

            .icon-circle i {
                font-size: 1.1rem;
            }

            /* ── Sidebar Nav Item (custom HTML) ── */
            .sidebar-nav-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 9px 16px;
                margin: 1px 8px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                border-left: 3px solid transparent;
            }

            .sidebar-nav-item:hover {
                background: rgba(255, 255, 255, 0.04);
            }

            .sidebar-nav-item .nav-icon {
                font-size: 0.9rem;
                color: #4b5563;
                width: 18px;
                text-align: center;
            }

            .sidebar-nav-item .nav-label {
                font-size: 0.84rem;
                color: #9CA3AF;
                font-weight: 400;
                margin: 0;
                padding: 0;
            }

            .sidebar-nav-item.active {
                background: rgba(0, 200, 83, 0.08);
                border-left: 3px solid #00d592;
            }

            .sidebar-nav-item.active .nav-icon {
                color: #00d592;
            }

            .sidebar-nav-item.active .nav-label {
                color: #00d592;
                font-weight: 600;
            }

            .sidebar-nav-item.disabled {
                opacity: 0.35;
                cursor: default;
            }

            .sidebar-nav-item.disabled:hover {
                background: transparent;
            }

            /* ── Em Breve Badge ── */
            .badge-em-breve {
                background: rgba(0, 200, 83, 0.12);
                color: #00d592;
                border-radius: 8px;
                padding: 1px 7px;
                font-size: 0.55rem;
                font-weight: 600;
                letter-spacing: 0.5px;
                margin-left: auto;
            }

            /* ── Sidebar Divider ── */
            .sidebar-divider {
                border: none;
                border-top: 1px solid rgba(255, 255, 255, 0.04);
                margin: 8px 16px;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )
