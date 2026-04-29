import streamlit as st
from supabase import create_client


# ── Conexão com Supabase (cacheada — uma instância por sessão) ────────────────

@st.cache_resource
def init_connection():
    """Inicializa o client Supabase usando as credenciais do secrets.toml."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


supabase = init_connection()


# ── Autenticação Nativa (Supabase Auth) ───────────────────────────────────────

def verify_user(email_input: str, senha_input: str):
    """
    Realiza o login via Supabase Auth nativo.
    Retorna os dados do usuário (dict) em caso de sucesso, ou None se falhar.
    """
    try:
        response = supabase.auth.sign_in_with_password({"email": email_input, "password": senha_input})
        user = response.user
        if user:
            # Tenta pegar o nome dos metadados, se não existir usa o email
            nome = user.user_metadata.get("full_name") or user.user_metadata.get("name") or email_input.split("@")[0]
            return {
                "id": user.id,
                "email": user.email,
                "nome": nome.title()
            }
        return None
    except Exception as e:
        # Em caso de erro (senha errada, não existe, etc), o Supabase lança uma exceção.
        return None

def reset_password(email_input: str) -> bool:
    """Envia e-mail de recuperação de senha via Supabase Auth."""
    try:
        supabase.auth.reset_password_for_email(email_input)
        return True
    except Exception as e:
        return False
