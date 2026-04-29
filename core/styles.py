import streamlit as st


def apply_global_styles():
    """
    CSS global da Perfor.ia — identidade Moderna, Tecnológica e Dinâmica.
    Fonte: Lexend (Google Fonts) · Glassmorphism com vidro fosco premium.
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
            header     { visibility: hidden; }

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
        </style>
        """,
        unsafe_allow_html=True,
    )
