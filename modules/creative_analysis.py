"""
modules/creative_analysis.py
Módulo 'Criativos' do dashboard Perfor.IA.
Exibe os anúncios ativos no Meta Ads com dados reais via API.

Multi-tenancy: Usa get_active_project() do core.context para obter
o meta_account_id do projeto selecionado na sidebar.
"""

import calendar
import json
from datetime import date
from typing import Optional

import streamlit as st

from core.context import (
    get_active_project,
    get_all_projects,
    get_project_display_name,
    render_cargo_badge,
    get_agent_prompt,
)
from core.sheets import MESES_ABREV


# ── Constantes ────────────────────────────────────────────────────────────────

_GUIDE_FILE = "MATRIZ_CRIATIVA_IA_guia-inteligencia.md"


# ── Helpers — Período do mês ─────────────────────────────────────────────────

def _get_month_range(mes_abrev: str) -> tuple[str, str]:
    """
    Retorna (since, until) no formato 'YYYY-MM-DD' para o mês selecionado.
    Usa o ano atual; se o mês selecionado for posterior ao mês corrente,
    assume que se refere ao ano anterior.
    """
    try:
        mes_num = MESES_ABREV.index(mes_abrev) + 1
    except ValueError:
        mes_num = date.today().month

    ano = date.today().year
    if mes_num > date.today().month:
        ano -= 1

    last_day = calendar.monthrange(ano, mes_num)[1]
    since = f"{ano}-{mes_num:02d}-01"
    until = f"{ano}-{mes_num:02d}-{last_day:02d}"
    return since, until


# ── Integração com a API do Meta Ads ─────────────────────────────────────────

def _init_meta_api() -> bool:
    """
    Inicializa o SDK do facebook_business com as credenciais do secrets.toml.
    Retorna True se a inicialização foi bem-sucedida, False caso contrário.
    """
    try:
        from facebook_business.api import FacebookAdsApi

        meta_secrets = st.secrets.get("meta_ads")
        if not meta_secrets:
            return False

        access_token = meta_secrets.get("access_token", "")
        app_id = meta_secrets.get("app_id", "")

        if not access_token:
            return False

        FacebookAdsApi.init(app_id, "", access_token)
        return True
    except Exception as e:
        print(f"[Meta API] Erro ao inicializar SDK: {e}")
        return False


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_meta_ads(account_id: str, since: str, until: str) -> dict:
    """
    Busca os TOP 20 anúncios por gasto no Meta Ads dentro do período.

    Estratégia:
      1) get_insights(level='ad') → top 20 por spend (1 call)
      2) Ad.api_get com creative{image_url,thumbnail_url,video_id} (1 call/ad)
    """
    result = {"ads": [], "erro": None}

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.ad import Ad

        if not account_id.startswith("act_"):
            account_id = f"act_{account_id}"

        account = AdAccount(account_id)

        # ── 1) Top 20 por gasto — única requisição de insights ───────────
        insights = account.get_insights(
            fields=["ad_id", "ad_name", "spend"],
            params={
                "level": "ad",
                "time_range": {"since": since, "until": until},
                "sort": ["spend_descending"],
                "limit": 20,
                "filtering": [
                    {"field": "spend", "operator": "GREATER_THAN", "value": "0"}
                ],
            },
        )

        # ── 2) Para cada insight, busca ad com creative expandido ────────
        for row in insights:
            ad_id = row.get("ad_id")
            ad_name = row.get("ad_name", "Sem nome")
            spend = float(row.get("spend", 0))

            if spend <= 0:
                continue

            preview_url = None
            creative_type = "Imagem"
            ad_status = "ACTIVE"

            try:
                ad_obj = Ad(ad_id).api_get(
                    fields=[
                        "name",
                        "status",
                        "creative{image_url,thumbnail_url,video_id}",
                    ]
                )
                ad_status = ad_obj.get("status", "ACTIVE")

                creative = ad_obj.get("creative") or {}

                image_url = creative.get("image_url")
                thumbnail_url = creative.get("thumbnail_url")
                video_id = creative.get("video_id")

                if video_id or thumbnail_url:
                    creative_type = "Vídeo"
                    preview_url = thumbnail_url or image_url
                else:
                    creative_type = "Imagem"
                    preview_url = image_url
            except Exception:
                pass

            result["ads"].append({
                "nome": ad_name,
                "status": ad_status,
                "spend": spend,
                "preview_url": preview_url,
                "creative_type": creative_type,
            })

    except Exception as e:
        result["erro"] = str(e)

    return result


# ── Formatação ────────────────────────────────────────────────────────────────

def _fmt_spend(value: float) -> str:
    """Formata o valor de gasto em BRL."""
    if value >= 1_000:
        return f"R$ {value / 1_000:.1f}k".replace(".", ",")
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _status_label(raw_status: str) -> tuple[str, str, str]:
    """
    Retorna (label, cor, bg) para o status do anúncio.
    """
    mapping = {
        "ACTIVE": ("Ativo", "#00d592", "rgba(0,213,146,0.15)"),
        "PAUSED": ("Pausado", "#FCD34D", "rgba(251,191,36,0.15)"),
        "CAMPAIGN_PAUSED": ("Campanha Pausada", "#F59E0B", "rgba(245,158,11,0.12)"),
        "ADSET_PAUSED": ("Conjunto Pausado", "#F59E0B", "rgba(245,158,11,0.12)"),
    }
    return mapping.get(raw_status, ("Inativo", "#6b7280", "rgba(107,114,128,0.15)"))


# ── Renderização dos Cards de Criativos ──────────────────────────────────────

_FALLBACK_IMG = "https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=400&q=60"


def _render_ad_cards(ads: list[dict]) -> None:
    """Renderiza os cards dos anúncios em um grid de 3 colunas usando st.image."""
    cols = st.columns(3, gap="medium")

    for i, ad in enumerate(ads):
        label, status_color, status_bg = _status_label(ad["status"])
        spend_str = _fmt_spend(ad["spend"])
        creative_type = ad.get("creative_type", "Imagem")
        preview_url = ad.get("preview_url") or _FALLBACK_IMG

        # Ícone do tipo de criativo
        if creative_type == "Vídeo":
            type_icon = '<i class="bi bi-camera-video-fill"></i>'
        else:
            type_icon = '<i class="bi bi-image-fill"></i>'

        with cols[i % 3]:
            # ── Card container (abertura) ──
            st.markdown(f"""
            <div class="glass-card" style="padding: 16px; margin-bottom: 24px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
            """, unsafe_allow_html=True)

            # ── Preview real via st.image ──
            try:
                st.image(preview_url, use_container_width=True)
            except Exception:
                st.image(_FALLBACK_IMG, use_container_width=True)

            # ── Metadados + status ──
            st.markdown(f"""
                <h4 style="margin: 8px 0 10px 0; font-size: 0.95rem; color: #FAFAFA; line-height: 1.3;">{ad['nome']}</h4>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 0.9rem; color:#9CA3AF;">{type_icon}</span>
                        <span style="font-size: 0.8rem; color: #9CA3AF;">{creative_type}</span>
                    </div>
                    <span style="font-size: 0.9rem; font-weight: 600; color: #FAFAFA; letter-spacing: -0.3px;">
                        <i class="bi bi-cash" style="margin-right:3px; color:#00d592;"></i>{spend_str}
                    </span>
                </div>
                <div style="display: inline-block; align-self: flex-start; padding: 4px 12px; border-radius: 20px; background: {status_bg}; border: 1px solid {status_color};">
                    <span style="color: {status_color}; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px;">{label}</span>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)


# ── Integração Gemini — Chamada de IA ────────────────────────────────────────

def _build_brain_context(projeto: dict) -> str:
    """Monta o contexto simulado do Perfor Brain (Personas, Dores, Soluções)."""
    nome = get_project_display_name(projeto)
    nicho = projeto.get("nicho") or projeto.get("categoria") or "e-commerce"
    return f"""## Perfor Brain — {nome}
**Nicho:** {nicho}

### Buyer Personas Mapeadas
1. **O Cliente Inseguro** — Tem interesse mas precisa de muita prova social e garantia para converter.
2. **O Comprador Prático** — Busca agilidade, frete rápido e praticidade no checkout.
3. **O Buscador de Resultado** — Foco total nos benefícios tangíveis e transformação real.
4. **O Comparador de Preço** — Pesquisa em vários concorrentes antes de decidir.
5. **O Cliente Premium** — Prioriza qualidade e experiência acima do preço.

### Dores Mapeadas
- Medo de comprar online e não receber o produto ou receber algo diferente.
- Frustração com atendimento pós-venda ruim em concorrentes.
- Dúvida sobre a eficácia/qualidade real do produto.
- Comparação constante de preço entre marcas similares.
- Falta de confiança em marcas novas ou pouco conhecidas.

### Soluções e Alavancas do Produto
- Garantia incondicional de satisfação (7-30 dias).
- Frete grátis ou frete expresso como diferencial competitivo.
- Depoimentos reais e resultados comprovados de clientes.
- Preço reposicionado ("menos de R$ X por dia").
- Certificações, laudos técnicos e autoridade do especialista.
"""


def _build_ads_table(ads: list[dict]) -> str:
    """Formata os anúncios ativos como tabela Markdown para o prompt."""
    if not ads:
        return "_Nenhum anúncio com gasto encontrado no período._"
    lines = ["| # | Nome do Anúncio | Status | Tipo | Gasto (R$) |"]
    lines.append("|---|---|---|---|---|")
    for i, ad in enumerate(ads, 1):
        status_label = {"ACTIVE": "Ativo", "PAUSED": "Pausado"}.get(ad["status"], ad["status"])
        lines.append(
            f"| {i} | {ad['nome']} | {status_label} | {ad.get('creative_type', '—')} | {ad['spend']:.2f} |"
        )
    return "\n".join(lines)


def _call_gemini(system_prompt: str, user_message: str) -> str:
    """Chama a API do Gemini e retorna a resposta em texto."""
    from google import genai

    api_key = st.secrets["gemini"]["api_key"]
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.8,
            max_output_tokens=4096,
        ),
    )
    return response.text


# ── Componente Visual: Diretor de Arte Inteligente ───────────────────────────

def _render_ai_director(projeto: dict, ads: list[dict]) -> None:
    """
    Renderiza o expander do Diretor de Arte Inteligente (Matriz Criativa).
    Carrega o guia de inteligência como System Prompt e cruza com dados
    de anúncios + Perfor Brain para gerar roteiros via Gemini.
    """
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    with st.expander("🎬 Diretor de Arte Inteligente (Matriz Criativa)", expanded=False):
        prompt_guide = get_agent_prompt(_GUIDE_FILE)

        # ── Guia não encontrado ──────────────────────────────────────────
        if prompt_guide is None:
            st.markdown(f"""
            <div style="padding:20px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:12px; color:#F59E0B;">
                    <i class="bi bi-file-earmark-text"></i>
                </div>
                <h4 style="color:#FAFAFA; margin:0 0 8px 0; font-size:0.95rem;">Guia de Inteligência Pendente</h4>
                <p style="color:#6b7280; font-size:0.82rem; margin:0 0 12px 0;">
                    O arquivo <code style="color:#FCD34D;">{_GUIDE_FILE}</code> ainda não foi adicionado
                    à pasta <code style="color:#FCD34D;">intelligence_guides/</code>.
                </p>
                <p style="color:#4b5563; font-size:0.72rem; margin:0;">
                    Adicione o manual para ativar o Copiloto de Análise Criativa.
                </p>
            </div>
            """, unsafe_allow_html=True)
            return

        # ── Chave Gemini não configurada ─────────────────────────────────
        gemini_secrets = st.secrets.get("gemini")
        if not gemini_secrets or not gemini_secrets.get("api_key"):
            st.markdown("""
            <div style="padding:20px; text-align:center;">
                <div style="font-size:1.8rem; margin-bottom:12px; color:#60A5FA;"><i class="bi bi-key"></i></div>
                <h4 style="color:#FAFAFA; margin:0 0 8px 0; font-size:0.95rem;">Chave do Gemini Pendente</h4>
                <p style="color:#6b7280; font-size:0.82rem; margin:0;">Adicione <code style="color:#60A5FA;">[gemini] api_key</code> no secrets.toml.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # ── Header com métricas ──────────────────────────────────────────
        nome_projeto = get_project_display_name(projeto)
        total_ads = len(ads)
        total_spend = sum(ad.get("spend", 0) for ad in ads)
        ativos = sum(1 for ad in ads if ad["status"] == "ACTIVE")

        st.markdown(f"""
        <div style="padding:16px 20px; background:rgba(0,213,146,0.04); border:1px solid rgba(0,213,146,0.15); border-radius:10px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <i class="bi bi-cpu" style="font-size:1.2rem; color:#00d592;"></i>
                <span style="color:#FAFAFA; font-weight:600; font-size:0.9rem;">Copiloto Criativo — {nome_projeto}</span>
            </div>
            <p style="color:#9CA3AF; font-size:0.8rem; margin:0; line-height:1.6;">
                <strong style="color:#FAFAFA;">{total_ads}</strong> criativos analisados ·
                <strong style="color:#FAFAFA;">{ativos}</strong> ativos ·
                Investimento total: <strong style="color:#00d592;">{_fmt_spend(total_spend)}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Botão de Geração ─────────────────────────────────────────────
        if st.button("⚡ Gerar Matriz Criativa via Gemini", key="btn_gen_matrix", use_container_width=True):
            brain_ctx = _build_brain_context(projeto)
            ads_table = _build_ads_table(ads)

            user_message = f"""## Dados de Entrada para Análise

### Contexto Estratégico (Perfor Brain)
{brain_ctx}

### Anúncios Ativos no Meta Ads (período selecionado)
{ads_table}

---

## Solicitação
Com base no protocolo de auditoria do guia, analise os anúncios acima e entregue:
1. **Auditoria rápida** dos criativos atuais (winners vs. fadiga).
2. **3 roteiros novos de vídeo** (1 DSB, 1 Full Funnel, 1 UGC) seguindo a anatomia Gancho → Conteúdo → CTA.
3. **2 briefings de imagem/carrossel** para remarketing (Prova Social + Objeção Direta).
4. Para cada briefing, indique o Pilar, Persona Alvo, Gancho, Conteúdo e CTA conforme o formato de entrega.
"""
            with st.spinner("Gerando Matriz Criativa com Gemini..."):
                try:
                    resposta = _call_gemini(
                        system_prompt=prompt_guide,
                        user_message=user_message,
                    )
                    st.session_state["_ai_matrix_result"] = resposta
                except Exception as e:
                    st.error(f"Erro na chamada do Gemini: {e}")

        # ── Exibe resultado salvo ────────────────────────────────────────
        resultado = st.session_state.get("_ai_matrix_result")
        if resultado:
            st.markdown("<hr style='border:none; border-top:1px solid #1f2937; margin:16px 0;'>", unsafe_allow_html=True)
            st.markdown(resultado)


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PÚBLICA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render_criativos() -> None:
    render_cargo_badge(
        "✦ Criativos Meta Ads",
        "Anúncios ativos e performance de criativos em tempo real.",
    )

    # ── Verifica projeto ativo ────────────────────────────────────────────────
    projeto = get_active_project()

    if projeto is None:
        st.markdown(
            """<div class="glass-card" style="text-align:center; padding:40px 32px;">
                <div style="font-size:2rem; margin-bottom:14px; color:#3B82F6;"><i class="bi bi-bullseye"></i></div>
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
        nome_proj = projeto.get("nome_cliente") or projeto.get("nome", "Projeto")
        html_erro = f"""
        <div class="glass-card" style="border-color:rgba(251,191,36,0.4); background:linear-gradient(135deg, rgba(251,191,36,0.06) 0%, rgba(12,12,12,0.70) 100%); padding:32px 28px; text-align:center;">
        <div style="font-size:2rem; margin-bottom:14px; color:#FCD34D;"><i class="bi bi-gear-fill"></i></div>
        <h3 style="color:#FCD34D; margin:0 0 8px 0; font-size:1rem;">Conta Meta Não Configurada</h3>
        <p style="color:#9CA3AF; font-size:0.85rem; max-width:480px; margin:0 auto 16px auto; line-height:1.7;">Não foi possível carregar os anúncios para <strong style="color:#FAFAFA;">{nome_proj}</strong>.</p>
        <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(251,191,36,0.2); border-radius:8px; padding:10px 16px; display:inline-block; max-width:600px;">
        <p style="color:#6b7280; font-size:0.75rem; margin:0; font-family:monospace; letter-spacing:0.3px;">meta_account_id não definido no Supabase.</p>
        </div>
        <p style="color:#4b5563; font-size:0.75rem; margin:16px 0 0 0;">Verifique o campo <code style="color:#FCD34D;">meta_account_id</code> na tabela de projetos para visualizar os criativos.</p>
        </div>
        """
        st.markdown(html_erro, unsafe_allow_html=True)
        return

    # ── Seletor de Mês (reutiliza a mesma chave do dashboard) ────────────────
    mes_sel = st.session_state.get("sel_mes_dashboard")
    if not mes_sel:
        hoje = date.today()
        idx = hoje.month - 1
        if hoje.day <= 5 and hoje.month > 1:
            idx = hoje.month - 2
        mes_sel = MESES_ABREV[idx]

    since, until = _get_month_range(mes_sel)

    st.markdown(
        f"<p style='color:#6b7280; font-size:0.85rem; margin-bottom:20px; text-align:right;'>"
        f"Meta Account: <strong>{meta_account_id}</strong> · "
        f"Período: <strong>{mes_sel}</strong></p>",
        unsafe_allow_html=True,
    )

    # ── Inicializa a API do Meta ─────────────────────────────────────────────
    meta_ok = _init_meta_api()

    if not meta_ok:
        # Credenciais do Meta não configuradas — mostra aviso amigável
        st.markdown("""
        <div class="glass-card" style="border-color:rgba(59,130,246,0.4); background:linear-gradient(135deg, rgba(59,130,246,0.06) 0%, rgba(12,12,12,0.70) 100%); padding:32px 28px; text-align:center;">
            <div style="font-size:2rem; margin-bottom:14px; color:#60A5FA;"><i class="bi bi-key-fill"></i></div>
            <h3 style="color:#60A5FA; margin:0 0 8px 0; font-size:1rem;">Credenciais do Meta Pendentes</h3>
            <p style="color:#9CA3AF; font-size:0.85rem; max-width:520px; margin:0 auto 16px auto; line-height:1.7;">
                Para conectar à API do Meta Ads, adicione as credenciais no arquivo de configuração.
            </p>
            <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(59,130,246,0.2); border-radius:8px; padding:14px 20px; display:inline-block; max-width:600px; text-align:left;">
                <p style="color:#60A5FA; font-size:0.72rem; margin:0 0 8px 0; letter-spacing:1px; font-weight:600;">SECRETS.TOML</p>
                <code style="color:#9CA3AF; font-size:0.78rem; line-height:1.8; white-space:pre; font-family:'Fira Code', monospace;">[meta_ads]
app_id = "SEU_APP_ID"
access_token = "SEU_ACCESS_TOKEN"</code>
            </div>
            <p style="color:#4b5563; font-size:0.72rem; margin:16px 0 0 0;">
                <i class="bi bi-shield-lock" style="margin-right:3px;"></i>
                Adicione na seção <code style="color:#60A5FA;">[meta_ads]</code> do <code style="color:#60A5FA;">.streamlit/secrets.toml</code>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Renderiza o expander do Diretor de Arte mesmo sem dados da API
        _render_ai_director(projeto, [])
        return

    # ── Busca os anúncios da API ─────────────────────────────────────────────
    with st.spinner("Conectando ao Meta Ads..."):
        data = _fetch_meta_ads(meta_account_id, since, until)

    if data.get("erro"):
        st.markdown(f"""
        <div class="glass-card" style="border-color:rgba(239,68,68,0.3); background:linear-gradient(135deg, rgba(239,68,68,0.06) 0%, rgba(12,12,12,0.70) 100%); padding:28px; text-align:center;">
            <div style="font-size:1.8rem; margin-bottom:12px; color:#EF4444;"><i class="bi bi-exclamation-triangle-fill"></i></div>
            <h3 style="color:#EF4444; margin:0 0 8px 0; font-size:1rem;">Erro ao Buscar Anúncios</h3>
            <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(239,68,68,0.2); border-radius:8px; padding:10px 16px; margin-top:12px; display:inline-block; max-width:600px;">
                <p style="color:#6b7280; font-size:0.75rem; margin:0; font-family:monospace;">{data['erro']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Corte estrito: Top 20 por gasto (Pandas) ──────────────────────────
    import pandas as pd

    ads_raw = data["ads"]
    if ads_raw:
        df = pd.DataFrame(ads_raw)
        df["spend"] = df["spend"].astype(float)
        df = df.sort_values("spend", ascending=False).head(20)
        ads = df.to_dict(orient="records")
    else:
        ads = []

    if not ads:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:40px 32px;">
            <div style="font-size:2rem; margin-bottom:14px; color:#6b7280;"><i class="bi bi-megaphone"></i></div>
            <h3 style="color:#FAFAFA; margin:0 0 8px 0; font-size:1rem;">Nenhum Criativo com Gasto</h3>
            <p style="color:#6b7280; font-size:0.85rem; margin:0;">
                Não foram encontrados anúncios com gasto no período de <strong style="color:#FAFAFA;">{mes_sel}</strong>
                para a conta <strong style="color:#FAFAFA;">{meta_account_id}</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        _render_ai_director(projeto, [])
        return

    # ── Resumo rápido ────────────────────────────────────────────────────────
    total_spend = sum(a["spend"] for a in ads)
    total_ativos = sum(1 for a in ads if a["status"] == "ACTIVE")

    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;">
        <div style="background:rgba(0,213,146,0.06); border:1px solid rgba(0,213,146,0.15); border-radius:10px; padding:12px 20px; flex:1; min-width:180px;">
            <p style="color:#6b7280; font-size:0.68rem; letter-spacing:1.2px; margin:0 0 4px 0;">CRIATIVOS ENCONTRADOS</p>
            <p style="color:#FAFAFA; font-size:1.5rem; font-weight:700; margin:0; letter-spacing:-0.5px;">{len(ads)}</p>
        </div>
        <div style="background:rgba(0,213,146,0.06); border:1px solid rgba(0,213,146,0.15); border-radius:10px; padding:12px 20px; flex:1; min-width:180px;">
            <p style="color:#6b7280; font-size:0.68rem; letter-spacing:1.2px; margin:0 0 4px 0;">ATIVOS NO PERÍODO</p>
            <p style="color:#00d592; font-size:1.5rem; font-weight:700; margin:0; letter-spacing:-0.5px;">{total_ativos}</p>
        </div>
        <div style="background:rgba(0,213,146,0.06); border:1px solid rgba(0,213,146,0.15); border-radius:10px; padding:12px 20px; flex:1; min-width:180px;">
            <p style="color:#6b7280; font-size:0.68rem; letter-spacing:1.2px; margin:0 0 4px 0;">GASTO TOTAL ({mes_sel})</p>
            <p style="color:#FAFAFA; font-size:1.5rem; font-weight:700; margin:0; letter-spacing:-0.5px;">{_fmt_spend(total_spend)}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Grid de Cards ────────────────────────────────────────────────────────
    _render_ad_cards(ads)

    # ── Diretor de Arte IA ───────────────────────────────────────────────────
    _render_ai_director(projeto, ads)
