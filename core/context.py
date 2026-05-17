"""
core/context.py
Módulo centralizado de contexto multi-tenant do SaaS Perfor.

Gerencia 3 variáveis de estado no Streamlit:
  - st.session_state.nivel_navegacao  →  "agencia" | "projeto"
  - st.session_state.projeto_ativo    →  dict (projeto do Supabase) | None
  - st.session_state.projetos_visiveis → list[dict]

Hierarquia:
  - CEO:      Vê todos os projetos + opção agregada na Visão Geral.
  - Head:     Vê apenas projetos do seu squad.
  - Analista: Vê apenas seus projetos vinculados por e-mail.
"""

import os
from pathlib import Path
from typing import Optional

import streamlit as st

from core.database import get_projects

# Caminho absoluto para a pasta de guias de inteligência na raiz do projeto
_GUIDES_DIR = Path(__file__).resolve().parent.parent / "intelligence_guides"


# ── Constantes ────────────────────────────────────────────────────────────────

_ALL_PROJECTS_LABEL = "Todos os Projetos (Agregado)"


# ── Inicialização do Contexto ─────────────────────────────────────────────────

def init_project_context() -> None:
    """
    Carrega os projetos visíveis via RBAC e inicializa o session_state.
    Deve ser chamada UMA vez no main.py, logo após o login ser confirmado.
    """
    user_data = st.session_state.get("user_data") or {}
    user_id   = user_data.get("id", "")
    cargo     = user_data.get("cargo", "analista")
    squad     = user_data.get("squad")
    email     = user_data.get("email", "")

    # Carrega projetos apenas se ainda não estão no session_state
    # ou se o usuário mudou (login diferente)
    cached_email = st.session_state.get("_ctx_cached_email")
    if "projetos_visiveis" not in st.session_state or cached_email != email:
        projetos = get_projects(user_id=user_id, cargo=cargo, squad=squad, email=email)
        st.session_state.projetos_visiveis = projetos
        st.session_state._ctx_cached_email = email

        # Se o projeto_ativo anterior não está mais na lista, reseta
        if "projeto_ativo" in st.session_state:
            ativo = st.session_state.projeto_ativo
            if ativo is not None:
                ids_visiveis = {p.get("id") for p in projetos}
                if ativo.get("id") not in ids_visiveis:
                    del st.session_state["projeto_ativo"]

    # Inicializa projeto_ativo se não existe
    if "projeto_ativo" not in st.session_state:
        st.session_state.projeto_ativo = None

    # Inicializa nível de navegação
    if "nivel_navegacao" not in st.session_state:
        st.session_state.nivel_navegacao = "agencia"

    # Inicializa página ativa (módulo dentro do projeto)
    if "pagina_ativa" not in st.session_state:
        st.session_state.pagina_ativa = "Visão Geral"


# ── Navegação entre Níveis ───────────────────────────────────────────────────

def navigate_to_project(projeto: dict) -> None:
    """Navega para o nível de projeto — abre a sidebar do projeto."""
    st.session_state.projeto_ativo = projeto
    st.session_state.nivel_navegacao = "projeto"
    st.session_state.pagina_ativa = "Dashboard"
    st.rerun()


def navigate_to_agency() -> None:
    """Volta para o nível da agência — sidebar principal."""
    st.session_state.projeto_ativo = None
    st.session_state.nivel_navegacao = "agencia"
    st.session_state.pagina_ativa = "Visão Geral"
    st.rerun()


def set_page(page: str) -> None:
    """Troca a página ativa sem mudar de nível."""
    st.session_state.pagina_ativa = page


# ── Getters Públicos ──────────────────────────────────────────────────────────

def get_active_project() -> Optional[dict]:
    """
    Retorna o projeto ativo (dict completo do Supabase) ou None se
    estiver no nível da agência.
    """
    return st.session_state.get("projeto_ativo")


def get_all_projects() -> list[dict]:
    """
    Retorna a lista completa de projetos visíveis para o usuário.
    Útil para a visão agregada do CEO.
    """
    return st.session_state.get("projetos_visiveis", [])


def get_nav_level() -> str:
    """Retorna o nível de navegação atual: 'agencia' ou 'projeto'."""
    return st.session_state.get("nivel_navegacao", "agencia")


def get_active_page() -> str:
    """Retorna a página ativa atual."""
    return st.session_state.get("pagina_ativa", "Visão Geral")


def is_ceo() -> bool:
    """Retorna True se o usuário logado tem cargo 'ceo'."""
    user_data = st.session_state.get("user_data") or {}
    return user_data.get("cargo", "").strip().lower() == "ceo"


def get_user_cargo() -> str:
    """Retorna o cargo normalizado do usuário logado."""
    user_data = st.session_state.get("user_data") or {}
    return user_data.get("cargo", "analista").strip().lower()


def get_user_squad() -> Optional[str]:
    """Retorna o squad do usuário logado (ou None)."""
    user_data = st.session_state.get("user_data") or {}
    return user_data.get("squad")


def get_squads() -> list[str]:
    """
    Retorna a lista de squads distintos dos projetos visíveis.
    Útil para a navegação da sidebar nível agência.
    """
    projetos = get_all_projects()
    squads = set()
    for p in projetos:
        sq = p.get("squad")
        if sq:
            squads.add(sq)
    return sorted(squads)


def get_projects_by_squad(squad_name: str) -> list[dict]:
    """Retorna projetos filtrados por nome do squad."""
    projetos = get_all_projects()
    return [p for p in projetos if p.get("squad") == squad_name]


def get_project_display_name(projeto: dict) -> str:
    """Retorna o nome de exibição de um projeto."""
    return projeto.get("nome_cliente") or projeto.get("nome") or "Projeto Sem Nome"


# ── Badge de Cargo (centralizado) ────────────────────────────────────────────

def render_cargo_badge(title: str, subtitle: str = "Dados em tempo real via Google Sheets"):
    """
    Renderiza o cabeçalho dinâmico principal de cada página.
    Retorna a coluna direita para permitir a injeção de filtros (como o seletor de data).
    """
    col_left, col_right = st.columns([4, 1])
    
    with col_left:
        st.markdown(f"""
        <div style="margin-bottom:8px;">
            <h1 style="font-size:1.8rem; font-weight:700; color:#FAFAFA; margin:0 0 6px 0; letter-spacing:-0.5px;">{title}</h1>
            <p style="margin:0; color:#6b7280; font-size:0.9rem;">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<hr style="border:none; border-top:1px solid #1f2937; margin-top:8px; margin-bottom:24px;">', unsafe_allow_html=True)
    
    return col_right


# ── Leitura de Prompts para Copilotos IA ─────────────────────────────────────

def get_agent_prompt(file_name: str) -> Optional[str]:
    """
    Lê o conteúdo em texto de um arquivo .md dentro da pasta
    intelligence_guides/ na raiz do projeto.

    Parâmetros:
        file_name: Nome do arquivo (ex: 'MATRIZ_CRIATIVA_IA_guia-inteligencia.md')

    Retorna:
        Conteúdo do arquivo como string, ou None se o arquivo não for encontrado.
    """
    file_path = _GUIDES_DIR / file_name
    if not file_path.exists() or not file_path.is_file():
        return None
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[IA] Erro ao ler guia de inteligência '{file_name}': {e}")
        return None

