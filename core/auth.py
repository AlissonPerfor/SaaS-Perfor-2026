import base64
import os

import streamlit as st

from core.database import verify_user, reset_password, get_supabase, clear_supabase_client


# ── Utilitário ────────────────────────────────────────────────────────────────

def get_image_as_base64(file_path: str) -> str:
    """Converte imagem local em Base64 para injeção segura via HTML."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# ── Verificação de Autenticação ───────────────────────────────────────────────

def _clear_user_session() -> None:
    """Remove todo estado local associado ao usuário atual."""
    clear_supabase_client()
    st.session_state.clear()


def check_login() -> bool:
    """
    Valida o estado de login da sessão atual.

    Agora que o client Supabase é isolado por st.session_state, podemos consultar
    a sessão do Auth com segurança sem risco de reutilizar a sessão de outro usuário.
    """
    if not st.session_state.get("logged_in") or not st.session_state.get("user_data"):
        # Não apaga widgets do formulário em cada rerun de um visitante anônimo.
        if st.session_state.get("logged_in") or st.session_state.get("user_data") or "_supabase_client" in st.session_state:
            _clear_user_session()
        return False

    try:
        client = get_supabase()
        # get_session renova tokens expirados; get_user valida o JWT no servidor.
        auth_session = client.auth.get_session()
        if not auth_session or not getattr(auth_session, "user", None):
            _clear_user_session()
            return False

        expected_user_id = (st.session_state.get("user_data") or {}).get("id")
        current_user_id = getattr(auth_session.user, "id", None)

        if not expected_user_id or str(current_user_id) != str(expected_user_id):
            _clear_user_session()
            return False

        verified = client.auth.get_user(auth_session.access_token)
        if not verified or not verified.user or str(verified.user.id) != str(expected_user_id):
            _clear_user_session()
            return False

        return True
    except Exception:
        _clear_user_session()
        return False


def logout():
    """Encerra somente a sessão atual e limpa todo estado local do usuário."""
    try:
        client = st.session_state.get("_supabase_client")
        if client is not None:
            client.auth.sign_out({"scope": "local"})
    except Exception:
        # Mesmo se o revoke remoto falhar, não mantemos sessão/local state no app.
        pass
    finally:
        _clear_user_session()
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
            background-color: #00d592 !important;
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
                    color: #00d592 !important;
                    text-decoration: underline !important;
                    background: transparent !important;
                }
                div[data-testid="stElementContainer"]:has(#forgot-pwd-anchor) + div[data-testid="stElementContainer"] button:focus {
                    color: #00d592 !important;
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
