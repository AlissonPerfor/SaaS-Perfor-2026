"""
modules/overview.py
Módulo 'Visão Geral' - Hub de Boas-Vindas Estratégico.
"""

import random
from datetime import datetime
import streamlit as st

from core.context import (
    get_all_projects,
    navigate_to_project,
)

MESSAGES_POOL = {
    "primeira_quinzena": {
        "manha": [
            "Café na mão, pixel aquecido e olho no CPA. Bora tracionar essas contas logo cedo!",
            "O orçamento do mês está fresquinho. Quais ganchos novos vamos testar hoje?",
            "Mente fria, dados limpos. Que tal auditar as regras automatizadas antes do mercado acordar?"
        ],
        "tarde": [
            "Primeira metade do dia concluída. Como está o comportamento do CTR nas campanhas de escala?",
            "Foco total! O tráfego do horário de almoço já processou. Hora de calibrar os lances.",
            "Tarde produtiva! Lembre-se: menos achismo, mais dados. O que o GA4 te diz hoje?"
        ],
        "noite": [
            "Operação encerrada por hoje? Só não esqueça de checar se nenhum orçamento diário ficou aberto por erro.",
            "Baita dia! Os criativos novos performaram? Dê aquela última olhada nos gráficos antes do report."
        ],
        "madrugada": [
            "Madrugada silenciosa, contas blindadas. Hora ideal para minerar novas referências na biblioteca de anúncios.",
            "Enquanto a concorrência dorme, a Perfor otimiza. O ROAS alto do dia seguinte nasce aqui."
        ]
    },
    "segunda_quinzena": {
        "manha": [
            "Segunda quinzena na tela! O planejamento de {proximo_mes} não vai se desenhar sozinho. Bora!",
            "Dia de analisar quais criativos saturaram nesta quinzena para pedir reposição ao design.",
            "Alinhamento estratégico ligado. As reuniões de renovação de budget para {proximo_mes} começam essa semana."
        ],
        "tarde": [
            "Hora do raio-X: Quais ganchos UGC performaram melhor para usarmos de base no briefing de {proximo_mes}?",
            "Não deixe o cliente te cobrar: antecipe as ideias promocionais do próximo mês hoje.",
            "Ajuste fino ativado: Hora de cortar o público que só gastou verba e focar no remarketing decisivo."
        ],
        "noite": [
            "Os briefings para as campanhas de {proximo_mes} já estão no forno? Garanta o fluxo do time criativo.",
            "Dia finalizado. Amanhã é dia de olhar o teto de CPA acumulado com os Heads."
        ],
        "madrugada": [
            "Arquitetando o futuro de {proximo_mes}. Grandes ganchos de tráfego surgem na calada da noite.",
            "Madrugada silenciosa, contas blindadas. Hora ideal para minerar novas referências na biblioteca de anúncios.",
            "Enquanto a concorrência dorme, a Perfor otimiza. O ROAS alto do dia seguinte nasce aqui."
        ]
    }
}

def get_hub_greeting() -> None:
    agora = datetime.now()
    hora = agora.hour
    
    if 5 <= hora < 12:
        saudacao = "Bom dia"
        periodo = "manha"
    elif 12 <= hora < 18:
        saudacao = "Boa tarde"
        periodo = "tarde"
    elif 18 <= hora <= 23:
        saudacao = "Boa noite"
        periodo = "noite"
    else:
        saudacao = "Boa madrugada"
        periodo = "madrugada"
        
    user_data = st.session_state.get("user_data") or {}
    nome_completo = user_data.get("nome", "Álisson")
    nome_usuario = nome_completo.split()[0] if nome_completo else "Álisson"
    
    dia_atual = agora.day
    mes_atual = agora.month
    quinzena = "primeira_quinzena" if dia_atual <= 15 else "segunda_quinzena"
    
    meses_extenso = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    prox_mes_idx = mes_atual % 12
    prox_mes_nome = meses_extenso[prox_mes_idx]
    
    # Seleção da mensagem dinâmica
    frase_escolhida = random.choice(MESSAGES_POOL[quinzena][periodo])
    msg_estrategica = frase_escolhida.format(proximo_mes=prox_mes_nome)
    
    icone = ""

    st.markdown(f'''
    <div style="margin-bottom: 24px; padding: 24px 28px; border-radius: 12px; background: linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(139,92,246,0.06) 100%); border: 1px solid rgba(255,255,255,0.05);">
        <h1 style="font-size: 2.2rem; font-weight: 700; color: #FAFAFA; margin: 0 0 6px 0; letter-spacing: -0.5px;">{saudacao}, {nome_usuario}! 🚀</h1>
        <p style="color: #D1D5DB; font-size: 1.05rem; margin: 0; letter-spacing: 0.3px;">
            {msg_estrategica}
        </p>
    </div>
    ''', unsafe_allow_html=True)

def render_workspace_analista() -> None:
    """Renderiza o workspace do analista/head com tarefas, agenda e atalhos rápidos."""
    
    css_card = '''
    <style>
    .workspace-card {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 213, 146, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        height: 100%;
        min-height: 140px;
        backdrop-filter: blur(10px);
    }
    </style>
    '''
    st.markdown(css_card, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown('''
        <div class="workspace-card">
            <h3 style="font-size: 1.1rem; color: #FAFAFA; margin: 0 0 12px 0;"> 📋 Quadro de Tarefas</h3>
            <p style="color: #9CA3AF; font-size: 0.85rem; margin: 0; line-height: 1.5;">
                <em>Em breve: Integração com seu fluxo de demandas diárias.</em>
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown('''
        <div class="workspace-card">
            <h3 style="font-size: 1.1rem; color: #FAFAFA; margin: 0 0 12px 0;"> 📅 Próximas Reuniões</h3>
            <p style="color: #9CA3AF; font-size: 0.85rem; margin: 0; line-height: 1.5;">
                <em>Em breve: Sincronização com seu calendário Perfor.</em>
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        st.markdown('''
        <div class="workspace-card" style="padding-bottom: 10px;">
            <h3 style="font-size: 1.1rem; color: #FAFAFA; margin: 0 0 12px 0;"><i class="bi bi-lightning-charge"></i> Acesso Rápido</h3>
            <div style="margin-top: -8px;"></div>
        ''', unsafe_allow_html=True)
        
        projetos = get_all_projects()
        recentes = projetos[:3]
        
        if recentes:
            for p in recentes:
                nome = p.get("nome_cliente") or p.get("nome", "Projeto")
                if st.button(f"🚀 {nome}", key=f"btn_ws_{p.get('id', nome)}", use_container_width=True):
                    navigate_to_project(p)
        else:
            st.markdown("<p style='color: #6b7280; font-size: 0.8rem;'>Nenhum projeto vinculado.</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

def render_visao_geral() -> None:
    """
    Renderiza o Hub de Boas-Vindas (Visão Geral) da Agência.
    Apenas exibe a saudação estratégica e o workspace do analista.
    """
    get_hub_greeting()
    render_workspace_analista()
