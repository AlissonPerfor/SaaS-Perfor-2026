"""
Módulo de Analytics GA4 e Copiloto Omnichannel (Integração Gemini)
"""

import streamlit as st
import pandas as pd
from core.context import get_active_project

def format_currency(val):
    if pd.isna(val):
        return "R$ 0,00"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(val):
    if pd.isna(val):
        return "0.00%"
    return f"{val:,.2f}%"

def map_perfor_channels(source_medium):
    sm = str(source_medium).lower()
    if 'facebook / cpc' in sm or 'instagram / cpc' in sm or 'anuncio' in sm:
        return "01. Facebook CPC"
    elif 'google / cpc' in sm:
        return "02. Google CPC"
    elif '(direct)' in sm:
        return "07. Direto"
    elif 'instagram' in sm or 'bio' in sm:
        return "08. Perfil Instagram"
    elif 'email' in sm or 'newsletter' in sm:
        return "04. E-mail"
    elif 'organic' in sm:
        return "06. Orgânico"
    else:
        return "Outros / Não Definido"

@st.cache_data(ttl=600, show_spinner=False)
def fetch_ga4_data(property_id: str, report_type: str):
    """
    Busca os dados do GA4 para Canais ou Produtos usando a conta de serviço.
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        from google.oauth2 import service_account
    except ImportError:
        st.error("Biblioteca `google-analytics-data` não instalada.")
        return None

    import json
    creds_dict = {}
    try:
        with open(".streamlit/google_credentials.json", "r", encoding="utf-8") as f:
            creds_dict = json.load(f)
    except FileNotFoundError:
        try:
            creds_dict = st.secrets["google"]
        except KeyError:
            st.error("Credenciais do Google não encontradas (st.secrets['google'] ou google_credentials.json).")
            return None

    try:
        # Garante que as credenciais são um dicionário mutável
        secrets_dict = dict(creds_dict)
        
        # Correção cirúrgica para leitura do arquivo PEM do Google (newlines escapadas no secrets)
        if "private_key" in secrets_dict and isinstance(secrets_dict["private_key"], str):
            secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")

        credentials = service_account.Credentials.from_service_account_info(secrets_dict)
        client = BetaAnalyticsDataClient(credentials=credentials)
    except Exception as e:
        st.error(f"Erro ao autenticar no GCP: {str(e)}")
        return None

    property_uri = f"properties/{property_id}"
    
    if report_type == "canais":
        request = RunReportRequest(
            property=property_uri,
            dimensions=[Dimension(name="sessionSourceMedium")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="engagementRate"),
                Metric(name="ecommercePurchases"),
                Metric(name="totalRevenue")
            ],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        )
        
        response = client.run_report(request)
        data = []
        for row in response.rows:
            data.append({
                "source_medium": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "engagement_rate": float(row.metric_values[1].value),
                "purchases": int(row.metric_values[2].value),
                "total_revenue": float(row.metric_values[3].value)
            })
            
        df = pd.DataFrame(data)
        if df.empty:
            return df
            
        df['Canal'] = df['source_medium'].apply(map_perfor_channels)
        
        grouped = df.groupby('Canal').agg({
            'sessions': 'sum',
            'purchases': 'sum',
            'total_revenue': 'sum',
            'engagement_rate': 'mean' # Média simples para exibição limpa
        }).reset_index()
        
        # Cálculos Inteligentes locais (Pandas)
        grouped['Taxa de Engajamento'] = (grouped['engagement_rate'] * 100).map("{:.2f}%".format)
        grouped['Taxa de Eventos Principais por Sessão: Purchase'] = ((grouped['purchases'] / grouped['sessions']) * 100).map("{:.2f}%".format)
        grouped['Receita Média de Compra'] = (grouped['total_revenue'] / grouped['purchases']).fillna(0.0)
        
        # Ordenação estratégica
        grouped = grouped.sort_values(by='total_revenue', ascending=False)
        
        # Formatação monetária final para a UI Premium
        grouped['Receita Total'] = grouped['total_revenue'].map("R$ {:,.2f}".format).str.replace(",", "v").str.replace(".", ",").str.replace("v", ".")
        grouped['Receita Média de Compra'] = grouped['Receita Média de Compra'].map("R$ {:,.2f}".format).str.replace(",", "v").str.replace(".", ",").str.replace("v", ".")
        
        final_df = grouped[[
            'Canal', 'sessions', 'Taxa de Engajamento', 'purchases', 
            'Taxa de Eventos Principais por Sessão: Purchase', 'Receita Total', 'Receita Média de Compra'
        ]].rename(columns={
            'sessions': 'Sessões',
            'purchases': 'Eventos Principais: Purchase'
        })
        
        return final_df
    elif report_type == "produtos":
        request = RunReportRequest(
            property=property_uri,
            dimensions=[Dimension(name="itemName")],
            metrics=[
                Metric(name="itemsViewed"),
                Metric(name="itemsAddedToCart"),
                Metric(name="itemsPurchased"),
                Metric(name="itemRevenue")
            ],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        )
        
        response = client.run_report(request)
        data = []
        for row in response.rows:
            dim_values = [dim.value for dim in row.dimension_values]
            metric_values = [float(metric.value) for metric in row.metric_values]
            data.append(dim_values + metric_values)
            
        if not data:
            return pd.DataFrame()
            
        cols = ["Produto", "Itens vistos", "Itens adicionados ao carrinho", "Itens comprados", "Receita do item"]
        df = pd.DataFrame(data, columns=cols)
        # Calculando Taxa de Conversão do Produto
        df["Taxa de Conversão do Produto"] = (df["Itens comprados"] / df["Itens vistos"]) * 100
        df["Taxa de Conversão do Produto"] = df["Taxa de Conversão do Produto"].fillna(0)
        df = df.sort_values(by="Receita do item", ascending=False)
        return df
    else:
        return None

def analyze_with_gemini(df_canais, df_produtos):
    """Envia os dados sumarizados para o Gemini e retorna a análise."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "❌ Biblioteca `google-genai` não instalada. Rode: `pip install google-genai`"

    try:
        api_key = st.secrets["gemini"]["api_key"]
    except Exception:
        return "❌ Chave da API do Gemini (gemini.api_key) não encontrada em st.secrets."

    client = genai.Client(api_key=api_key)
    
    csv_canais = df_canais.head(10).to_csv(index=False) if df_canais is not None and not df_canais.empty else "Sem dados de canais."
    csv_produtos = df_produtos.head(10).to_csv(index=False) if df_produtos is not None and not df_produtos.empty else "Sem dados de produtos."
    
    prompt = f"""
    Você é a inteligência artificial estratégica (Copiloto) da Perfor Agency, uma agência focada em performance e Growth.
    
    Baseado nos dados do Google Analytics 4 (últimos 30 dias):
    
    DADOS DE CANAIS (Top 10):
    {csv_canais}
    
    DADOS DE PRODUTOS (Top 10):
    {csv_produtos}
    
    Sua missão é fornecer um relatório direto, profissional e focado em Growth. 
    NÃO utilize tabelas no seu retorno. Use formatação Markdown limpa e elegante.
    
    Estruture obrigatoriamente a sua resposta nos seguintes tópicos:
    
    1. Diagnóstico do Funil de Produtos
    2. Eficiência de Canais de Aquisição
    3. Plano de Ação Comercial Recomendado
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        return response.text
    except Exception as e:
        return f"Erro na chamada ao Gemini: {str(e)}"

def render_ga4() -> None:
    st.markdown('''
    <div style="margin-bottom: 24px;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin: 0 0 6px 0;">Google Analytics 4</h1>
        <p style="color: #8a99ad; font-size: 0.95rem; margin: 0;">Faturamento, canais de aquisição e funil de vendas</p>
    </div>
    ''', unsafe_allow_html=True)
    
    projeto = get_active_project()
    if not projeto:
        st.warning("Nenhum projeto selecionado.")
        return
        
    ga4_id = projeto.get('ga4_id')
    if not ga4_id:
        st.markdown('''
        <div style="background-color: rgba(255,255,255,0.03); border-left: 4px solid #8a99ad; padding: 20px; border-radius: 8px;">
            <p style="color: #FAFAFA; margin: 0; font-size: 1.05rem;">Integração GA4 Pendente</p>
            <p style="color: #8a99ad; margin: 8px 0 0 0; font-size: 0.9rem;">
                O Google Analytics 4 ainda não foi configurado para este cliente. Adicione o ID da Propriedade (ga4_id) no painel de configurações.
            </p>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Buscar dados da API
    with st.spinner("Sincronizando dados com Google Analytics..."):
        df_canais = fetch_ga4_data(ga4_id, "canais")
        df_produtos = fetch_ga4_data(ga4_id, "produtos")

    # Renderizar UI com as abas
    tab1, tab2 = st.tabs(["Desempenho de Canais", "Performance de Produtos"])
    
    # CSS Customizado para Tabs (Monocromático, Verde #00D592 no ativo)
    st.markdown('''
    <style>
    [data-testid="stTabs"] button[role="tab"] {
        font-family: 'Urbanist', 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        color: #8a99ad !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #00D592 !important;
    }
    [data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: #00D592 !important;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    with tab1:
        if df_canais is not None and not df_canais.empty:
            st.dataframe(
                df_canais,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhum dado de canais encontrado para este período.")
            
    with tab2:
        if df_produtos is not None and not df_produtos.empty:
            df_prod_display = df_produtos.copy()
            # Formatação
            df_prod_display["Receita do item"] = df_prod_display["Receita do item"].apply(format_currency)
            df_prod_display["Taxa de Conversão do Produto"] = df_prod_display["Taxa de Conversão do Produto"].apply(format_percentage)
            df_prod_display["Itens vistos"] = df_prod_display["Itens vistos"].astype(int)
            df_prod_display["Itens adicionados ao carrinho"] = df_prod_display["Itens adicionados ao carrinho"].astype(int)
            df_prod_display["Itens comprados"] = df_prod_display["Itens comprados"].astype(int)
            
            # Reordenar colunas
            cols = ["Produto", "Itens vistos", "Itens adicionados ao carrinho", "Itens comprados", "Taxa de Conversão do Produto", "Receita do item"]
            st.dataframe(
                df_prod_display[cols],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhum dado de produtos encontrado para este período.")

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    # Copiloto Omnichannel (Integração Gemini)
    st.markdown('''
    <style>
    .copilot-expander [data-testid="stExpander"] {
        border: 1px solid rgba(0, 213, 146, 0.3) !important;
        border-radius: 12px !important;
        background-color: rgba(0, 213, 146, 0.02) !important;
    }
    .copilot-expander summary p {
        color: #00D592 !important;
        font-weight: 600 !important;
    }
    .copilot-expander svg {
        color: #00D592 !important;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="copilot-expander">', unsafe_allow_html=True)
    with st.expander("Análise Estratégica da IA (Copiloto Perfor)", expanded=False):
        st.markdown("<p style='color:#8a99ad; font-size:0.9rem;'>Gere um diagnóstico avançado combinando os dados de tráfego e conversão de vendas.</p>", unsafe_allow_html=True)
        
        if st.button("Interpretar Dados do Funil via Gemini", key="btn_gemini_ga4", type="primary"):
            if not df_canais.empty or not df_produtos.empty:
                with st.spinner("A IA está analisando os padrões de tráfego e vendas..."):
                    analise = analyze_with_gemini(df_canais, df_produtos)
                st.markdown(analise)
            else:
                st.warning("Não há dados suficientes para a IA analisar.")
    st.markdown('</div>', unsafe_allow_html=True)
