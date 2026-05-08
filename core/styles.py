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

            .glass-card.kpi {
                text-align: center;
                padding: 20px 16px;
            }

            /* ══════════════════════════════════════════════════════════════
               SIDEBAR DINÂMICA
               ══════════════════════════════════════════════════════════════ */

            .sidebar-section-label {
                color: #4b5563;
                font-size: 0.65rem;
                font-weight: 600;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin: 24px 0 8px 4px;
                padding: 0;
            }

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

        </style>
        """,
        unsafe_allow_html=True,
    )
