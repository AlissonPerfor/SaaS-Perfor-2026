import base64
import os

import streamlit as st

from core.database import verify_user


# ── Utilitário ────────────────────────────────────────────────────────────────

def get_image_as_base64(file_path: str) -> str:
    """Converte imagem local em Base64 para injeção segura via HTML."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# ── Verificação de Autenticação ───────────────────────────────────────────────

def check_login() -> bool:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in


# ── Tela de Login ─────────────────────────────────────────────────────────────

def show_login_page() -> None:
    """
    Tela de Login — visual limpo e estável.
    Credenciais temporárias: admin / 123
    """
    bg_base64   = get_image_as_base64("assets/fundo_perfor.jpg")
    logo_base64 = get_image_as_base64("assets/logo_perfor.png")

    st.markdown(
        f"""
        <style>
        /* 1. Trava total de scroll — seletor universal cobre tudo */
        *, *::before, *::after {{
            box-sizing: border-box !important;
        }}
        html {{
            overflow: hidden !important;
            height: 100% !important;
        }}
        body {{
            overflow: hidden !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"],
        section[data-testid="stSidebar"],
        .block-container,
        .stMainBlockContainer {{
            overflow: hidden !important;
            max-height: 100vh !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }}
        /* Zera o padding do bloco principal do Streamlit — culpado do scroll */
        div[data-testid="stAppViewBlockContainer"] > div {{
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            gap: 0 !important;
        }}
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
        }}

        /* 2. Card de vidro (glassmorphism premium) */
        [data-testid="stForm"] {{
            background-color: rgba(14, 14, 14, 0.40) !important;
            backdrop-filter: blur(25px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(25px) saturate(160%) !important;
            border: 1px solid rgba(0, 200, 83, 0.3) !important;
            border-radius: 20px !important;
            padding: 45px !important;
            margin-top: 15vh !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5) !important;
        }}

        /* 3. Estilo do botão */
        div[data-testid="stFormSubmitButton"] {{
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-top: 30px !important;
        }}
        div[data-testid="stFormSubmitButton"] button {{
            background-color: #00C853 !important;
            color: #0E0E0E !important;
            font-weight: 600 !important;
            width: 100% !important;
            white-space: nowrap !important;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.25s ease !important;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{
            background-color: #00E676 !important;
            box-shadow: 0 0 18px rgba(0, 200, 83, 0.4) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Layout centralizado ───────────────────────────────────────────────────
    _, col_center, _ = st.columns([1, 1.2, 1])

    with col_center:
        with st.form("login_form"):

            # Logo
            if logo_base64:
                st.markdown(
                    f'<img src="data:image/png;base64,{logo_base64}" '
                    'style="width:160px; display:block; margin:0 auto 30px auto;">',
                    unsafe_allow_html=True,
                )

            email = st.text_input("E-mail corporativo", placeholder="analista@perforr.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")

            # Botão centralizado via colunas Python (100% confiável)
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                if st.form_submit_button("Acessar Perfor.IA", use_container_width=True):
                    if verify_user(email, senha):
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas. Verifique seu e-mail e senha.")
