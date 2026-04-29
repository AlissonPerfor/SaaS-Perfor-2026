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


# ── Verificação de Usuário ────────────────────────────────────────────────────

def verify_user(email_input: str, senha_input: str) -> bool:
    """
    Busca na tabela 'usuarios' um registro com email e senha correspondentes.
    Retorna True se encontrar, False caso contrário.
    """
    try:
        result = (
            supabase.table("usuarios")
            .select("*")
            .eq("email", email_input)
            .eq("senha", senha_input)
            .execute()
        )
        return len(result.data) > 0
    except Exception as e:
        st.error(f"Erro técnico de conexão: {e}")
        return False
