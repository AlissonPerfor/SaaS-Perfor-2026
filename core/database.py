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
            nome = user.user_metadata.get("full_name") or user.user_metadata.get("name") or email_input.split("@")[0]
            
            # Reutiliza a função centralizada de perfil — buscando por email
            perfil = get_user_profile(user.email)
            
            return {
                "id": user.id,
                "email": user.email,
                "nome": nome.title(),
                "cargo": perfil["cargo"],   # ex: 'ceo', 'head', 'analista'
                "squad": perfil["squad"]    # ex: 'Cold Hunters', 'Rise Gold', None
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


def get_user_profile(email: str) -> dict:
    """
    Busca cargo e squad de um usuário na tabela 'usuarios' pelo email.
    (A tabela usa IDs numéricos, não UUIDs do Supabase Auth.)
    Retorna um dict com 'cargo' e 'squad', com defaults seguros.
    """
    defaults = {"cargo": "analista", "squad": None}
    try:
        resp = supabase.table("usuarios").select("cargo, squad").eq("email", email).execute()
        if resp.data:
            perfil = resp.data[0]
            # Normaliza cargo para minúsculas para comparações seguras
            cargo_raw = perfil.get("cargo") or "analista"
            return {
                "cargo": cargo_raw.strip().lower(),
                "squad": perfil.get("squad")
            }
    except Exception as e:
        print(f"[RBAC] Erro ao buscar perfil do usuário '{email}': {e}")
    return defaults


def get_projects(user_id: str, cargo: str, squad: str | None) -> list:
    """
    Busca projetos na tabela 'projetos' aplicando a hierarquia de acesso:
    - CEO:      Acesso total — sem filtros.
    - Head:     Projetos onde squad do projeto == squad do Head (ex: 'Cold Hunters', 'Rise Gold').
    - Analista: Apenas projetos onde analista_id == user_id.

    A comparação de cargo usa .lower() para evitar erros de case (analista/Analista/ANALISTA).
    """
    try:
        query = supabase.table("projetos").select("*")

        # Normaliza cargo para lowercase uma única vez
        cargo_norm = str(cargo).strip().lower() if cargo else "analista"

        if cargo_norm == "ceo":
            # Acesso total — não aplica nenhum filtro
            pass

        elif cargo_norm == "head":
            if squad:
                # Filtra pelo nome exato do squad (case-sensitive no banco, ex: 'Cold Hunters')
                query = query.eq("squad", squad)
            else:
                # Head sem squad definido: bloqueio de segurança
                print(f"[RBAC] AVISO: Head (user_id={user_id}) sem squad atribuído. Acesso negado.")
                return []

        else:
            # Analistas e qualquer cargo desconhecido: filtro pelo próprio user_id
            query = query.eq("analista_id", user_id)

        response = query.execute()
        return response.data or []

    except Exception as e:
        print(f"[RBAC] Erro ao buscar projetos (cargo={cargo}, squad={squad}): {e}")
        return []
