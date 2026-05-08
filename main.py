import base64
import os

import streamlit as st

from core.styles import apply_global_styles
from core.context import (
    init_project_context,
    get_active_project,
    get_all_projects,
    get_nav_level,
    get_active_page,
    get_squads,
    get_projects_by_squad,
    get_project_display_name,
    get_user_cargo,
    get_user_squad,
    navigate_to_project,
    navigate_to_agency,
    set_page,
    is_ceo,
    render_cargo_badge,
)
import core.auth as auth


def get_image_as_base64(file_path: str) -> str:
    """Converte imagem local em Base64 para injeção segura via HTML."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ── Configuração da Página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perfor SaaS",
    page_icon="assets/icone_p.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_st_style = """
            <style>
            /* 1. Esconde Menu e Rodapé padrão */
            #MainMenu {display: none !important;}
            footer {display: none !important;}

            /* 2. Deixa o header transparente, mas NÃO esconde nem quebra a estrutura dele */
            header[data-testid="stHeader"] {
                background-color: transparent !important;
                box-shadow: none !important;
            }

            /* 3. FORÇA A SETA DE ABRIR A SIDEBAR A APARECER */
            /* Quando a sidebar fecha, o Streamlit usa o collapsedControl no lugar do botão padrão */
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"] {
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                z-index: 999999 !important;
            }
            
            [data-testid="collapsedControl"] svg,
            [data-testid="stSidebarCollapsedControl"] svg {
                fill: #00C853 !important; /* Força a cor Verde Perfor na setinha SVG */
                color: #00C853 !important;
            }

            /* 4. Esconde APENAS OS ÍCONES da Toolbar no Canto Superior Direito (Deploy, Fork) */
            /* Se escondermos a stToolbar inteira, a seta some junto em algumas versões! */
            [data-testid="stActionMenu"],
            [data-testid="stToolbarActions"],
            .stAppDeployButton,
            header[data-testid="stHeader"] a {
                display: none !important;
                visibility: hidden !important;
            }

            /* 4. BALAS DE PRATA CONTRA STREAMLIT CLOUD BADGES (Canto Inferior Direito) */
            /* Esconde o Status Widget, "Hosted with Streamlit" e linha decorativa */
            [data-testid="stStatusWidget"],
            [data-testid="stConnectionStatus"],
            [data-testid="stDecoration"] {
                display: none !important;
            }

            /* Esconde explicitamente os avatares e selos flutuantes injetados pelo Cloud */
            div[class*="viewerBadge"],
            div[class^="viewerBadge"],
            .viewerBadge_container__17m9G,
            .viewerBadge_link__1S137,
            a[href*="streamlit.io/cloud"],
            a[href*="github.com/streamlit"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }
            
            /* Remove a margem extra do rodapé para o app ocupar tudo */
            .stApp {
                margin-bottom: -2rem !important;
            }

            /* ── Estilo dos botões de navegação na sidebar (transparentes) ── */
            [data-testid="stSidebar"] .stButton > button {
                background: transparent !important;
                border: none !important;
                color: #D1D5DB !important;
                text-align: left !important;
                padding: 10px 14px !important;
                font-size: 0.88rem !important;
                font-weight: 400 !important;
                font-family: 'Lexend', sans-serif !important;
                border-radius: 10px !important;
                width: 100% !important;
                display: flex !important;
                justify-content: flex-start !important;
                box-shadow: none !important;
                transition: all 0.2s ease !important;
                margin: 0 !important;
                min-height: 0 !important;
                line-height: 1.4 !important;
            }

            [data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(255, 255, 255, 0.04) !important;
                color: #FAFAFA !important;
            }

            /* Botão de voltar */
            [data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background: transparent !important;
                border: none !important;
                color: #6b7280 !important;
                font-size: 0.82rem !important;
                padding: 10px 14px !important;
                border-top: 1px solid rgba(255,255,255,0.06) !important;
                border-radius: 0 !important;
                margin-top: 12px !important;
            }

            [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
                color: #00C853 !important;
                background: rgba(0, 200, 83, 0.05) !important;
            }

            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ── Estilos Globais ───────────────────────────────────────────────────────────
apply_global_styles()

# ── Roteamento Principal ──────────────────────────────────────────────────────
# Guard: mostra login e interrompe se não autenticado
if not auth.check_login():
    auth.show_login_page()
    st.stop()

# ── Inicializa o contexto multi-tenant (carrega projetos via RBAC) ────────────
init_project_context()

# ── Usuário autenticado — painel principal ────────────────────────────────────

def render_header():
    """Renderiza o botão de perfil/logout fixo no canto superior direito."""
    user_data = st.session_state.get("user_data") or {}
    nome = user_data.get("nome", "Usuário")
    inicial = nome[0].upper() if nome else "U"
    
    st.markdown(f"""
        <style>
        /* 1. Remove qualquer espaço ocupado pelo container do popover no fluxo normal da página */
        div[data-testid="stElementContainer"]:has(div[data-testid="stPopover"]) {{
            position: absolute !important;
            width: 0px !important;
            height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }}
        
        /* 2. Fixa o popover EXATAMENTE no canto superior direito */
        div[data-testid="stPopover"] {{
            position: fixed !important;
            top: 15px !important;
            right: 25px !important;
            z-index: 999999 !important;
            width: 45px !important;
            height: 45px !important;
            display: block !important;
        }}
        
        /* 3. Formata a bolinha (O botão do popover) */
        div[data-testid="stPopover"] > div > button {{
            width: 45px !important;
            height: 45px !important;
            border-radius: 50% !important;
            background: rgba(18, 18, 18, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            border: 2px solid #00C853 !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
        }}
        
        /* 4. A inicial dentro do botão */
        div[data-testid="stPopover"] > div > button p {{
            color: #00C853 !important;
            font-weight: 700 !important;
            font-family: 'Lexend', sans-serif !important;
            font-size: 18px !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* 5. Esconde o SVG (seta do popover) */
        div[data-testid="stPopover"] > div > button svg {{
            display: none !important;
        }}
        
        /* 6. Hover da bolinha */
        div[data-testid="stPopover"] > div > button:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 200, 83, 0.5) !important;
            background: rgba(18, 18, 18, 0.9) !important;
        }}

        /* 7. Estilo GLOBAL do menu Popover quando aberto */
        div[data-testid="stPopoverBody"] {{
            background: rgba(20, 20, 20, 0.85) !important;
            backdrop-filter: blur(10px) saturate(180%) !important;
            border: 1px solid rgba(0, 200, 83, 0.4) !important;
            border-radius: 16px !important;
            padding: 15px !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
            min-width: 200px !important;
        }}
        
        /* 8. Botão Sair transparente dentro do popover */
        div[data-testid="stElementContainer"]:has(#logout-anchor) + div[data-testid="stElementContainer"] button {{
            background: transparent !important;
            border: none !important;
            color: #ff4444 !important;
            padding: 8px 10px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            font-family: 'Lexend', sans-serif !important;
            width: 100% !important;
            display: flex !important;
            justify-content: flex-start !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stElementContainer"]:has(#logout-anchor) + div[data-testid="stElementContainer"] button:hover {{
            background: rgba(255, 68, 68, 0.1) !important;
            border-radius: 8px !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    with st.popover(inicial):
        cargo = get_user_cargo()
        cargo_display = {"ceo": "CEO", "head": "Head", "analista": "Analista"}.get(cargo, cargo)
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: #00C853; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #000; font-size: 16px; font-family: 'Lexend', sans-serif;">
                    {inicial}
                </div>
                <div>
                    <span style="color: #fff; font-weight: 500; font-family: 'Lexend', sans-serif; font-size: 15px; display:block;">{nome}</span>
                    <span style="color: #6b7280; font-size: 0.72rem;">{cargo_display}</span>
                </div>
            </div>
            <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.1); margin: 10px 0;">
            <div id="logout-anchor"></div>
        """, unsafe_allow_html=True)
        st.button("Sair da conta", on_click=auth.logout, key="btn_logout_popover")

# Chama o header customizado
render_header()

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DA SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def _render_sidebar_agency():
    """Sidebar nível Agência: Visão Geral, Squads expandíveis, CEO Panel."""
    cargo = get_user_cargo()

    # ── Menu Principal ────────────────────────────────────────────────────
    if st.button("📊  Visão Geral", key="nav_visao_geral", use_container_width=True):
        set_page("Visão Geral")
        st.rerun()

    # ── SQUADS ────────────────────────────────────────────────────────────
    st.markdown('<p class="sidebar-section-label">SQUADS</p>', unsafe_allow_html=True)

    squads = get_squads()
    if squads:
        for squad_name in squads:
            projetos_squad = get_projects_by_squad(squad_name)

            with st.expander(f"👥 {squad_name}", expanded=False):
                # Botão para ver o dashboard do squad
                if st.button(
                    f"📋 Dashboard do Squad",
                    key=f"squad_dash_{squad_name}",
                    use_container_width=True,
                ):
                    st.session_state._squad_view = squad_name
                    set_page("Squad Dashboard")
                    st.rerun()

                # Lista de clientes dentro do squad
                for p in projetos_squad:
                    nome = get_project_display_name(p)
                    if st.button(
                        f"  📁 {nome}",
                        key=f"nav_proj_{p.get('id', nome)}",
                        use_container_width=True,
                    ):
                        navigate_to_project(p)
    else:
        # Analistas sem squads — lista projetos direto
        projetos = get_all_projects()
        for p in projetos:
            nome = get_project_display_name(p)
            if st.button(
                f"📁  {nome}",
                key=f"nav_proj_{p.get('id', nome)}",
                use_container_width=True,
            ):
                navigate_to_project(p)

    # ── CEO Panel ─────────────────────────────────────────────────────────
    if cargo == "ceo":
        st.markdown('<p class="sidebar-section-label">GESTÃO</p>', unsafe_allow_html=True)

        if st.button("👑  CEO Dashboard", key="nav_ceo_dash", use_container_width=True):
            set_page("CEO Dashboard")
            st.rerun()

    # ── Em Breve ──────────────────────────────────────────────────────────
    st.markdown('<p class="sidebar-section-label">EM BREVE</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 4px 14px;">
        <p style="color:#374151; font-size:0.78rem; margin:6px 0;">📅 Calendário</p>
        <p style="color:#374151; font-size:0.78rem; margin:6px 0;">💬 Reuniões</p>
        <p style="color:#374151; font-size:0.78rem; margin:6px 0;">🔔 Notificações</p>
    </div>
    """, unsafe_allow_html=True)


def _render_sidebar_project():
    """Sidebar nível Projeto: header do projeto + módulos + botão voltar."""
    projeto = get_active_project()
    if not projeto:
        navigate_to_agency()
        return

    nome = get_project_display_name(projeto)
    categoria = projeto.get("nicho") or projeto.get("categoria") or ""
    squad = projeto.get("squad") or ""
    inicial = nome[0].upper() if nome else "?"

    # ── Header do Projeto ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="project-header">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:38px; height:38px; border-radius:10px; background:rgba(0,200,83,0.12);
                        border:1px solid rgba(0,200,83,0.25); display:flex; align-items:center;
                        justify-content:center; font-weight:700; color:#00C853; font-size:1rem; flex-shrink:0;">
                {inicial}
            </div>
            <div>
                <p class="project-name">{nome}</p>
                <p class="project-category">{categoria}{(' · ' + squad) if squad else ''}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PERFORMANCE ───────────────────────────────────────────────────────
    st.markdown('<p class="sidebar-section-label">PERFORMANCE</p>', unsafe_allow_html=True)

    modules_perf = [
        ("📊", "GPS Dashboard", "nav_gps"),
        ("🧠", "Brain", "nav_brain"),
        ("🎨", "Criativos", "nav_criativos"),
        ("💰", "Financeiro", "nav_financeiro"),
    ]

    for icon, label, key in modules_perf:
        if st.button(
            f"{icon}  {label}",
            key=key,
            use_container_width=True,
        ):
            set_page(label)
            st.rerun()

    # ── GESTÃO ────────────────────────────────────────────────────────────
    st.markdown('<p class="sidebar-section-label">GESTÃO</p>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 4px 14px;">
        <p style="color:#374151; font-size:0.78rem; margin:6px 0;">📋 Planejamento <span style="background:rgba(0,200,83,0.15); color:#00C853; border-radius:8px; padding:1px 6px; font-size:0.6rem; margin-left:4px;">Em Breve</span></p>
        <p style="color:#374151; font-size:0.78rem; margin:6px 0;">📅 Calendário <span style="background:rgba(0,200,83,0.15); color:#00C853; border-radius:8px; padding:1px 6px; font-size:0.6rem; margin-left:4px;">Em Breve</span></p>
        <p style="color:#374151; font-size:0.78rem; margin:6px 0;">📝 Reuniões <span style="background:rgba(0,200,83,0.15); color:#00C853; border-radius:8px; padding:1px 6px; font-size:0.6rem; margin-left:4px;">Em Breve</span></p>
    </div>
    """, unsafe_allow_html=True)

    # ── Botão Voltar ──────────────────────────────────────────────────────
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    if st.button("← Voltar para a Agência", key="nav_back_agency", type="primary", use_container_width=True):
        navigate_to_agency()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR DINÂMICA — Muda conteúdo com base no nível de navegação
# ══════════════════════════════════════════════════════════════════════════════

nivel = get_nav_level()
pagina_ativa = get_active_page()

with st.sidebar:
    # Logo — sempre presente
    _logo_b64 = get_image_as_base64("assets/logo_perfor.png")
    if _logo_b64:
        st.markdown(
            f'<img src="data:image/png;base64,{_logo_b64}" '
            'style="width:160px; display:block; margin-top:5px; margin-bottom:20px; margin-left:15px;">',
            unsafe_allow_html=True,
        )

    # ── NÍVEL AGÊNCIA ─────────────────────────────────────────────────────
    if nivel == "agencia":
        _render_sidebar_agency()

    # ── NÍVEL PROJETO ─────────────────────────────────────────────────────
    elif nivel == "projeto":
        _render_sidebar_project()

    # Rodapé da sidebar
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#374151; font-size:0.65rem; text-align:center;"
        "letter-spacing:0.5px;'>© 2026 Perfor Agency · v2.0</p>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAINEL PRINCIPAL — Renderiza o conteúdo da página ativa
# ══════════════════════════════════════════════════════════════════════════════

# Header da página
_page_title = pagina_ativa
_page_subtitle = "Performance Intelligence · Perfor Agency"

if nivel == "projeto":
    projeto = get_active_project()
    if projeto:
        _page_subtitle = get_project_display_name(projeto)

st.markdown(
    f"""
    <div style='margin-bottom: 32px;'>
        <h1 style='font-size:2rem; font-weight:700; color:#FAFAFA;
                   letter-spacing:-0.5px; margin-bottom:4px;'>
            {_page_title}
        </h1>
        <p style='color:#4b5563; font-size:0.9rem; margin:0;'>
            {_page_subtitle}
        </p>
        <hr style='border:none; border-top:1px solid #1f2937; margin-top:16px;'>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Roteamento de páginas ─────────────────────────────────────────────────────

if nivel == "agencia":
    # ── Páginas do nível agência ──────────────────────────────────────────
    if pagina_ativa == "Visão Geral":
        from modules.dashboard import render_visao_geral
        render_visao_geral()

    elif pagina_ativa == "Squad Dashboard":
        from modules.squad_dashboard import render_squad_dashboard
        squad_name = st.session_state.get("_squad_view")
        render_squad_dashboard(squad_name=squad_name)

    elif pagina_ativa == "CEO Dashboard":
        if is_ceo():
            render_cargo_badge("👑 CEO Dashboard", "Visão consolidada de toda a agência.")
            from modules.dashboard import render_visao_geral
            # CEO Dashboard reutiliza a visão agregada
            render_visao_geral()
        else:
            st.warning("Acesso restrito ao CEO.")

    else:
        from modules.dashboard import render_visao_geral
        render_visao_geral()

elif nivel == "projeto":
    # ── Páginas do nível projeto ──────────────────────────────────────────
    if pagina_ativa == "GPS Dashboard":
        from modules.dashboard import render_visao_geral
        render_visao_geral()

    elif pagina_ativa == "Brain":
        render_cargo_badge("✦ Brain — Estratégia & Insights", "Análises estratégicas, recomendações de budget e alertas de performance.")
        projeto = get_active_project()
        _nome = get_project_display_name(projeto) if projeto else "—"
        st.markdown(
            f"""<div class="glass-card" style="text-align:center; padding:48px 32px;">
                <div style="font-size:3rem; margin-bottom:16px;">🧠</div>
                <h3 style="color:#FAFAFA; margin:0 0 8px 0;">Módulo em Construção</h3>
                <p style="color:#6b7280; font-size:0.88rem; margin:0;">Projeto ativo: <strong style="color:#00C853;">{_nome}</strong><br>
                Em breve: análises estratégicas e alertas de performance.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    elif pagina_ativa == "Criativos":
        from modules.creative_analysis import render_criativos
        render_criativos()

    elif pagina_ativa == "Financeiro":
        render_cargo_badge("✦ Financeiro", "MRR, churn, LTV e projeções de receita.")
        projeto = get_active_project()
        _nome = get_project_display_name(projeto) if projeto else "—"
        st.markdown(
            f"""<div class="glass-card" style="text-align:center; padding:48px 32px;">
                <div style="font-size:3rem; margin-bottom:16px;">💳</div>
                <h3 style="color:#FAFAFA; margin:0 0 8px 0;">Módulo em Construção</h3>
                <p style="color:#6b7280; font-size:0.88rem; margin:0;">Projeto ativo: <strong style="color:#00C853;">{_nome}</strong><br>
                Em breve: MRR, churn, LTV e projeções de receita.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    else:
        from modules.dashboard import render_visao_geral
        render_visao_geral()
