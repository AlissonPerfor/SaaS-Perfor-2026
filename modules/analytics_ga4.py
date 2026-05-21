"""
Módulo de Analytics GA4 e Copiloto Omnichannel (Integração Gemini)
Painel Executivo Premium - Padrão SaaS
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.context import get_active_project

def format_currency(val):
    if pd.isna(val):
        return "R$ 0,00"
    return f"R$ {val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def format_percentage(val):
    if pd.isna(val):
        return "0.00%"
    return f"{val:,.2f}%"

def map_perfor_channels(source_medium):
    sm = str(source_medium).lower()
    # Google Ads
    if 'google' in sm and ('cpc' in sm or 'gclid' in sm or 'adwords' in sm):
        return "02. Google CPC"
    # Meta Ads
    elif ('facebook' in sm or 'instagram' in sm or 'fb' in sm or 'ig' in sm) and ('cpc' in sm or 'anuncio' in sm or 'paidsocial' in sm):
        return "01. Facebook CPC"
    # Direto
    elif '(direct)' in sm or 'direto' in sm:
        return "07. Direto"
    # Instagram Orgânico / Link na Bio
    elif 'instagram' in sm or 'bio' in sm or 'linktree' in sm:
        return "08. Perfil Instagram"
    # Email Marketing
    elif 'email' in sm or 'newsletter' in sm or 'mailchimp' in sm or 'rdstation' in sm or 'activecampaign' in sm:
        return "04. E-mail"
    # Orgânico (SEO)
    elif 'organic' in sm or 'google / organic' in sm or 'bing' in sm or 'yahoo' in sm:
        return "06. Orgânico"
    # Referências (Backlinks/Parceiros)
    elif 'referral' in sm:
        return "09. Referral"
    # Outros CPCs (Tiktok, Pinterest, etc)
    elif 'cpc' in sm or 'ads' in sm:
        return "03. Outras Mídias Pagas"
    else:
        return "10. Outros / Não Definido"

@st.cache_data(ttl=600, show_spinner=False)
def fetch_ga4_data(property_id: str, report_type: str, start_date: str, end_date: str):
    """
    Busca os dados do GA4 para Canais ou Produtos usando a conta de serviço.
    Faz cache da requisição atrelado as datas selecionadas.
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

    # 1. RASTREADOR INTELIGENTE DE SEGREDOS DO GOOGLE
    google_secrets = None

    # Procura primeiro nas sub-gavetas conhecidas
    for target_key in ["gcp_service_account", "gspread", "google_sheets", "google"]:
        if target_key in st.secrets:
            sub_dict = st.secrets[target_key]
            if hasattr(sub_dict, "get") and sub_dict.get("client_email"):
                google_secrets = dict(sub_dict)
                break

    # Se não achou, faz uma varredura completa procurando onde está o client_email
    if not google_secrets:
        for k in st.secrets.keys():
            try:
                potential_dict = st.secrets[k]
                if hasattr(potential_dict, "get") and potential_dict.get("client_email"):
                    google_secrets = dict(potential_dict)
                    break
            except:
                continue

    # Caso os segredos estejam salvos direto na raiz (formato plano)
    if not google_secrets and "client_email" in st.secrets:
        google_secrets = dict(st.secrets)

    # Se mesmo assim não localizar, exibe o erro amigável na tela
    if not google_secrets:
        st.error("Configuração pendente: Credenciais do Google não foram localizadas em st.secrets.")
        return None

    # 2. CORREÇÃO DA CHAVE PEM E INICIALIZAÇÃO
    if google_secrets and "private_key" in google_secrets:
        raw_key = str(google_secrets["private_key"]).strip()
        
        # Higienização e Reconstrução Absoluta do PEM
        if raw_key.startswith('"') and raw_key.endswith('"'):
            raw_key = raw_key[1:-1]
        if raw_key.startswith("'") and raw_key.endswith("'"):
            raw_key = raw_key[1:-1]
            
        raw_key = raw_key.replace("-----BEGIN PRIVATE KEY-----", "")
        raw_key = raw_key.replace("-----END PRIVATE KEY-----", "")
        raw_key = raw_key.replace("\\n", "")
        raw_key = raw_key.replace("\n", "")
        raw_key = raw_key.replace(" ", "")
        
        import textwrap
        wrapped_key = "\n".join(textwrap.wrap(raw_key, 64))
        google_secrets["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{wrapped_key}\n-----END PRIVATE KEY-----\n"

    try:
        client = BetaAnalyticsDataClient.from_service_account_info(google_secrets)
    except Exception as e:
        st.error(f"Erro crítico ao instanciar cliente GA4: {str(e)}")
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
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        
        try:
            response = client.run_report(request)
        except Exception as e:
            st.error(f"Erro ao buscar dados de Canais na API do GA4: {str(e)}")
            return pd.DataFrame()
            
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
        grouped['Taxa de Eventos Principais por Sessão: Purchase'] = ((grouped['purchases'] / grouped['sessions']) * 100).fillna(0.0).map("{:.2f}%".format)
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
        
        # Return dataframes together with raw metrics for global KPIs
        raw_kpis = {
            'total_revenue': df['total_revenue'].sum(),
            'total_sessions': df['sessions'].sum(),
            'total_purchases': df['purchases'].sum()
        }
        
        return final_df, raw_kpis
        
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
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        
        try:
            response = client.run_report(request)
        except Exception as e:
            st.error(f"Erro ao buscar dados de Produtos na API do GA4: {str(e)}")
            return pd.DataFrame()
            
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

def render_kpi_cards(kpi_data):
    """Renderiza os 4 cards executivos via HTML/CSS."""
    rev = kpi_data.get('total_revenue', 0)
    sess = kpi_data.get('total_sessions', 0)
    purch = kpi_data.get('total_purchases', 0)
    
    conv_rate = (purch / sess * 100) if sess > 0 else 0
    avg_ticket = (rev / purch) if purch > 0 else 0
    
    css = """
    <style>
    .ga4-card {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 213, 146, 0.15);
        border-radius: 12px;
        padding: 20px;
        text-align: left;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 24px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .ga4-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 213, 146, 0.05);
    }
    .ga4-card-title {
        color: #8a99ad;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .ga4-card-value {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''
            <div class="ga4-card">
                <div class="ga4-card-title">Faturamento Total</div>
                <div class="ga4-card-value">{format_currency(rev)}</div>
            </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
            <div class="ga4-card">
                <div class="ga4-card-title">Volume de Tráfego</div>
                <div class="ga4-card-value">{int(sess):,}</div>
            </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''
            <div class="ga4-card">
                <div class="ga4-card-title">Conversão Blended</div>
                <div class="ga4-card-value">{format_percentage(conv_rate)}</div>
            </div>
        ''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''
            <div class="ga4-card">
                <div class="ga4-card-title">Ticket Médio Geral</div>
                <div class="ga4-card-value">{format_currency(avg_ticket)}</div>
            </div>
        ''', unsafe_allow_html=True)


def render_ga4() -> None:
    # Cabeçalho da página
    st.markdown('''
    <div style="margin-bottom: 8px;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin: 0 0 6px 0;">Google Analytics 4</h1>
        <p style="color: #8a99ad; font-size: 0.95rem; margin: 0;">Faturamento, canais de aquisição e funil de vendas</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Filtro de Data Dinâmico
    st.markdown('''
    <style>
    div[data-testid="stDateInput"] {
        max-width: 320px;
        margin-bottom: 12px;
    }
    
    /* Remove native Streamlit date presets in popup */
    div[data-baseweb="calendar"] div[data-baseweb="select"] {
        display: none !important;
    }
    div[data-baseweb="calendar"] div:has(> span:contains("Choose a date range")) {
        display: none !important;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    today = datetime.today()
    
    st.markdown('<p style="font-size: 0.9rem; color: #8a99ad; margin-bottom: 8px;">Filtrar Período de Análise:</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        preset_option = st.selectbox(
            "Preset",
            options=["Últimos 7 Dias", "Últimos 14 Dias", "Últimos 30 Dias", "Mês Atual", "Últimos 3 Meses", "Últimos 6 Meses", "Ano Atual", "Personalizado"],
            index=2, # Padrão: Últimos 30 Dias
            label_visibility="collapsed"
        )
        
    if preset_option == "Últimos 7 Dias":
        default_dates = (today - timedelta(days=7), today)
    elif preset_option == "Últimos 14 Dias":
        default_dates = (today - timedelta(days=14), today)
    elif preset_option == "Últimos 30 Dias":
        default_dates = (today - timedelta(days=30), today)
    elif preset_option == "Mês Atual":
        default_dates = (today.replace(day=1), today)
    elif preset_option == "Últimos 3 Meses":
        default_dates = (today - timedelta(days=90), today)
    elif preset_option == "Últimos 6 Meses":
        default_dates = (today - timedelta(days=180), today)
    elif preset_option == "Ano Atual":
        default_dates = (today.replace(month=1, day=1), today)
    else:
        default_dates = (today - timedelta(days=30), today)

    with col2:
        if preset_option == "Personalizado":
            c_start, c_end = st.columns(2)
            with c_start:
                start_d = st.date_input(
                    "Inicial",
                    value=default_dates[0],
                    max_value=today,
                    format="DD/MM/YYYY",
                    label_visibility="collapsed"
                )
            with c_end:
                end_d = st.date_input(
                    "Final",
                    value=default_dates[1],
                    max_value=today,
                    format="DD/MM/YYYY",
                    label_visibility="collapsed"
                )
            date_range = (start_d, end_d)
        else:
            date_range = default_dates
            # Visual de input bloqueado via HTML para evitar o popup em inglês do Streamlit
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); 
                        padding: 0 12px; border-radius: 8px; color: #8a99ad; font-size: 0.95rem; height: 38px; display: flex; align-items: center; cursor: not-allowed;">
                {date_range[0].strftime('%d/%m/%Y')} – {date_range[1].strftime('%d/%m/%Y')}
            </div>
            """, unsafe_allow_html=True)
    
    # Verifica se o usuário já selecionou ambas as datas
    if len(date_range) != 2:
        st.warning("Selecione a data inicial e final do período.")
        return
        
    start_date = date_range[0].strftime("%Y-%m-%d")
    end_date = date_range[1].strftime("%Y-%m-%d")
    
    projeto = get_active_project()
    if not projeto:
        st.warning("Nenhum projeto selecionado.")
        return
        
    ga4_id = projeto.get('ga4_id')
    if not ga4_id:
        st.markdown('''
        <div style="background-color: rgba(255,255,255,0.03); border-left: 4px solid #8a99ad; padding: 20px; border-radius: 8px; margin-top: 24px;">
            <p style="color: #FAFAFA; margin: 0; font-size: 1.05rem;">Integração GA4 Pendente</p>
            <p style="color: #8a99ad; margin: 8px 0 0 0; font-size: 0.9rem;">
                O Google Analytics 4 ainda não foi configurado para este cliente. Adicione o ID da Propriedade (ga4_id) no painel de configurações.
            </p>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Buscar dados da API
    with st.spinner("Sincronizando dados com Google Analytics..."):
        res_canais = fetch_ga4_data(ga4_id, "canais", start_date, end_date)
        df_produtos = fetch_ga4_data(ga4_id, "produtos", start_date, end_date)
    
    if res_canais is None:
        return
        
    df_canais, raw_kpis = res_canais
    
    # Renderizar KPIs Executivos
    render_kpi_cards(raw_kpis)

    # Renderizar UI com as abas
    tab1, tab2 = st.tabs(["Desempenho de Canais", "Performance de Produtos"])
    
    # CSS Customizado Premium para Tabs e DataFrames
    st.markdown('''
    <style>
    /* Styling Tabs */
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
    /* Styling Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
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
