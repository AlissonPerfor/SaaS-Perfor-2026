import base64
import os

import streamlit as st

from core.database import verify_user, reset_password, get_user_profile, supabase


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
        st.session_state.user_data = None
    
    # Tenta recuperar sessão ativa do Supabase (útil para mitigar logout no F5 caso o client preserve)
    if not st.session_state.logged_in:
        try:
            session = supabase.auth.get_session()
            if session:
                user = session.user
                nome = user.user_metadata.get("full_name") or user.user_metadata.get("name") or user.email.split("@")[0]

                # Busca centralizada de perfil (cargo já vem em lowercase)
                perfil = get_user_profile(user.id)

                st.session_state.logged_in = True
                st.session_state.user_data = {
                    "id": user.id,
                    "email": user.email,
                    "nome": nome.title(),
                    "cargo": perfil["cargo"],   # ex: 'ceo', 'head', 'analista'
                    "squad": perfil["squad"]    # ex: 'Cold Hunters', 'Rise Gold', None
                }
        except Exception:
            pass

    return st.session_state.logged_in

def logout():
    """Limpa sessão e desloga."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.logged_in = False
    st.session_state.user_data = None
    st.rerun()


@st.dialog("Recuperar Senha")
def render_forgot_password_dialog():
    st.caption("Insira seu e-mail corporativo abaixo para receber um link de redefinição de senha.")
    reset_email = st.text_input("E-mail corporativo", key="reset_email_input_dialog")
    if st.button("Enviar link de redefinição", type="primary", use_container_width=True):
        if reset_email:
            if reset_password(reset_email):
                st.success("Link enviado! Verifique sua caixa de entrada e spam.")
            else:
                st.error("Erro ao enviar. Verifique se o e-mail está correto e cadastrado.")
        else:
            st.warning("Por favor, preencha o e-mail acima.")


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

            # Link 'Esqueci minha senha' (botão do form disfarçado via CSS)
            st.markdown("""
                <style>
                div[data-testid="stElementContainer"]:has(#forgot-pwd-anchor) + div[data-testid="stElementContainer"] button {
                    background: transparent !important;
                    border: none !important;
                    color: #9CA3AF !important;
                    padding: 0 !important;
                    min-height: 0 !important;
                    height: auto !important;
                    font-size: 13px !important;
                    box-shadow: none !important;
                    margin-top: -10px !important;
                    margin-bottom: 25px !important;
                    justify-content: flex-start !important;
                }
                div[data-testid="stElementContainer"]:has(#forgot-pwd-anchor) + div[data-testid="stElementContainer"] button:hover {
                    color: #00C853 !important;
                    text-decoration: underline !important;
                    background: transparent !important;
                }
                div[data-testid="stElementContainer"]:has(#forgot-pwd-anchor) + div[data-testid="stElementContainer"] button:focus {
                    color: #00C853 !important;
                    background: transparent !important;
                }
                </style>
                <div id="forgot-pwd-anchor"></div>
            """, unsafe_allow_html=True)
            forgot_clicked = st.form_submit_button("Esqueci minha senha")

            # Botão centralizado via colunas Python (100% confiável)
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                login_clicked = st.form_submit_button("Acessar Perfor.IA", use_container_width=True)

            if login_clicked:
                user_data = verify_user(email, senha)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user_data
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique seu e-mail e senha.")

        if forgot_clicked:
            render_forgot_password_dialog()
