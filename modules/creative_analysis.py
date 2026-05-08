"""
modules/creative_analysis.py
Módulo 'Criativos' do dashboard Perfor.IA.
Exibe os anúncios ativos no Meta Ads (placeholder via mock/sheets).

Multi-tenancy: Usa get_active_project() do core.context para obter
o meta_account_id do projeto selecionado na sidebar.
"""

import streamlit as st

from core.context import get_active_project, get_all_projects, render_cargo_badge


def render_criativos() -> None:
    render_cargo_badge(
        "✦ Criativos Meta Ads",
        "Acompanhamento de anúncios ativos e performance.",
    )

    # ── Verifica projeto ativo ────────────────────────────────────────────────
    projeto = get_active_project()

    if projeto is None:
        # CEO com "Todos os Projetos" selecionado — pede para escolher um
        st.markdown(
            """<div class="glass-card" style="text-align:center; padding:40px 32px;">
                <div style="font-size:2.5rem; margin-bottom:14px;">🎯</div>
                <h3 style="color:#FAFAFA; margin:0 0 8px 0; font-size:1rem;">Selecione um Projeto</h3>
                <p style="color:#6b7280; font-size:0.88rem; margin:0;">Para visualizar os criativos, selecione um projeto específico no seletor da sidebar.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    projetos = get_all_projects()
    if not projetos:
        st.warning("Nenhum projeto encontrado.")
        return

    meta_account_id = projeto.get("meta_account_id")

    if not meta_account_id:
        html_erro = f"""
        <div class="glass-card" style="border-color:rgba(251,191,36,0.4); background:linear-gradient(135deg, rgba(251,191,36,0.06) 0%, rgba(12,12,12,0.70) 100%); padding:32px 28px; text-align:center;">
        <div style="font-size:2.5rem; margin-bottom:14px;">⚙️</div>
        <h3 style="color:#FCD34D; margin:0 0 8px 0; font-size:1rem;">Conta Meta Não Configurada</h3>
        <p style="color:#9CA3AF; font-size:0.85rem; max-width:480px; margin:0 auto 16px auto; line-height:1.7;">Não foi possível carregar os anúncios para <strong style="color:#FAFAFA;">{projeto.get('nome_cliente') or projeto.get('nome', 'Projeto')}</strong>.</p>
        <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(251,191,36,0.2); border-radius:8px; padding:10px 16px; display:inline-block; max-width:600px;">
        <p style="color:#6b7280; font-size:0.75rem; margin:0; font-family:monospace; letter-spacing:0.3px;">meta_account_id não definido no Supabase.</p>
        </div>
        <p style="color:#4b5563; font-size:0.75rem; margin:16px 0 0 0;">Verifique o campo <code style="color:#FCD34D;">meta_account_id</code> na tabela de projetos para visualizar os criativos.</p>
        </div>
        """
        st.markdown(html_erro, unsafe_allow_html=True)
        return

    st.markdown(f"<p style='color:#6b7280; font-size:0.85rem; margin-bottom:20px; text-align:right;'>Meta Account ID: <strong>{meta_account_id}</strong></p>", unsafe_allow_html=True)

    # Tabs para estruturar a página
    tab1, tab2 = st.tabs(["🔥 Anúncios Ativos (Placeholder)", "📈 Análise de Formatos"])

    with tab1:
        st.markdown(
            "<p style='color:#9CA3AF; font-size:0.85rem; margin-top: 8px;'><em>Os dados abaixo simulam uma listagem de anúncios submetidos via Google Sheets. Futuramente, esta visão será atualizada em tempo real pela API do Meta Ads.</em></p>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Mock de dados simulando Google Sheets listando criativos e status
        mock_ads = [
            {
                "nome": "Vídeo VSL 01 - Oferta Principal",
                "tipo": "Vídeo",
                "preview": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                "data_ativacao": "25/04/2026",
                "status": "Ativo"
            },
            {
                "nome": "Imagem Carrossel - Benefícios",
                "tipo": "Imagem",
                "preview": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                "data_ativacao": "28/04/2026",
                "status": "Pendente"
            },
            {
                "nome": "UGC - Depoimento Cliente Real",
                "tipo": "Vídeo",
                "preview": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                "data_ativacao": "30/04/2026",
                "status": "Ativo"
            },
            {
                "nome": "Story - Chamada Imediata",
                "tipo": "Imagem",
                "preview": "https://images.unsplash.com/photo-1563986768609-322da13575f3?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                "data_ativacao": "01/05/2026",
                "status": "Pendente"
            }
        ]

        cols = st.columns(3, gap="medium")
        for i, ad in enumerate(mock_ads):
            with cols[i % 3]:
                if ad["status"] == "Ativo":
                    status_color = "#00C853"
                    status_bg = "rgba(0,200,83,0.15)"
                else:
                    status_color = "#FCD34D"
                    status_bg = "rgba(251,191,36,0.15)"
                
                st.markdown(f"""
                <div class="glass-card" style="padding: 16px; margin-bottom: 24px; display:flex; flex-direction:column; justify-content:space-between; height: 100%;">
                    <div>
                        <div style="width: 100%; height: 180px; border-radius: 8px; margin-bottom: 16px; overflow: hidden; background-color: #1f2937;">
                            <img src="{ad['preview']}" style="width: 100%; height: 100%; object-fit: cover; opacity: 0.85; transition: opacity 0.3s ease;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.85'" />
                        </div>
                        <h4 style="margin: 0 0 12px 0; font-size: 1rem; color: #FAFAFA; line-height: 1.3;">{ad['nome']}</h4>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span style="font-size: 1rem;">{'🎥' if ad['tipo'] == 'Vídeo' else '🖼️'}</span>
                                <span style="font-size: 0.8rem; color: #9CA3AF;">{ad['tipo']}</span>
                            </div>
                            <span style="font-size: 0.8rem; color: #9CA3AF;">📅 {ad['data_ativacao']}</span>
                        </div>
                    </div>
                    <div style="display: inline-block; align-self: flex-start; padding: 4px 12px; border-radius: 20px; background: {status_bg}; border: 1px solid {status_color};">
                        <span style="color: {status_color}; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px;">{ad['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with tab2:
        st.markdown(
            """<div class="glass-card" style="text-align:center; padding:48px 32px; margin-top: 16px;">
                <div style="font-size:3rem; margin-bottom:16px;">🚧</div>
                <h3 style="color:#FAFAFA; margin:0 0 8px 0;">Módulo em Construção</h3>
                <p style="color:#6b7280; font-size:0.88rem; margin:0;">Em breve: Comparativo de CTR, Hook Rate e performance por formato criativo com dados reais da API do Meta Ads.</p>
            </div>""",
            unsafe_allow_html=True
        )
