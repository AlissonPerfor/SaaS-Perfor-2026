"""
modules/report_generator.py
Módulo 'Reports Automatizados' do dashboard Perfor.IA.
Gera o texto de Feedback de Resultados para fácil cópia.
"""

import calendar
from datetime import date
from typing import Optional

import streamlit as st

from core.context import get_active_project, render_cargo_badge
from core.sheets import MESES_ABREV, get_gps_data, fmt_pct

def format_money_full(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def render_report() -> None:
    render_cargo_badge(
        "✦ Reports",
        "Geração automática de Feedback de Resultados"
    )

    projeto = get_active_project()
    if not projeto:
        st.warning("Selecione um projeto na sidebar para gerar o relatório.")
        return

    sheet_id: Optional[str] = projeto.get("google_sheet_id")
    if not sheet_id:
        st.error("google_sheet_id não cadastrado para este projeto.")
        return

    # Seletor de mês
    hoje = date.today()
    mes_padrao_idx = hoje.month - 1
    if hoje.day <= 5 and hoje.month > 1:
        mes_padrao_idx = hoje.month - 2

    _, _, col_mes = st.columns([2, 2, 1])
    with col_mes:
        mes_sel = st.selectbox(
            "Mês",
            options=MESES_ABREV,
            index=mes_padrao_idx,
            key="sel_mes_report",
        )

    with st.spinner(f"Gerando relatório de {projeto.get('nome_cliente') or projeto.get('nome', '')}..."):
        dados = get_gps_data(sheet_id=sheet_id, mes_abrev=mes_sel)

    if dados.get("erro"):
        st.error(dados["erro"])
        return

    # Extraindo dados
    real = dados["realizado"]
    proj = dados["projetado"]
    pacing_mes = dados.get("pacing_mes", 0.0)

    # 1. Datas
    mes_num = MESES_ABREV.index(mes_sel) + 1
    ano_atual = hoje.year
    total_dias = calendar.monthrange(ano_atual, mes_num)[1]
    
    if hoje.month == mes_num and hoje.year == ano_atual:
        dia_atual = hoje.day
    elif (ano_atual, mes_num) < (hoje.year, hoje.month):
        dia_atual = total_dias
    else:
        dia_atual = 1

    data_inicio_str = f"01/{mes_num:02d}"
    data_fim_str = f"{dia_atual:02d}/{mes_num:02d}"
    pacing_pct_str = f"{pacing_mes * 100:.0f}%"

    # 2. Desempenho de Vendas
    inv_total = format_money_full(real.get("Investimento Total"))
    rec_cap = format_money_full(real.get("Receita Captada"))
    rec_fat = format_money_full(real.get("Receita Faturada"))
    pct_pag = fmt_pct(real.get("% de Pagamento"))
    
    ped_pagos_val = real.get("Pedidos Pagos")
    ped_pagos = f"{int(ped_pagos_val)}" if ped_pagos_val is not None else "—"
    
    roas_val = real.get("ROAS Pago")
    roas = f"{roas_val:.2f}x".replace(".", ",") if roas_val is not None else "—"

    # 3. Desempenho de Receita e Investimento
    rec_real = real.get("Receita Faturada")
    rec_proj = proj.get("Receita Faturada")
    inv_real = real.get("Investimento Total")
    inv_proj = proj.get("Investimento Total")

    ating_rec = (rec_real / rec_proj) if (rec_real is not None and rec_proj and rec_proj > 0) else 0
    ating_inv = (inv_real / inv_proj) if (inv_real is not None and inv_proj and inv_proj > 0) else 0

    ating_rec_str = f"{ating_rec * 100:.2f}%".replace(".", ",")
    ating_inv_str = f"{ating_inv * 100:.2f}%".replace(".", ",")

    status_rec = "abaixo do previsto"
    if ating_rec >= pacing_mes:
        status_rec = "acima do previsto"
    elif abs(ating_rec - pacing_mes) < 0.05:
        status_rec = "dentro do previsto"

    status_inv = "abaixo do esperado"
    if ating_inv > pacing_mes + 0.05:
        status_inv = "acima do esperado"
    elif ating_inv >= pacing_mes - 0.05:
        status_inv = "dentro do esperado"

    projecao_fechamento = (rec_real / pacing_mes) if (rec_real is not None and pacing_mes > 0) else 0
    proj_fech_str = f"R$ {projecao_fechamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # 4. Performance das KPI
    def get_kpi_delta(metrica, invert=False):
        v_real = real.get(metrica)
        v_meta = proj.get(metrica)
        
        v_real_str = "—"
        v_meta_str = "—"
        delta_str = ""
        emoji = ""

        if metrica == "Taxa de Conversão":
            v_real_str = fmt_pct(v_real)
            v_meta_str = fmt_pct(v_meta)
        else:
            # Ticket and CPS
            v_real_str = format_money_full(v_real)
            v_meta_str = format_money_full(v_meta)

        if v_real is not None and v_meta is not None and v_meta > 0:
            diff = v_real - v_meta
            pct = (diff / v_meta) * 100

            if invert: # lower is better (CPS)
                is_good = diff <= 0
            else: # higher is better (Ticket, CVR)
                is_good = diff >= 0

            emoji = "✅" if is_good else "❌"
            sinal = "+" if pct > 0 else ""
            delta_str = f" ({sinal}{pct:.2f}%)".replace(".", ",")

        return v_real_str, v_meta_str, delta_str, emoji

    cps_real, cps_meta, cps_delta, cps_emj = get_kpi_delta("Custo por Sessão", invert=True)
    cvr_real, cvr_meta, cvr_delta, cvr_emj = get_kpi_delta("Taxa de Conversão", invert=False)
    tmd_real, tmd_meta, tmd_delta, tmd_emj = get_kpi_delta("Ticket Médio", invert=False)

    report_text = f'''*Feedback de Resultados* 📊
{data_inicio_str} até {data_fim_str} · (Dia {dia_atual}/{total_dias} - {pacing_pct_str} do mês)

💰 *Desempenho de Vendas*

➡️ Investimento Total: *{inv_total}*
➡️ Receita Captada: *{rec_cap}*
➡️ Receita Faturada: *{rec_fat}*
➡️ % de Pagamento: *{pct_pag}*
➡️ Pedidos Pagos: *{ped_pagos}*
➡️ ROAS: *{roas}*

🎯 *Desempenho de Receita e Investimento:*

• Receita: Até o momento *alcançamos {ating_rec_str} da nossa meta* de receita mensal, o que está *{status_rec}* para a data atual; conforme nossos resultados até o momento a projeção para fecharmos o mês está em {proj_fech_str}.

• Investimento: Nosso investimento atual corresponde a {ating_inv_str} do orçamento total previsto, {status_inv}.

🔑 *Performance das KPI*

➡️ Custo por Sessão: *{cps_real}* | Meta: *{cps_meta}*{cps_delta} {cps_emj}
➡️ Taxa de Conversão: *{cvr_real}* | Meta: *{cvr_meta}*{cvr_delta} {cvr_emj}
➡️ Ticket Médio: *{tmd_real}* | Meta: *{tmd_meta}*{tmd_delta} {tmd_emj}

📝 Análise de Cenário e Próximos Passos:
'''

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card" style="padding: 24px;">
        <h4 style="color:#FAFAFA; margin-top:0;">Relatório Gerado</h4>
        <p style="color:#9CA3AF; font-size:0.85rem; margin-bottom: 16px;">
            Copie o texto abaixo clicando no ícone no canto superior direito do quadro.
        </p>
    """, unsafe_allow_html=True)
    
    st.code(report_text, language="markdown")
    
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados Manualmente", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
