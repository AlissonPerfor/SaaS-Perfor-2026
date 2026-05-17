"""
modules/creative_analysis.py — Módulo Criativos Perfor.IA (Axoly Style)
"""
import calendar, json
from datetime import date
from typing import Optional
import streamlit as st
import pandas as pd

from core.context import (
    get_active_project, get_all_projects, get_project_display_name,
    render_cargo_badge, get_agent_prompt,
)
from core.sheets import MESES_ABREV

_GUIDE_FILE = "MATRIZ_CRIATIVA_IA_guia-inteligencia.md"
_FALLBACK = "https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=400&q=60"

# ── Helpers ──────────────────────────────────────────────────────────────────

def _month_range(m):
    try: mn = MESES_ABREV.index(m)+1
    except: mn = date.today().month
    y = date.today().year
    if mn > date.today().month: y -= 1
    ld = calendar.monthrange(y, mn)[1]
    return f"{y}-{mn:02d}-01", f"{y}-{mn:02d}-{ld:02d}"

def _xval(actions, types=("purchase","omni_purchase")):
    if not actions: return 0
    for a in actions:
        if a.get("action_type") in types:
            return float(a.get("value",0))
    return 0

def _fmt_brl(v):
    if v is None: return "R$ 0,00"
    if v >= 1000: return f"R$ {v/1000:.1f}k".replace(".",",")
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def _fmt_pct(v): return f"{v:.2f}%".replace(".",",") if v else "0,00%"
def _fmt_roas(v): return f"{v:.2f}x".replace(".",",") if v else "0,00x"

# ── Meta API Init ────────────────────────────────────────────────────────────

def _init_meta_api():
    try:
        from facebook_business.api import FacebookAdsApi
        
        # 1. Correção Universal das Chaves (Segurança Máxima)
        meta_token = st.secrets.get('meta_ads', {}).get('access_token', '').strip('"')
        meta_app_id = st.secrets.get('meta_ads', {}).get('app_id', '').strip('"')
        
        if not meta_token: return False
        FacebookAdsApi.init(meta_app_id, "", meta_token)
        return True
    except Exception as e:
        print(f"[Meta] {e}"); return False

# ── Fetch Enriched Ads ───────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_meta_ads(account_id, since, until):
    result = {"ads": [], "erro": None, "agg": {}}
    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.ad import Ad
        if not account_id.startswith("act_"): account_id = f"act_{account_id}"
        account = AdAccount(account_id)

        rows = account.get_insights(
            fields=["ad_id","ad_name","spend","impressions","cpm","ctr",
                    "inline_link_click_ctr","actions","cost_per_action_type",
                    "purchase_roas","video_p75_watched_actions"],
            params={"level":"ad","time_range":{"since":since,"until":until},
                    "sort":["spend_descending"],"limit":20,
                    "filtering":[{"field":"spend","operator":"GREATER_THAN","value":"0"}]},
        )

        t_spend=t_imp=t_purchases=n=n_vid=0; s_cpm=s_ctr=s_lctr=s_tsr=s_roas=s_hold=0
        for r in rows:
            spend=float(r.get("spend",0)); imp=int(r.get("impressions",0))
            cpm=float(r.get("cpm",0)); ctr_all=float(r.get("ctr",0))
            ctr_link=float(r.get("inline_link_click_ctr",0))
            acts = r.get("actions", [])
            purchases=int(_xval(acts))
            cpa=_xval(r.get("cost_per_action_type"))
            roas=_xval(r.get("purchase_roas"))
            v3s=int(_xval(acts,("video_view",)))
            tsr=(v3s/imp*100) if imp>0 else 0
            
            # Tenta pegar das actions ou do field direto
            v75=int(_xval(acts,("video_p75_watched_actions",))) or int(_xval(r.get("video_p75_watched_actions",[]), ("video_p75_watched_actions",)))
            hold_rate=(v75/imp*100) if imp>0 else 0

            t_spend+=spend; t_imp+=imp; t_purchases+=purchases; n+=1
            s_cpm+=cpm; s_ctr+=ctr_all; s_lctr+=ctr_link; s_roas+=roas

            preview=None; ctype="Imagem"; status="ACTIVE"; permalink=None
            try:
                ao=Ad(r.get("ad_id")).api_get(fields=["status","creative"])
                status=ao.get("status","ACTIVE")
                c_id=ao.get("creative",{}).get("id")
                if c_id:
                    from facebook_business.adobjects.adcreative import AdCreative
                    cr=AdCreative(c_id).api_get(fields=["image_url","thumbnail_url","video_id","object_story_spec","instagram_permalink_url","effective_object_story_id"])
                    
                    ig_link = cr.get("instagram_permalink_url")
                    eff_id = cr.get("effective_object_story_id")
                    if ig_link: permalink = ig_link
                    elif eff_id: permalink = f"https://facebook.com/{eff_id}"
                    else: permalink = f"https://facebook.com/{r.get('ad_id')}"
                    
                    oss = cr.get("object_story_spec", {})
                    
                    # Tenta buscar a imagem original (alta resolução) nas specs
                    high_res = None
                    if "video_data" in oss: high_res = oss["video_data"].get("image_url")
                    elif "link_data" in oss: high_res = oss["link_data"].get("picture")
                    elif "photo_data" in oss: high_res = oss["photo_data"].get("url")
                    
                    iu=cr.get("image_url"); tu=cr.get("thumbnail_url"); vi=cr.get("video_id")
                    
                    if vi or "video_data" in oss: 
                        ctype="Vídeo"
                        preview = high_res or iu or tu
                    else: 
                        ctype="Imagem"
                        preview = high_res or iu or tu
            except: pass
            
            if ctype == "Vídeo":
                s_tsr += tsr; s_hold += hold_rate; n_vid += 1

            result["ads"].append({"ad_id":r.get("ad_id"),"nome":r.get("ad_name","?"),"status":status,"spend":spend,
                "preview_url":preview,"creative_type":ctype,"cpm":cpm,"tsr":tsr,"hold_rate":hold_rate,
                "ctr_all":ctr_all,"ctr_link":ctr_link,"purchases":purchases,
                "cpa":cpa,"roas":roas,"permalink":permalink})

        if n>0:
            avg_tsr = s_tsr/n_vid if n_vid>0 else 0
            avg_hold = s_hold/n_vid if n_vid>0 else 0
            result["agg"]={"cpm":s_cpm/n,"tsr":avg_tsr,"hold_rate":avg_hold,"ctr_all":s_ctr/n,"ctr_link":s_lctr/n,
                "purchases":t_purchases,"cpa":t_spend/t_purchases if t_purchases>0 else 0,
                "roas":s_roas/n,"spend":t_spend}
    except Exception as e:
        result["erro"]=str(e)
    return result

# ── Render: 8 Macro Cards (Axoly Style) ──────────────────────────────────────

def _render_macro_cards(agg):
    metrics = [
        ("CPM", _fmt_brl(agg.get("cpm")), "MÉDIA DO PERÍODO", "#3B82F6"),
        ("Thumb Stop Rate", _fmt_pct(agg.get("tsr")), "MÉDIA DO PERÍODO", "#8B5CF6"),
        ("CTR (Todos)", _fmt_pct(agg.get("ctr_all")), "MÉDIA DO PERÍODO", "#F59E0B"),
        ("CTR (Link)", _fmt_pct(agg.get("ctr_link")), "MÉDIA DO PERÍODO", "#EF4444"),
        ("Compras", str(int(agg.get("purchases",0))), "TOTAL DO PERÍODO", "#00d592"),
        ("CPA", _fmt_brl(agg.get("cpa")), "MÉDIA DO PERÍODO", "#F59E0B"),
        ("ROAS", _fmt_roas(agg.get("roas")), "MÉDIA DO PERÍODO", "#8B5CF6"),
        ("Valor Gasto", _fmt_brl(agg.get("spend")), "TOTAL DO PERÍODO", "#3B82F6"),
    ]
    cols = st.columns(8, gap="small")
    for col, (label, val, sub, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""<div class="glass-card" style="padding:14px 10px;text-align:left;min-height:110px;">
<p style="color:{color};font-size:0.68rem;font-weight:600;margin:0 0 2px 0;letter-spacing:0.5px;">{label}</p>
<p style="color:#6b7280;font-size:0.58rem;letter-spacing:1px;margin:0 0 8px 0;">{sub}</p>
<p style="color:#FAFAFA;font-size:1.3rem;font-weight:700;margin:0;letter-spacing:-0.5px;">{val}</p>
</div>""", unsafe_allow_html=True)

# ── Render: Diagnóstico Executivo ────────────────────────────────────────────

def _render_diagnostico(agg, mes):
    roas=agg.get("roas",0); p=int(agg.get("purchases",0))
    ctr=agg.get("ctr_all",0); tsr=agg.get("tsr",0); cpa=agg.get("cpa",0)
    diag = f"Com um ROAS de {_fmt_roas(roas)} e {p} compras, a conta "
    diag += "apresenta retorno positivo. " if roas>1 else "precisa de otimização urgente. "
    diag += f"O CTR geral de {_fmt_pct(ctr)} "
    diag += "está saudável." if ctr>1 else "indica necessidade de novos ganchos criativos."

    st.markdown(f"""<div class="glass-card" style="padding:24px 28px;">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
<span style="font-size:1.1rem;">📊</span>
<span style="color:#FAFAFA;font-weight:700;font-size:0.95rem;">Diagnóstico da Conta</span>
</div>
<p style="color:#6b7280;font-size:0.7rem;margin:0 0 16px 0;">Análise executiva por IA — {mes}</p>
<p style="color:#FAFAFA;font-weight:600;font-size:0.85rem;margin:0 0 6px 0;">📌 Diagnóstico do Período</p>
<p style="color:#9CA3AF;font-size:0.82rem;line-height:1.7;margin:0 0 20px 0;">{diag}</p>
<p style="color:#FAFAFA;font-weight:600;font-size:0.85rem;margin:0 0 10px 0;">🚀 3 Ações para a Próxima Semana</p>
<ol style="color:#9CA3AF;font-size:0.8rem;line-height:1.8;margin:0;padding-left:18px;">
<li>Testar novos ganchos visuais para melhorar o CTR (Todos) e a Thumb Stop Rate.</li>
<li>Criar variação de copies nos anúncios ativos focando em dores e benefícios.</li>
<li>{"Escalar os criativos campeões com aumento gradual de orçamento." if roas>1.5 else "Pausar criativos com CPA acima da meta e redistribuir verba."}</li>
</ol>
<p style="color:#6b7280;font-size:0.75rem;margin:14px 0 0 0;">⭐ Veredito: <strong style="color:#FAFAFA;">{"Manter & Otimizar" if roas>1 else "Reestruturar Criativos"}</strong></p>
</div>""", unsafe_allow_html=True)

# ── Render: Top Performers (Axoly Insights) ──────────────────────────────────

def _render_top_performers(ads):
    if len(ads)<1: return
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;font-size:0.72rem;letter-spacing:1.5px;margin-bottom:10px;'><i class='bi bi-stars' style='margin-right:4px;'></i> PERFOR INSIGHTS — Top Performers</p>", unsafe_allow_html=True)
    df=pd.DataFrame(ads)
    champs=[
        ("🥇 Melhor Gancho","tsr","THUMB STOP RATE",_fmt_pct),
        ("⚡ Melhor CTR","ctr_all","CTR",_fmt_pct),
        ("🛒 Mais Compras","purchases","COMPRAS",lambda v:str(int(v))),
        ("📈 Maior ROAS","roas","ROAS",_fmt_roas),
    ]
    cols=st.columns(4,gap="medium")
    for col,(title,key,sub,fmt) in zip(cols,champs):
        if key not in df.columns: continue
        best=df.loc[df[key].idxmax()]
        url=best.get("preview_url") or _FALLBACK
        with col:
            st.markdown(f"""<div class="glass-card" style="padding:16px; display:flex; flex-direction:column; height:100%; justify-content:space-between;">
    <div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
            <span style="font-size:1.1rem;">{title.split(' ')[0]}</span>
            <span style="color:#FAFAFA; font-weight:600; font-size:0.85rem;">{' '.join(title.split(' ')[1:])}</span>
        </div>
        <img src="{url}" style="width:100%; aspect-ratio:1/1; object-fit:cover; border-radius:8px; margin-bottom:14px; border:1px solid rgba(255,255,255,0.05);" onerror="this.src='{_FALLBACK}'" />
        <p style="color:#FAFAFA; font-size:0.85rem; font-weight:500; margin:0 0 16px 0; line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">{best['nome']}</p>
    </div>
    <div>
        <p style="color:#6b7280; font-size:0.65rem; font-weight:600; letter-spacing:1px; margin:0 0 2px 0;">{sub}</p>
        <p style="color:#00d592; font-size:1.4rem; font-weight:700; margin:0; letter-spacing:-0.5px;">{fmt(best[key])}</p>
    </div>
</div>""", unsafe_allow_html=True)

# ── Render: Grid de Criativos com Métricas Dedicadas ─────────────────────────

def _render_ad_cards(ads, agg):
    st.markdown(f"<p style='color:#6b7280;font-size:0.85rem;margin:20px 0 12px 0;'><strong style='color:#FAFAFA;'>Criativos ({len(ads)})</strong> — Top por gasto</p>", unsafe_allow_html=True)
    cols=st.columns(5, gap="small")
    for i,ad in enumerate(ads):
        lbl="Ativo" if ad["status"]=="ACTIVE" else "Pausado"
        lc="#00d592" if ad["status"]=="ACTIVE" else "#FCD34D"
        tc="🎬 Vídeo" if ad.get("creative_type")=="Vídeo" else "🖼️ Imagem"
        url=ad.get("preview_url") or _FALLBACK
        with cols[i%5]:
            st.markdown(f"""<div class="glass-card" style="padding:14px; height:100%;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
<span style="background:{lc}; color:#000; font-size:0.65rem; font-weight:700; padding:3px 10px; border-radius:12px; letter-spacing:0.5px;">{lbl}</span>
<span style="color:#9CA3AF; font-size:0.75rem; font-weight:500;">{tc}</span>
</div>

<img src="{url}" style="width:100%; aspect-ratio:4/5; object-fit:cover; border-radius:8px; margin-bottom:14px; border:1px solid rgba(255,255,255,0.05);" onerror="this.src='{_FALLBACK}'" />

<p style="color:#FAFAFA; font-size:0.85rem; font-weight:600; margin:0 0 16px 0; line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; min-height:2.8em;">{ad['nome']}</p>

<div style="font-size:0.72rem; line-height:2.0;">
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">CPM</span><span style="color:#FAFAFA; font-weight:500;">{_fmt_brl(ad.get('cpm',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">Thumb Stop Rate</span><span style="color:#FAFAFA; font-weight:500;">{_fmt_pct(ad.get('tsr',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">CTR (Todos)</span><span style="color:#FAFAFA; font-weight:500;">{_fmt_pct(ad.get('ctr_all',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">CTR (Link)</span><span style="color:#FAFAFA; font-weight:500;">{_fmt_pct(ad.get('ctr_link',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">Compras</span><span style="color:#FAFAFA; font-weight:500;">{int(ad.get('purchases',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">CPA</span><span style="color:#FAFAFA; font-weight:500;">{_fmt_brl(ad.get('cpa',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; margin-bottom:4px;">
<span style="color:#9CA3AF;">ROAS</span><span style="color:#00d592; font-weight:600;">{_fmt_roas(ad.get('roas',0))}</span>
</div>
<div style="display:flex; justify-content:space-between; padding-top:2px;">
<span style="color:#9CA3AF;">Valor Gasto</span><span style="color:#FAFAFA; font-weight:500;">{_fmt_brl(ad.get('spend',0))}</span>
</div>
</div>
</div>""", unsafe_allow_html=True)
            
            link = ad.get("permalink")
            if link:
                st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
                st.link_button("🔗 Ver Material Original", url=link, use_container_width=True)
            if st.button("🧠 Rodar Raio-X da IA", key=f"rx_{ad.get('ad_id', i)}_{i}", use_container_width=True):
                _show_ad_insights(get_active_project(), ad, agg)

# ── Gemini Helpers ───────────────────────────────────────────────────────────

def _build_brain(p):
    n=get_project_display_name(p); ni=p.get("nicho") or "e-commerce"
    return f"""## Perfor Brain — {n} (Nicho: {ni})
### Personas: O Inseguro, O Prático, O Buscador de Resultado, O Comparador, O Premium
### Dores: Medo de compra online, atendimento ruim, dúvida de qualidade, comparação de preço
### Soluções: Garantia, frete grátis, depoimentos reais, preço reposicionado, autoridade técnica"""

def _call_gemini(system, user):
    import os
    from google import genai
    
    key = ""
    try: key = st.secrets["gemini"]["api_key"]
    except: pass
    if not key:
        try: key = st.secrets["GEMINI_API_KEY"]
        except: pass
    if not key:
        key = os.environ.get("GEMINI_API_KEY", "")
        
    if isinstance(key, str): key = key.strip('"')
    
    if not key:
        raise ValueError("Chave do Gemini ausente no secrets.toml ou variaveis de ambiente.")
    
    client=genai.Client(api_key=key)
    r=client.models.generate_content(model="gemini-2.5-flash",contents=user,
        config=genai.types.GenerateContentConfig(system_instruction=system,temperature=0.8,max_output_tokens=4096))
    return r.text

@st.dialog("🧠 Axoly Creative Insights", width="large")
def _show_ad_insights(projeto, ad, agg):
    st.markdown(f"**Analisando:** `{ad['nome']}`")
    guide=get_agent_prompt(_GUIDE_FILE)
    if not guide:
        st.error(f"Guia `{_GUIDE_FILE}` não encontrado.")
        return

    msg = f"""## Dados de Entrada
{_build_brain(projeto)}

### Benchmarks da Conta (Média Atual)
- TSR Médio: {_fmt_pct(agg.get('tsr', 0))}
- Hold Rate Médio: {_fmt_pct(agg.get('hold_rate', 0))}
- CTR Médio: {_fmt_pct(agg.get('ctr_all', 0))}
- CPA Médio: {_fmt_brl(agg.get('cpa', 0))}
- ROAS Médio: {_fmt_roas(agg.get('roas', 0))}

### Desempenho do Anúncio (Isolado)
- Nome: {ad['nome']}
- Tipo: {ad.get('creative_type', 'Imagem')}
- Investimento: {_fmt_brl(ad['spend'])}
- CPM: {_fmt_brl(ad.get('cpm',0))}
- Thumb Stop Rate (Gancho): {_fmt_pct(ad.get('tsr',0))}
- Hold Rate (Retenção 75%): {_fmt_pct(ad.get('hold_rate',0))}
- CTR Todos (Engajamento): {_fmt_pct(ad.get('ctr_all',0))}
- CTR Link (Clique de Saída): {_fmt_pct(ad.get('ctr_link',0))}
- Compras: {int(ad.get('purchases',0))}
- CPA: {_fmt_brl(ad.get('cpa',0))}
- ROAS: {_fmt_roas(ad.get('roas',0))}

---
## Solicitação (formato Axoly)
Analise APENAS este criativo e entregue a resposta em Markdown limpo (SEM tabelas), dividida estritamente nas seguintes seções:

🧠 **Análise por Etapa**
Se o Tipo for 'Vídeo':
- Gancho (0-3s): Compare o TSR do criativo com o TSR Médio da conta.
- Conteúdo (Desenvolvimento): Compare o Hold Rate (Retenção 75%) do criativo com o Hold Rate Médio da conta.
- Conversão (CTA): Analise o CTR (Todos/Link) para avaliar se o vídeo induz bem ao clique em comparação ao CTR Médio.
Se o Tipo for 'Imagem' ou Catálogo, IGNORE Gancho e Hold Rate, e avalie apenas a atratividade visual baseada no CTR.

🛒 **Conversão Final**
Analise o volume de Vendas, o CPA e o ROAS em relação às médias da conta para determinar a lucratividade real pós-clique.

⚠️ **Gargalo Principal**
Identifique o ponto fraco dominante do criativo baseado nos dados acima.

🎯 **Ação Recomendada**
O que fazer taticamente (testar ganchos, mudar CTA, pausar, manter, escalar).

📊 **Classificação**
(Apenas uma das opções: Winners, Testar Variações, ou Pausar)
"""
    with st.spinner("Analisando métricas do criativo..."):
        try:
            res = _call_gemini(guide, msg)
            st.markdown(res)
        except Exception as e:
            st.error(f"Erro ao chamar a IA: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render_criativos():
    render_cargo_badge("✦ Criativos Meta Ads","Análise de criativos em tempo real")
    projeto=get_active_project()
    if projeto is None:
        st.markdown('<div class="glass-card" style="text-align:center;padding:40px;"><h3 style="color:#FAFAFA;">Selecione um Projeto</h3><p style="color:#6b7280;">Escolha um projeto na sidebar.</p></div>', unsafe_allow_html=True)
        return
    if not get_all_projects(): st.warning("Nenhum projeto."); return
    meta_id=projeto.get("meta_account_id")
    if not meta_id:
        st.markdown(f'<div class="glass-card" style="text-align:center;padding:32px;"><p style="color:#FCD34D;font-size:1.5rem;"><i class="bi bi-gear-fill"></i></p><h3 style="color:#FCD34D;font-size:1rem;">Meta Não Configurado</h3><p style="color:#6b7280;font-size:0.82rem;">meta_account_id ausente no Supabase.</p></div>', unsafe_allow_html=True)
        return
    mes=st.session_state.get("sel_mes_dashboard")
    if not mes:
        h=date.today(); idx=h.month-1
        if h.day<=5 and h.month>1: idx=h.month-2
        mes=MESES_ABREV[idx]
    since,until=_month_range(mes)
    st.markdown(f"<p style='color:#6b7280;font-size:0.82rem;text-align:right;margin-bottom:16px;'>Conectado · <strong>act_{meta_id}</strong> · {mes}</p>", unsafe_allow_html=True)

    if not _init_meta_api():
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:32px;">
            <p style="color:#60A5FA;font-size:1.5rem;"><i class="bi bi-key-fill"></i></p>
            <h3 style="color:#60A5FA;font-size:1rem;">Credenciais Meta Pendentes</h3>
            <p style="color:#6b7280;font-size:0.82rem;">Adicione <code style="color:#60A5FA;">[meta_ads] access_token</code> no secrets.toml.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    with st.spinner("Conectando ao Meta Ads..."):
        data=_fetch_meta_ads(meta_id,since,until)
    if data.get("erro"):
        st.error(f"Erro Meta API: {data['erro']}"); return

    raw=data["ads"]
    if raw:
        df=pd.DataFrame(raw); df["spend"]=df["spend"].astype(float)
        df=df.sort_values("spend",ascending=False).head(20)
        ads=df.to_dict(orient="records")
    else: ads=[]

    agg=data.get("agg",{})
    if not ads:
        st.markdown(f'<div class="glass-card" style="text-align:center;padding:40px;"><p style="color:#6b7280;font-size:1.5rem;"><i class="bi bi-megaphone"></i></p><h3 style="color:#FAFAFA;font-size:1rem;">Nenhum criativo com gasto em {mes}</h3></div>', unsafe_allow_html=True)
        return

    _render_macro_cards(agg)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    _render_diagnostico(agg, mes)
    _render_top_performers(ads)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    _render_ad_cards(ads, agg)
