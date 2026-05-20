"""
modules/squad_dashboard.py
Dashboard do Squad — visão de performance de todos os clientes.
Mostra Receita, Investimento e ROAS com: Realizado | Atingimento | Projeção
Com colorização Verde/Amarelo/Vermelho e análise de IA.
"""

import calendar
import re
import textwrap
from datetime import date
from typing import Optional

import streamlit as st

from core.context import (
    get_projects_by_squad,
    get_all_projects,
    get_user_cargo,
    get_project_display_name,
    navigate_to_project,
    is_ceo,
)
from core.sheets import get_gps_data, fmt_brl, fmt_roas, MESES_ABREV


# ── Helpers de colorização ─────────────────────────────────────────────────────


def _clean_html(html_str: str) -> str:
    cleaned = re.sub(r'^[ 	]+', '', html_str, flags=re.MULTILINE)
    return cleaned.replace('
', ' ')

def _status_color(atingimento: Optional[float]) -> dict:
    """
    Retorna dict com cor, bg e label de status baseado no atingimento.
    Verde: >= 1.0 | Amarelo: >= 0.90 | Vermelho: < 0.90
    """
    if atingimento is None:
        return {"color": "#6b7280", "bg": "rgba(107,114,128,0.10)", "border": "rgba(107,114,128,0.25)", "label": "—", "icon": "bi-dash-circle"}
    if atingimento >= 1.0:
        return {"color": "#00d592", "bg": "rgba(0,213,146,0.10)", "border": "rgba(0,213,146,0.30)", "label": "✓ Meta", "icon": "bi-check-circle-fill"}
    if atingimento >= 0.90:
        return {"color": "#F59E0B", "bg": "rgba(245,158,11,0.10)", "border": "rgba(245,158,11,0.30)", "label": "⚠ Atenção", "icon": "bi-exclamation-circle-fill"}
    return {"color": "#EF4444", "bg": "rgba(239,68,68,0.10)", "border": "rgba(239,68,68,0.30)", "label": "✗ Abaixo", "icon": "bi-x-circle-fill"}


def _calc_projecao_fim_mes(realizado: Optional[float], pacing: float) -> Optional[float]:
    """Projeta o valor de fechamento do mês: realizado / pacing."""
    if realizado is None or pacing <= 0:
        return None
    return realizado / pacing


def _calc_investimento_diario_necessario(
    meta: Optional[float],
    realizado: Optional[float],
    mes_num: int,
    ano: int,
) -> Optional[float]:
    """
    Calcula o investimento diário necessário para atingir a meta até o fim do mês.
    = (meta - realizado) / dias_restantes
    """
    if meta is None or realizado is None:
        return None
    hoje = date.today()
    total_dias = calendar.monthrange(ano, mes_num)[1]
    dias_restantes = total_dias - hoje.day
    if dias_restantes <= 0:
        return None
    faltante = meta - realizado
    if faltante <= 0:
        return 0.0
    return faltante / dias_restantes


# ── Função pública principal ───────────────────────────────────────────────────

def render_squad_dashboard(squad_name: Optional[str] = None) -> None:
    """Renderiza o dashboard de performance do squad."""
    if squad_name:
        projetos = get_projects_by_squad(squad_name)
        titulo = f"Squad {squad_name}"
    else:
        projetos = get_all_projects()
        titulo = "Visão Geral da Agência"

    # Seletor de mês
    hoje = date.today()
    mes_padrao_idx = hoje.month - 1
    if hoje.day <= 5 and hoje.month > 1:
        mes_padrao_idx = hoje.month - 2

    col_title, col_mes = st.columns([4, 1])
    with col_title:
        st.markdown(_clean_html(f"""
        <div style="margin-bottom:8px;">
            <h1 style="font-size:1.8rem; font-weight:700; color:#FAFAFA; margin:0 0 4px 0; letter-spacing:-0.5px;">
                {titulo}
            </h1>
            <p style="color:#4b5563; font-size:0.88rem; margin:0;">
                Performance consolidada · {len(projetos)} cliente(s) ativo(s)
            </p>
        </div>
        """), unsafe_allow_html=True)

    with col_mes:
        mes_sel = st.selectbox(
            "Mês",
            options=MESES_ABREV,
            index=mes_padrao_idx,
            key="sel_mes_squad_dash",
            label_visibility="collapsed",
        )

    st.markdown('<hr style="border:none; border-top:1px solid #1f2937; margin:12px 0 24px 0;">', unsafe_allow_html=True)

    if not projetos:
        st.markdown(_clean_html("""
        <div class="glass-card" style="text-align:center; padding:48px 32px;">
            <div style="font-size:2.5rem; margin-bottom:16px; color:#6b7280;"><i class="bi bi-inbox"></i></div>
            <h3 style="color:#FAFAFA; margin:0 0 8px 0;">Nenhum cliente encontrado</h3>
        </div>
        """), unsafe_allow_html=True)
        return

    # Coleta dados de todos os projetos
    try:
        mes_num = MESES_ABREV.index(mes_sel) + 1
    except ValueError:
        mes_num = hoje.month
    ano = hoje.year

    clientes_data = []
    with st.spinner(f"Carregando performance de {len(projetos)} cliente(s)..."):
        for p in projetos:
            nome = get_project_display_name(p)
            sheet_id = p.get("google_sheet_id")
            if not sheet_id:
                clientes_data.append({"projeto": p, "nome": nome, "dados": None, "sem_config": True})
                continue
            dados = get_gps_data(sheet_id=sheet_id, mes_abrev=mes_sel)
            clientes_data.append({
                "projeto": p,
                "nome": nome,
                "dados": dados if not dados.get("erro") else None,
                "sem_config": bool(dados.get("erro")),
            })

    # ── Análise de IA ──────────────────────────────────────────────────────────
    _render_ai_insights(clientes_data, mes_sel)

    # ── Tabela de Performance ──────────────────────────────────────────────────
    st.markdown(_clean_html("""
    <p style="color:#4b5563; font-size:0.68rem; letter-spacing:1.5px; margin-bottom:12px;">
        <i class="bi bi-bar-chart-fill" style="margin-right:4px;"></i> PERFORMANCE DOS CLIENTES
    </p>
    """), unsafe_allow_html=True)

    for item in clientes_data:
        _render_client_performance_card(item, mes_num, ano, mes_sel)


# ── Card de Performance por Cliente ───────────────────────────────────────────

def _render_client_performance_card(item: dict, mes_num: int, ano: int, mes_sel: str) -> None:
    """Renderiza o card completo de performance de um cliente."""
    nome = item["nome"]
    projeto = item["projeto"]
    dados = item["dados"]
    inicial = nome[0].upper() if nome else "?"

    # Sem configuração
    if item["sem_config"] or dados is None:
        st.markdown(_clean_html(f"""
        <div class="glass-card" style="padding:16px 20px; border-color:rgba(251,191,36,0.25); margin-bottom:2px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:40px; height:40px; border-radius:10px; background:rgba(251,191,36,0.08);
                    border:1px solid rgba(251,191,36,0.25); display:flex; align-items:center; justify-content:center;
                    font-weight:700; color:#FCD34D; font-size:1rem; flex-shrink:0;">{inicial}</div>
                <div>
                    <p style="font-size:0.95rem; font-weight:600; color:#FAFAFA; margin:0 0 2px 0;">{nome}</p>
                    <span style="background:rgba(251,191,36,0.12); color:#FCD34D; border:1px solid rgba(251,191,36,0.3);
                        border-radius:12px; padding:2px 8px; font-size:0.65rem;">GPS não configurado</span>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)
        if st.button(f"Abrir {nome}", key=f"open_noconfig_{projeto.get('id', nome)}", use_container_width=True, type="secondary"):
            navigate_to_project(projeto)
        return

    # Extrai métricas
    pacing = dados.get("pacing_mes", 0.0)
    r_real = dados["realizado"].get("Receita Faturada")
    r_proj = dados["projetado"].get("Receita Faturada")
    i_real = dados["realizado"].get("Investimento Total")
    i_proj = dados["projetado"].get("Investimento Total")

    # ROAS calculado
    roas_real = (r_real / i_real) if (r_real and i_real and i_real > 0) else dados["realizado"].get("ROAS Pago")
    roas_proj = (r_proj / i_proj) if (r_proj and i_proj and i_proj > 0) else dados["projetado"].get("ROAS Pago")

    # Atingimentos
    ating_receita = (r_real / r_proj) if (r_real is not None and r_proj and r_proj > 0) else None
    ating_invest  = (i_real / i_proj) if (i_real is not None and i_proj and i_proj > 0) else None
    ating_roas    = (roas_real / roas_proj) if (roas_real is not None and roas_proj and roas_proj > 0) else None

    # Projeções de fechamento
    proj_receita = _calc_projecao_fim_mes(r_real, pacing)
    proj_invest  = _calc_projecao_fim_mes(i_real, pacing)
    proj_roas_val = (proj_receita / proj_invest) if (proj_receita and proj_invest and proj_invest > 0) else None

    # Investimento diário necessário
    inv_diario_nec = _calc_investimento_diario_necessario(i_proj, i_real, mes_num, ano)

    # Status geral (pior dos 3)
    statuses = [ating_receita, ating_roas]
    worst = min((s for s in statuses if s is not None), default=None)
    card_status = _status_color(worst)

    st.markdown(_clean_html(f"""
    <div class="glass-card" style="padding:20px 24px; border-color:{card_status['border']}; 
         background:linear-gradient(135deg, {card_status['bg']} 0%, rgba(12,12,12,0.70) 100%); margin-bottom:2px;">

        <!-- Header do cliente -->
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:42px; height:42px; border-radius:10px; background:{card_status['bg']};
                    border:1px solid {card_status['border']}; display:flex; align-items:center; justify-content:center;
                    font-weight:700; color:{card_status['color']}; font-size:1.1rem; flex-shrink:0;">{inicial}</div>
                <div>
                    <p style="font-size:1rem; font-weight:700; color:#FAFAFA; margin:0 0 2px 0;">{nome}</p>
                    <span style="background:{card_status['bg']}; color:{card_status['color']};
                        border:1px solid {card_status['border']}; border-radius:12px;
                        padding:2px 10px; font-size:0.65rem; font-weight:600;">{card_status['label']}</span>
                </div>
            </div>
            <div style="text-align:right;">
                <p style="color:#4b5563; font-size:0.62rem; letter-spacing:1px; margin:0 0 2px 0;">PACING DO MÊS</p>
                <p style="font-size:1.1rem; font-weight:700; color:#9CA3AF; margin:0;">{pacing*100:.0f}%</p>
            </div>
        </div>

        <!-- Grid de métricas -->
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;">
            {_metric_block("Receita", r_real, r_proj, ating_receita, proj_receita, "brl")}
            {_metric_block_invest("Investimento", i_real, i_proj, ating_invest, proj_invest, inv_diario_nec, mes_num, ano)}
            {_metric_block("ROAS", roas_real, roas_proj, ating_roas, proj_roas_val, "roas")}
        </div>
    </div>
    """), unsafe_allow_html=True)

    if st.button(f"Abrir {nome}", key=f"open_perf_{projeto.get('id', nome)}", use_container_width=True, type="secondary"):
        navigate_to_project(projeto)


def _fmt(value: Optional[float], tipo: str) -> str:
    if value is None:
        return "—"
    if tipo == "brl":
        return fmt_brl(value)
    if tipo == "roas":
        return fmt_roas(value)
    return str(value)


def _metric_block(label: str, real: Optional[float], meta: Optional[float],
                  ating: Optional[float], proj: Optional[float], tipo: str) -> str:
    """Gera HTML de um bloco de métrica (Receita ou ROAS)."""
    st_color = _status_color(ating)
    ating_pct = f"{ating*100:.1f}%".replace(".", ",") if ating is not None else "—"
    real_fmt = _fmt(real, tipo)
    meta_fmt = _fmt(meta, tipo)
    proj_fmt = _fmt(proj, tipo)
    color = st_color["color"]

    return _clean_html(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
         border-radius:10px; padding:14px 16px;">
        <p style="color:#6b7280; font-size:0.62rem; letter-spacing:1.2px; margin:0 0 10px 0; font-weight:600;">{label.upper()}</p>
        <p style="font-size:1.4rem; font-weight:700; color:#FAFAFA; margin:0 0 4px 0; letter-spacing:-0.5px;">{real_fmt}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="color:#4b5563; font-size:0.68rem;">Meta: <span style="color:#9CA3AF;">{meta_fmt}</span></span>
            <span style="color:{color}; font-size:0.75rem; font-weight:700;">{ating_pct}</span>
        </div>
        <div style="background:rgba(255,255,255,0.05); border-radius:999px; height:4px; width:100%; margin-bottom:8px; overflow:hidden;">
            <div style="height:100%; width:{min((ating or 0)*100, 100):.1f}%; background:{color}; border-radius:999px;"></div>
        </div>
        <p style="color:#4b5563; font-size:0.65rem; margin:0;">Proj: <span style="color:#9CA3AF;">{proj_fmt}</span></p>
    </div>
    """)


def _metric_block_invest(label: str, real: Optional[float], meta: Optional[float],
                          ating: Optional[float], proj: Optional[float],
                          inv_diario: Optional[float], mes_num: int, ano: int) -> str:
    """Bloco de Investimento com alerta de investimento diário necessário."""
    st_color = _status_color(ating)
    ating_pct = f"{ating*100:.1f}%".replace(".", ",") if ating is not None else "—"
    real_fmt = _fmt(real, "brl")
    meta_fmt = _fmt(meta, "brl")
    proj_fmt = _fmt(proj, "brl")
    color = st_color["color"]

    # Alerta de inv. diário
    diario_html = ""
    if inv_diario is not None and inv_diario > 0:
        diario_fmt = fmt_brl(inv_diario)
        diario_html = f"""
        <div style="margin-top:8px; background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25);
             border-radius:6px; padding:6px 8px;">
            <p style="color:#F59E0B; font-size:0.62rem; margin:0; line-height:1.4;">
                <i class="bi bi-lightning-charge-fill"></i> Ajuste para <strong>{diario_fmt}/dia</strong> para fechar na meta
            </p>
        </div>
        """
    elif inv_diario == 0.0:
        diario_html = """
        <div style="margin-top:8px; background:rgba(0,213,146,0.08); border:1px solid rgba(0,213,146,0.25);
             border-radius:6px; padding:6px 8px;">
            <p style="color:#00d592; font-size:0.62rem; margin:0;">
                <i class="bi bi-check-circle-fill"></i> Meta de investimento atingida
            </p>
        </div>
        """

    return _clean_html(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
         border-radius:10px; padding:14px 16px;">
        <p style="color:#6b7280; font-size:0.62rem; letter-spacing:1.2px; margin:0 0 10px 0; font-weight:600;">{label.upper()}</p>
        <p style="font-size:1.4rem; font-weight:700; color:#FAFAFA; margin:0 0 4px 0; letter-spacing:-0.5px;">{real_fmt}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="color:#4b5563; font-size:0.68rem;">Meta: <span style="color:#9CA3AF;">{meta_fmt}</span></span>
            <span style="color:{color}; font-size:0.75rem; font-weight:700;">{ating_pct}</span>
        </div>
        <div style="background:rgba(255,255,255,0.05); border-radius:999px; height:4px; width:100%; margin-bottom:8px; overflow:hidden;">
            <div style="height:100%; width:{min((ating or 0)*100, 100):.1f}%; background:{color}; border-radius:999px;"></div>
        </div>
        <p style="color:#4b5563; font-size:0.65rem; margin:0;">Proj: <span style="color:#9CA3AF;">{proj_fmt}</span></p>
        {diario_html}
    </div>
    """)


# ── Análise de IA ──────────────────────────────────────────────────────────────

def _render_ai_insights(clientes_data: list[dict], mes_sel: str) -> None:
    """Renderiza o painel de análise de IA com insights sobre o squad."""
    criticos = []
    atencao = []
    ok = []

    for item in clientes_data:
        nome = item["nome"]
        dados = item["dados"]
        if dados is None:
            continue

        pacing = dados.get("pacing_mes", 0.0)
        r_real = dados["realizado"].get("Receita Faturada")
        r_proj = dados["projetado"].get("Receita Faturada")
        i_real = dados["realizado"].get("Investimento Total")
        i_proj = dados["projetado"].get("Investimento Total")

        ating_r = (r_real / r_proj) if (r_real is not None and r_proj and r_proj > 0) else None
        ating_i = (i_real / i_proj) if (i_real is not None and i_proj and i_proj > 0) else None

        # Classifica pelo atingimento de receita (principal KPI)
        if ating_r is not None:
            if ating_r < 0.90:
                deficit_pct = (1 - ating_r) * 100
                criticos.append({"nome": nome, "ating": ating_r, "deficit": deficit_pct, "ating_i": ating_i})
            elif ating_r < 1.0:
                criticos_temp = (1 - ating_r) * 100
                atencao.append({"nome": nome, "ating": ating_r, "deficit": criticos_temp})
            else:
                ok.append(nome)

    # Gera o texto de insight
    insights_html = _build_ai_text(criticos, atencao, ok, mes_sel)

    st.markdown(_clean_html(f"""
    <div style="background:linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(12,12,12,0.80) 100%);
         border:1px solid rgba(139,92,246,0.25); border-radius:14px; padding:20px 24px; margin-bottom:24px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <span style="font-size:1.2rem; color:#8B5CF6;"><i class="bi bi-stars"></i></span>
            <p style="color:#8B5CF6; font-size:0.72rem; letter-spacing:1.5px; font-weight:600; margin:0;">ANÁLISE DE INTELIGÊNCIA — {mes_sel.upper()}</p>
        </div>
        <div style="color:#D1D5DB; font-size:0.88rem; line-height:1.7;">
            {insights_html}
        </div>
    </div>
    """), unsafe_allow_html=True)


def _build_ai_text(criticos: list, atencao: list, ok: list, mes_sel: str) -> str:
    """Constrói o texto de análise de IA baseado nos dados."""
    parts = []

    total_analisados = len(criticos) + len(atencao) + len(ok)
    if total_analisados == 0:
        return "<em>Nenhum dado GPS disponível para análise neste mês.</em>"

    # Clientes críticos
    if criticos:
        nomes_crit = ", ".join(f"<strong style='color:#EF4444;'>{c['nome']}</strong>" for c in criticos)
        partes_crit = []
        for c in criticos:
            deficit = c["deficit"]
            ating_i = c.get("ating_i")
            acoes = []
            if ating_i is not None and ating_i < 0.85:
                acoes.append("aumente o investimento diário")
            else:
                acoes.append("revise criativos e segmentação")
            partes_crit.append(f"<strong>{c['nome']}</strong> ({deficit:.0f}% abaixo — {acoes[0]})")
        texto_crit = "; ".join(partes_crit)
        parts.append(
            f"🔴 <strong style='color:#EF4444;'>Prioridade Máxima:</strong> {nomes_crit} estão mais de 10% abaixo da meta de receita "
            f"em {mes_sel} e precisam de ação imediata. Recomendações: {texto_crit}."
        )

    # Clientes em atenção
    if atencao:
        nomes_at = ", ".join(f"<strong style='color:#F59E0B;'>{a['nome']}</strong>" for a in atencao)
        parts.append(
            f"🟡 <strong style='color:#F59E0B;'>Atenção:</strong> {nomes_at} estão até 10% abaixo da meta. "
            f"Monitore o pacing diário e ajuste o investimento se necessário nos próximos dias."
        )

    # Clientes saudáveis
    if ok:
        nomes_ok = ", ".join(f"<strong style='color:#00d592;'>{n}</strong>" for n in ok)
        parts.append(
            f"🟢 <strong style='color:#00d592;'>No caminho certo:</strong> {nomes_ok} {'está' if len(ok)==1 else 'estão'} "
            f"acima da meta. Mantenha a estratégia atual e explore oportunidades de escala."
        )

    if not parts:
        return f"<em>Todos os {total_analisados} clientes analisados ainda não possuem dados suficientes para classificação.</em>"

    return "<br><br>".join(parts)
