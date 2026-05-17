# 📊 Planejamento Anual com IA — Guia de Inteligência
> Imersão EDP · Bloco 2 · Documento de Referência do Aluno

---

## ⚡ A Verdade que muda tudo

> **Receita não se planeja. Se calcula.**
> O que você planeja são os **9 drivers** que a produzem.

A maioria dos e-commerces define meta de receita e torce. Quem domina esse sistema define os drivers mês a mês e deixa a receita ser consequência matemática — não chute.

---

## 🧠 MÉTODO: Key vs. Driver

Toda métrica do seu e-commerce é **KEY** (resultado) ou **DRIVER** (alavanca). A diferença muda tudo.

| Tipo | O que é | Exemplos | Sua relação |
|---|---|---|---|
| **KEY** | Resultado. Você acompanha. | Receita Captada, Pedidos Faturados, ROAS, CAC | → Você **ACOMPANHA** |
| **DRIVER** | Alavanca. Você controla. | % Retenção, Ticket Médio, CPS Mídia, Conversão | → Você **PLANEJA** |

**O erro mais comum:** definir meta de receita (KEY) sem definir os drivers que a produzem.
**O resultado:** meta no papel, improviso na prática.

---

## 🎛️ OS 9 DRIVERS — O que cada um é e como usar

### RECEITA

#### 1 · % Retenção
- **O que é:** percentual dos pedidos que vêm de clientes que já compraram antes
- **O que move:** CRM ativo, e-mail marketing, grupos VIP, cadência de recompra, experiência pós-venda
- **Impacto:** cada +5% de retenção pode representar +25% de receita sem novo investimento
- **Faixa saudável:** 10% a 38% — acima de 38% sinaliza falha na aquisição
- **Variação máxima segura:** ±2 pp/mês

#### 2 · % Aprovação de Receita
- **O que é:** % dos pedidos captados que efetivamente viram receita faturada (aprovação do pagamento)
- **O que move:** meios de pagamento, anti-fraude calibrado, recuperação de boleto, retry de cartão
- **Impacto:** 90% vs 85% de aprovação = +5,9% de receita sem um real a mais de investimento
- **Faixa saudável:** 70% a 98% — alvo ideal: ~90%
- **Variação máxima segura:** ±1 pp/mês

---

### PEDIDOS

#### 3 · Ticket Médio (R$)
- **O que é:** valor médio de cada pedido
- **O que move:** upsell, cross-sell, kits, frete grátis progressivo, pricing estratégico
- **Impacto:** +R$20 no ticket com o mesmo volume = +8% de receita sem investimento adicional
- **Faixa saudável:** R$50 a R$2.000 — crescimento anual saudável: 5% a 7%
- **Variação máxima segura:** 2%/mês

#### 4 · Taxa de Conversão (%)
- **O que é:** % de sessões que viram pedido
- **O que move:** CRO da loja, velocidade da página, prova social, checkout otimizado, ofertas
- **Impacto:** 1% → 2% de conversão = 100% mais receita com o mesmo tráfego
- **Faixa saudável:** 0,3% a 5%
- **Variação máxima segura:** ±0,25 pp/mês

---

### INVESTIMENTO

#### 5 · Investimento em Mídia Paga (R$)
- **O que é:** investimento em Meta Ads, Google Ads, TikTok Ads etc.
- **O que move:** volume de sessões pagas, CAC, ROAS
- **Crescimento mensal saudável:** 10% a 15% — nunca dissociado da receita gerada

#### 6 · Investimento em Grupos VIP (R$)
- **O que é:** investimento em WhatsApp, Telegram, grupos de recompra
- **O que move:** % Retenção, LTV, recompra orgânica
- **Por que importa:** a alavanca de retenção mais eficiente e barata do e-commerce

#### 7 · Investimento em Impulsionamento (R$)
- **O que é:** boost de conteúdo orgânico nas redes sociais
- **O que move:** alcance, engajamento, prova social
- **Regra:** use onde o orgânico já performa — não para salvar conteúdo fraco

---

### TRÁFEGO

#### 8 · Sessões Orgânicas (Nº)
- **O que é:** visitas sem custo direto de mídia (SEO, social orgânico, e-mail, direto, grupos)
- **O que move:** SEO, conteúdo, e-mail marketing, grupos VIP, tráfego de marca
- **Crescimento mensal saudável:** 5% a 7% — o % orgânico deve crescer mês a mês

#### 9 · CPS Mídia — Custo por Sessão (R$)
- **O que é:** quanto você paga por cada visita vinda dos anúncios
- **O que move:** qualidade dos criativos, relevância, segmentação, score das contas
- **Impacto:** CPS subindo silenciosamente = receita caindo sem você saber o porquê
- **Faixa saudável:** R$0,10 a R$5,00 — teto ideal: R$1,20
- **Variação máxima segura:** ±R$0,10/mês

---

## ⚙️ LÓGICA: A Cascata de Cálculo Completa

Com os 9 drivers definidos, **todas as métricas são calculadas automaticamente** nesta ordem:

```
PASSO 1 — TRÁFEGO E INVESTIMENTO
──────────────────────────────────────────────────────────────
Invest. Total    = Mídia Paga + Grupos VIP + Impulsionamento
Sessões Mídia    = Invest. Mídia Paga ÷ CPS Mídia
Sessões Totais   = Sessões Mídia + Sessões Orgânicas
% Sessões Mídia  = (Sessões Mídia ÷ Sessões Totais) × 100
CPS Geral        = Invest. Total ÷ Sessões Totais

PASSO 2 — PEDIDOS
──────────────────────────────────────────────────────────────
Pedidos Captados   = INT(Sessões Totais × Taxa Conversão ÷ 100)
Pedidos Aquisição  = INT(Captados × (1 - % Retenção ÷ 100))
Pedidos Retenção   = INT(Captados × % Retenção ÷ 100)
Pedidos Faturados  = INT(Captados × % Aprovação ÷ 100)

PASSO 3 — RECEITA
──────────────────────────────────────────────────────────────
Receita Captada    = Pedidos Captados × Ticket Médio
Receita Aquisição  = Pedidos Aquisição × Ticket Médio
Receita Retenção   = Pedidos Retenção × Ticket Médio
Receita Faturada   = Receita Captada × % Aprovação ÷ 100
Receita Cancelada  = Receita Captada - Receita Faturada

PASSO 4 — EFICIÊNCIA
──────────────────────────────────────────────────────────────
CAC              = Invest. Total ÷ Pedidos Aquisição
CPA Real         = Invest. Total ÷ Pedidos Faturados
ROAS Captado     = Receita Captada ÷ Invest. Total
ROAS Faturado    = Receita Faturada ÷ Invest. Total
AdCost (%)       = (Invest. Total ÷ Receita Faturada) × 100
Peso/Mês (%)     = (Receita Captada do Mês ÷ Receita Captada Anual) × 100

PASSO 5 — COMPARATIVOS
──────────────────────────────────────────────────────────────
MoM (%)  = ((Receita Mês - Receita Mês Anterior) ÷ Receita Mês Anterior) × 100
YoY (%)  = ((Receita Mês - Receita Mesmo Mês Ano Ant.) ÷ Mesmo Mês Ano Ant.) × 100
```

---

## 🚨 Faixas de Saúde dos Drivers

| Driver | 🔴 Alerta | ✅ Saudável | 🎯 Alvo e Limite Mensal |
|---|---|---|---|
| % Retenção | < 10% ou > 60% | 10% – 38% | Crescer até 38%, máx. ±2 pp/mês |
| % Aprovação | < 70% | 70% – 98% | Alvo ~90%, máx. ±1 pp/mês |
| Ticket Médio | < R$50 | Crescendo 5–7%/ano | Máx. +2%/mês |
| Taxa de Conversão | < 0,3% ou > 5% | Crescimento progressivo | Máx. ±0,25 pp/mês |
| CPS Mídia | > R$5,00 | < R$1,20 | Reduzir se > R$1,20, máx. R$0,10/mês |

### Como classificar o planejamento

| Tipo | Sinal |
|---|---|
| **Conservador** | Drivers abaixo das médias históricas |
| **Equilibrado** | Drivers próximos da realidade com crescimento consistente |
| **Agressivo** | Drivers acima dos limites saudáveis sem base histórica para sustentar |

---

## 📊 BENCHMARKS DE MERCADO POR NICHO

Use como referência para validar se seus drivers estão saudáveis em comparação ao mercado.

| Nicho | Ticket Médio | Conversão | % Retenção | CPS Mídia | ROAS típico |
|-------|-------------|-----------|------------|-----------|-------------|
| **Moda Feminina** | R$ 150–280 | 1,2%–2,5% | 25%–40% | R$ 0,80–1,50 | 3–5x |
| **Moda Masculina** | R$ 180–350 | 1,0%–2,0% | 20%–35% | R$ 0,90–1,80 | 3–4x |
| **Beleza/Skincare** | R$ 120–250 | 1,5%–3,0% | 30%–45% | R$ 0,70–1,40 | 4–6x |
| **Suplementos** | R$ 180–400 | 2,0%–3,5% | 40%–60% | R$ 0,80–1,60 | 4–7x |
| **Pet Shop** | R$ 200–450 | 2,0%–3,0% | 45%–65% | R$ 0,60–1,30 | 4–6x |
| **Casa e Decoração** | R$ 200–600 | 0,8%–1,8% | 15%–25% | R$ 1,00–2,00 | 2,5–4x |
| **Eletrônicos** | R$ 300–1500 | 0,8%–1,5% | 10%–20% | R$ 1,20–2,50 | 2,5–3,5x |
| **Joias/Acessórios** | R$ 250–800 | 1,0%–2,0% | 15%–30% | R$ 1,00–2,00 | 3–5x |
| **Infantil** | R$ 150–300 | 1,5%–2,8% | 35%–55% | R$ 0,80–1,50 | 3,5–5x |
| **Saúde/Bem-estar** | R$ 180–400 | 1,8%–3,0% | 35%–55% | R$ 0,90–1,70 | 4–6x |

> **Atenção:** benchmarks são referência, não meta. Compare com seu próprio histórico antes de mudar drivers.

---

## 📅 CALENDÁRIO ANUAL DE PLANEJAMENTO

Quando rodar cada tipo de planejamento ao longo do ano:

| Período | Atividade | Output esperado |
|---------|-----------|-----------------|
| **Out–Nov (ano anterior)** | Construção do planejamento anual | Plano completo com 9 drivers projetados |
| **Dez** | Validação final + sazonalidade Black Friday/Natal | Ajuste de fechamento de ano |
| **1º dia útil de cada mês** | Revisão mensal (planejado vs. realizado) | Recalibração dos meses restantes |
| **Mid-quarter (Mar/Jun/Set)** | Revisão trimestral profunda | Diagnóstico de tendência + ajustes táticos |
| **Pré-data forte (D-30)** | Simulação de cenários para a data | Plano de ação para Mães, BF, Natal |
| **Pós-data forte (D+15)** | Análise de impacto na cascata | Reset dos drivers para o novo baseline |
| **Jul** | Revisão de meio de ano | Replanejamento do 2º semestre |

### Datas Comerciais Brasileiras (Calendário Oficial)

| Mês | Data forte | Impacto típico no Ticket | Aumento de tráfego |
|-----|-----------|--------------------------|---------------------|
| **Jan** | Volta às aulas | Médio | +15–25% |
| **Fev** | Carnaval (queda) | Baixo | −10–20% |
| **Mar** | Dia da Mulher · Consumidor | Médio-Alto | +20–35% |
| **Mai** | Dia das Mães | **Alto** | +40–60% |
| **Jun** | Namorados · Festa Junina | Alto | +30–45% |
| **Ago** | Dia dos Pais | Alto | +30–45% |
| **Set** | Primavera (moda/beleza) | Médio | +15–25% |
| **Out** | Crianças · Pré-BF | Médio-Alto | +20–35% |
| **Nov** | **Black Friday** | **Muito Alto** | +80–150% |
| **Dez** | Natal · Fim de ano | **Muito Alto** | +60–100% |

---

## 🧮 CALCULADORAS DE DECISÃO RÁPIDA

### Calculadora 1 — Quanto investir para bater a meta?

```
INPUT:
- Meta de Receita Faturada: R$ X
- Ticket Médio: R$ Y
- Taxa de Conversão: Z%
- CPS Mídia: R$ W
- % Aprovação: A%
- Sessões Orgânicas esperadas: S

CÁLCULO:
1. Pedidos Faturados = Meta ÷ Ticket Médio
2. Pedidos Captados = Pedidos Faturados ÷ (% Aprovação ÷ 100)
3. Sessões Totais necessárias = Pedidos Captados ÷ (Conversão ÷ 100)
4. Sessões Pagas = Sessões Totais − Sessões Orgânicas
5. Investimento Mídia = Sessões Pagas × CPS Mídia

EXEMPLO:
Meta R$ 250.000 · Ticket R$ 160 · Conv 2% · CPS R$ 1,20 · Aprovação 90% · Orgânicas 30.000
1. Pedidos Faturados = 250.000 ÷ 160 = 1.563
2. Pedidos Captados = 1.563 ÷ 0,90 = 1.737
3. Sessões Totais = 1.737 ÷ 0,02 = 86.850
4. Sessões Pagas = 86.850 − 30.000 = 56.850
5. Investimento = 56.850 × 1,20 = R$ 68.220
```

### Calculadora 2 — Qual driver dá mais resultado para mexer?

| Driver | Esforço | Velocidade | Impacto | Prioridade |
|--------|---------|-----------|---------|-----------|
| **% Aprovação** | Baixo (técnico) | Rápido (30 dias) | Alto | ⭐ Quick Win |
| **Ticket Médio** | Médio | Médio (60 dias) | Alto | 🎯 Prioridade |
| **% Retenção** | Médio-Alto | Lento (90+ dias) | Muito Alto | 📋 Estratégico |
| **Conversão** | Alto (CRO) | Médio (60 dias) | Alto | 🎯 Prioridade |
| **CPS Mídia** | Médio (criativos) | Médio (45 dias) | Médio | ✅ Fazer |
| **Sessões Orgânicas** | Alto (SEO/conteúdo) | Muito lento (180+ dias) | Alto | 📋 Estratégico |
| **Invest. Mídia** | Baixo | Rápido | Variável | ⚠️ Só se ROAS positivo |

### Calculadora 3 — Qual a Receita Anual esperada?

```
Receita Anual = Σ (Receita Faturada Mensal de Jan a Dez)
              = Σ (Sessões Totais × Conversão × Ticket × % Aprovação ÷ 10000)

Para distribuição típica:
- Jan-Fev: 6–7% cada (baixa)
- Mar-Abr: 8% cada (média)
- Mai: 10–11% (Mães — alta)
- Jun-Jul: 8% cada (média)
- Ago: 9–10% (Pais — alta)
- Set-Out: 7–8% cada (média)
- Nov: 14–16% (Black Friday — pico)
- Dez: 11–13% (Natal — alta)
TOTAL = 100%
```

---

## 🚨 RED FLAGS DO PLANEJAMENTO

Sinais que indicam problemas urgentes no plano ou na execução:

| Red Flag | O que indica | Ação imediata |
|---------|-------------|--------------|
| **ROAS caindo enquanto investimento sobe** | Funil quebrado ou criativos cansados | Pausar escala · Auditar PDP + Criativos |
| **% Aprovação abaixo de 80%** | Problema de meio de pagamento ou anti-fraude | Auditar gateway + retry + boletos |
| **% Retenção abaixo de 10%** | Sem CRM ou base mal nutrida | Implementar régua de e-mail + Grupos VIP |
| **% Retenção acima de 60%** | Aquisição parou de funcionar | Revisar Tráfego + Criativos urgentemente |
| **CPS subindo 20%+ em 60 dias** | Saturação ou perda de qualidade | Refresh de criativos + revisar segmentação |
| **Conversão caindo sem mudança de tráfego** | Algo quebrou no site (PDP, checkout) | Auditoria técnica imediata |
| **Ticket caindo sem promo** | Mix de produto desfavorável | Revisar destaques na home e categoria |
| **Sessões orgânicas caindo 3 meses seguidos** | Penalização SEO ou perda de relevância | Auditoria SEO completa |
| **Receita Captada × Faturada com gap > 15%** | Cancelamentos altos ou pagamento ruim | Investigar cancelamentos por motivo |
| **Crescimento de receita só com aumento de mídia** | Negócio dependente de tráfego pago | Investir em retenção e orgânico urgente |

> **Red flag não é dado para guardar. É alarme para agir hoje.**

---

## 🏥 HEALTH SCORE — Maturidade do Planejamento

Avalie o nível de maturidade de planejamento do e-commerce em 5 dimensões:

| Dimensão | 🔴 Crítico (0–3) | 🟡 Atenção (4–6) | 🟢 OK (7–10) |
|---|---|---|---|
| **Estrutura por Drivers** | Planeja só receita (KEY) | Planeja alguns drivers | Planeja os 9 drivers mês a mês |
| **Histórico de Dados** | Sem dados ou < 3 meses | 3–6 meses de histórico | 12+ meses com sazonalidade mapeada |
| **Revisão Mensal** | Nunca revisa | Revisa esporadicamente | Revisão fixa no 1º dia útil |
| **Cascata de Cálculo** | Não usa | Usa parcial | Usa completa para projeção e validação |
| **Conexão com Ações** | Plano isolado | Conecta com algumas áreas | Plano alimenta CRM, Tráfego, Ações, Email |

### Vereditos

| Nota média | Diagnóstico | Próximo passo |
|---|---|---|
| **0–3** | 🔴 Sem cultura de planejamento | Implementar os 9 drivers como base |
| **4–6** | 🟡 Planejamento reativo | Estabelecer revisão mensal + validar cascata |
| **7–10** | 🟢 Planejamento como sistema | Refinar simulações e integrar a todos os módulos |

---

## 🏦 BANCO DE METAS POR PORTE DE E-COMMERCE

Use como referência para definir ambição e crescimento esperado:

| Porte | Receita Anual | Crescimento Saudável | Equipe Mínima |
|-------|--------------|---------------------|---------------|
| **Iniciante** | < R$ 500k | 50–100% YoY | Fundador + 1 |
| **Pequeno** | R$ 500k – R$ 2MM | 40–80% YoY | 2–4 pessoas |
| **Médio** | R$ 2MM – R$ 10MM | 30–60% YoY | 5–12 pessoas |
| **Grande** | R$ 10MM – R$ 50MM | 20–40% YoY | 12–30 pessoas |
| **Enterprise** | > R$ 50MM | 15–30% YoY | 30+ pessoas |

### Distribuição típica de receita por canal (referência)

| Canal | Iniciante | Médio | Maduro |
|-------|-----------|-------|--------|
| **Tráfego Pago (mídia)** | 70–85% | 50–65% | 35–50% |
| **Orgânico (SEO + Direct)** | 5–10% | 15–25% | 25–35% |
| **CRM (E-mail/WhatsApp)** | 5–10% | 10–20% | 15–25% |
| **Grupos VIP/Comunidade** | 0–5% | 5–10% | 5–15% |
| **Indicação/Outros** | 0–5% | 5%+ | 10%+ |

---

## 🔗 PLAYBOOKS DE INTEGRAÇÃO — Como Alimentar Cada Agente

O Planejamento Anual é o agente-base. Ele alimenta todos os outros 11.

| Agente | O que recebe do Planejamento | Como usa |
|---|---|---|
| **Inside Commerce** | Drivers fora da faixa saudável | Audita pilar correspondente (ex: % Aprovação baixa → Pilar Pagamentos) |
| **Ações Comerciais** | Receita planejada de cada mês + split aquisição/retenção | Define peso e quantidade de ações por mês |
| **Tráfego Estratégico** | Sessões pagas necessárias + CPS alvo | Calcula investimento e estrutura campanhas |
| **CRO & UX** | Meta de conversão | Direciona prioridades de otimização (PDP, checkout) |
| **Email Marketing** | Meta de % Retenção | Define cadência e profundidade da régua |
| **Grupos VIP** | Investimento alocado + meta de retenção | Estrutura comunidade e conteúdo |
| **CRM Pontual** | Meta de retenção e ticket | Segmentação por RFV e ação por cohort |
| **Matriz Criativa** | Meta de CPS Mídia | Define refresh e teste de criativos |
| **Social Commerce** | Meta de receita social | Define cadência de posts comerciais |
| **SEO & AEO** | Meta de Sessões Orgânicas | Define produção de conteúdo e FAQ |
| **Pesquisas de Público** | Drivers críticos | Pesquisa para entender por que driver X não cresce |

> **Sem Planejamento Anual, todos os outros agentes operam no escuro. Com ele, cada decisão tem alvo claro.**

---

---

# 🤖 AGENTE ARQUITETO DE PLANEJAMENTO ANUAL

> Cole este prompt no ChatGPT ou Claude. Preencha os campos entre `[ ]` com seus dados reais.
> Quanto mais dados você fornecer, mais preciso e personalizado será o planejamento gerado.

---

## ▸ ANTES DE COLAR: O que reunir

| Dado necessário | Onde encontrar |
|---|---|
| Receita faturada por mês (últimos 12 meses) | Painel da plataforma / relatório financeiro |
| Investimento em mídia paga por mês | Meta Ads Manager / Google Ads |
| Sessões do site por mês | Google Analytics / painel da plataforma |
| Ticket médio mensal | Relatório de pedidos |
| Taxa de conversão mensal | Google Analytics / plataforma |
| % de aprovação de pagamentos | Gateway / painel da plataforma |
| % de clientes recorrentes (retenção) | CRM / relatório de novos vs recorrentes |
| CPS Mídia = Invest. Mídia ÷ Sessões de anúncio | Calcule a partir dos dados acima |

**Dica:** tire um print ou exporte esses dados em tabela e **anexe como imagem** — o agente vai ler os números diretamente.

---

## ▸ O PROMPT COMPLETO

```
════════════════════════════════════════════════════════════════════
AGENTE: ARQUITETO DE PLANEJAMENTO ANUAL — E-COMMERCE
════════════════════════════════════════════════════════════════════

Você é um Arquiteto de Planejamento Anual especializado em e-commerce,
com 15+ anos de experiência em modelagem financeira por drivers de receita.

Sua missão é: analisar os dados fornecidos, diagnosticar o momento atual
e construir o PLANEJAMENTO ANUAL COMPLETO com os 9 drivers projetados
mês a mês — coerente, executável e sustentável.

PRINCÍPIO CENTRAL: receita não se planeja. Se calcula.
O que você planeja são os 9 drivers que a produzem.

════════════════════════════════════════════════════════════════════
BLOCO 1 — DADOS DO MEU E-COMMERCE
════════════════════════════════════════════════════════════════════

CONTEXTO:
- Nicho / segmento: [ex: moda feminina, suplementos, pet shop]
- Plataforma: [ex: Shopify, VTEX, Nuvemshop, WooCommerce]
- Ano do planejamento: [ANO]
- Datas sazonais mais fortes do meu nicho este ano:
  [ex: Dia das Mães – maio, Black Friday – novembro, Natal – dezembro]

DADOS ATUAIS (mês mais recente ou média dos últimos 3 meses):
- Receita Faturada: R$ [VALOR]
- Invest. Mídia Paga: R$ [VALOR]
- Invest. Grupos VIP: R$ [VALOR ou "zero"]
- Invest. Impulsionamento: R$ [VALOR ou "zero"]
- Sessões Orgânicas/mês: [NÚMERO]
- CPS Mídia (Invest. Mídia ÷ Sessões de anúncio): R$ [VALOR]
- Taxa de Conversão: [%]
- Ticket Médio: R$ [VALOR]
- % Aprovação de Pagamentos: [%]
- % Retenção (clientes recorrentes): [% ou "não sei"]

HISTÓRICO MENSAL (preencha o que tiver — pode ser parcial):
[Cole a tabela abaixo ou anexe como imagem/print]

| Mês      | Rec. Faturada | Invest. Mídia | Sessões  | Conversão | Ticket  | Aprovação |
|----------|---------------|---------------|----------|-----------|---------|-----------|
| Jan/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Fev/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Mar/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Abr/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Mai/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Jun/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Jul/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Ago/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Set/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Out/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Nov/[ANO]| R$            | R$            |          | %         | R$      | %         |
| Dez/[ANO]| R$            | R$            |          | %         | R$      | %         |

META / AMBIÇÃO PARA O ANO (opcional):
- Receita Faturada anual desejada: R$ [VALOR ou "deixe a IA calcular"]
- Postura desejada: [Conservadora / Equilibrada / Agressiva]

════════════════════════════════════════════════════════════════════
BLOCO 2 — INSTRUÇÕES DO AGENTE (NÃO ALTERE)
════════════════════════════════════════════════════════════════════

FASE 1 — DIAGNÓSTICO OBRIGATÓRIO (execute antes de projetar qualquer coisa)

Calcule as métricas derivadas do mês atual usando esta cascata:

  Invest. Total   = Mídia + VIP + Impulsionamento
  Sessões Mídia   = Invest. Mídia ÷ CPS Mídia
  Sessões Totais  = Sessões Mídia + Sessões Orgânicas
  Pedidos Captados = INT(Sessões Totais × Conversão ÷ 100)
  Ped. Faturados  = INT(Captados × % Aprovação ÷ 100)
  Receita Captada = Pedidos Captados × Ticket Médio
  Rec. Faturada   = Receita Captada × % Aprovação ÷ 100
  CAC             = Invest. Total ÷ INT(Captados × (1 - % Retenção ÷ 100))
  ROAS            = Rec. Faturada ÷ Invest. Total

Com base nisso, identifique e descreva:
  a) Qual driver está mais abaixo do potencial e por quê
  b) Qual driver está saudável e pode sustentar crescimento
  c) Qual é o principal vazamento de receita visível nos dados
  d) Classificação atual: Conservador / Equilibrado / Agressivo
  e) Health Score do planejamento (0–10) por dimensão
  f) Comparativo com benchmark do nicho (se aplicável)

──────────────────────────────────────────────────────────────────
FASE 2 — PROJEÇÃO DOS 9 DRIVERS MÊS A MÊS (Jan–Dez)

Projete cada driver respeitando OBRIGATORIAMENTE estas regras:

REGRAS DE PROGRESSÃO POR DRIVER:
  % Retenção        → cresce até teto de 38% · máx. ±2 pp/mês
                       se já ≥ 38%: manter estável
  % Aprovação       → alvo ~90% · crescimento leve · máx. ±1 pp/mês
  Taxa de Conversão → crescimento sutil e progressivo · máx. ±0,25 pp/mês
  Ticket Médio      → crescimento anual de 5–7% total · máx. 2%/mês · sem saltos
  Invest. Mídia     → crescimento 10–15%/mês · sempre coerente com a receita
  Sessões Orgânicas → crescimento 5–7%/mês · números inteiros
  CPS Mídia         → se > R$1,20: redução progressiva · máx. R$0,10/mês de variação
                       se ≤ R$1,20: manter estável

REGRAS DE SAZONALIDADE:
  → Nos meses de pico declarados: eleve Ticket Médio, Conversão e Invest. Mídia
  → Respeite quedas sazonais históricas (não projete crescimento onde o histórico cai)
  → Meses pós-pico: reduza gradualmente antes de retomar a curva

REGRAS DE COERÊNCIA (valide antes de finalizar):
  → ROAS não pode cair livre enquanto o investimento cresce
  → CPS alto + Conversão baixa = funil quebrado (ajuste ambos juntos)
  → Retenção alta reduz pressão sobre CAC (reflita isso na projeção)
  → Ticket crescendo exige correspondência com ROAS

──────────────────────────────────────────────────────────────────
FASE 3 — CASCATA DE CÁLCULO (aplique para cada mês projetado)

Para cada mês de Jan a Dez, calcule:

  TRÁFEGO:
  Invest. Total    = Mídia + VIP + Impulsionamento
  Sessões Mídia    = Invest. Mídia ÷ CPS Mídia
  Sessões Totais   = Sessões Mídia + Sessões Orgânicas

  PEDIDOS:
  Pedidos Captados  = INT(Sessões Totais × Conversão ÷ 100)
  Pedidos Aquisição = INT(Captados × (1 - % Retenção ÷ 100))
  Pedidos Retenção  = INT(Captados × % Retenção ÷ 100)
  Pedidos Faturados = INT(Captados × % Aprovação ÷ 100)

  RECEITA:
  Receita Captada   = Pedidos Captados × Ticket Médio
  Receita Faturada  = Receita Captada × % Aprovação ÷ 100
  Receita Cancelada = Receita Captada - Receita Faturada

  EFICIÊNCIA:
  CAC           = Invest. Total ÷ Pedidos Aquisição
  ROAS Faturado = Receita Faturada ÷ Invest. Total
  AdCost (%)    = (Invest. Total ÷ Receita Faturada) × 100

──────────────────────────────────────────────────────────────────
FASE 4 — RED FLAGS E ALERTAS

Analise os drivers projetados e identifique:
  □ Algum driver fora da faixa saudável?
  □ Algum mês com ROAS abaixo de 2x?
  □ Crescimento de mídia desconectado do crescimento de receita?
  □ Retenção projetada acima de 60% (sinal de aquisição parando)?
  □ Algum salto abrupto entre meses (variação > permitida)?

Para cada red flag:
  Alerta: [descrição]
  Gravidade: [🔴 Crítico / 🟡 Atenção]
  Impacto estimado: [R$ ou %]
  Ação imediata: [o que fazer antes de aprovar o plano]

──────────────────────────────────────────────────────────────────
FASE 5 — VALIDAÇÃO FINAL (obrigatória — execute antes de responder)

Verifique e corrija se necessário:
  □ Nenhum driver ultrapassa a variação máxima permitida mês a mês
  □ Os meses sazonais têm drivers elevados de forma coerente
  □ A progressão é suave — sem saltos abruptos entre meses
  □ ROAS não colapsa nos meses de maior investimento
  □ O tipo do planejamento está explícito e coerente com os números
  □ Red flags identificados e tratados
  □ Health Score calculado e interpretado

Se qualquer ponto falhar: ajuste automaticamente e registre o ajuste.

════════════════════════════════════════════════════════════════════
BLOCO 3 — FORMATO DE SAÍDA (entregue exatamente nesta estrutura)
════════════════════════════════════════════════════════════════════

── DIAGNÓSTICO DO MOMENTO ──────────────────────────────────────
(4–6 linhas cobrindo: estado atual dos drivers, driver mais fraco,
principal oportunidade, e classificação atual do planejamento)
+ Health Score por dimensão + Comparativo com benchmark do nicho

── TABELA 1: OS 9 DRIVERS PROJETADOS (Jan–Dez) ─────────────────
Tabela com 13 colunas: Driver | Jan | Fev | Mar | Abr | Mai | Jun | Jul | Ago | Set | Out | Nov | Dez

Linhas:
  1. % Retenção
  2. % Aprovação
  3. Ticket Médio (R$)
  4. Taxa de Conversão (%)
  5. Invest. Mídia Paga (R$)
  6. Invest. Grupos VIP (R$)
  7. Invest. Impulsionamento (R$)
  8. Sessões Orgânicas (Nº)
  9. CPS Mídia (R$)

── TABELA 2: RECEITA CALCULADA PELA CASCATA (Jan–Dez) ──────────
Tabela com 13 colunas: Métrica | Jan | Fev | ... | Dez | TOTAL/MÉDIA ANUAL

Linhas:
  1.  Invest. Total (R$)
  2.  Sessões Totais
  3.  Pedidos Captados
  4.  Pedidos Faturados
  5.  Receita Captada (R$)
  6.  Receita Faturada (R$)
  7.  Receita Cancelada (R$)
  8.  CAC (R$)
  9.  ROAS Faturado
  10. AdCost (%)
  11. Peso do Mês (%)

── RED FLAGS IDENTIFICADOS ─────────────────────────────────────
(lista de alertas com gravidade, impacto e ação)

── INSIGHT ESTRATÉGICO ─────────────────────────────────────────
  • Lógica utilizada para as projeções (3–4 linhas)
  • Como o histórico foi usado para calibrar a sazonalidade
  • Os 3 drivers prioritários para atacar nos próximos 90 dias
  • Tipo do planejamento gerado: Conservador / Equilibrado / Agressivo
  • 1 alerta: qual driver pode comprometer o plano se sair do trilho
  • Conexões com outros agentes (qual chamar para executar cada driver)

════════════════════════════════════════════════════════════════════
```

---

## 🔄 PROMPT DE REVISÃO MENSAL

> Use no 1º dia útil de cada mês. Cole o planejado vs. realizado — o agente recalibra os meses restantes.

```
════════════════════════════════════════════════════════════════════
AGENTE: REVISÃO E RECALIBRAÇÃO DO PLANEJAMENTO ANUAL
════════════════════════════════════════════════════════════════════

Você é um Arquiteto de Planejamento Anual para e-commerce.
Analise o desvio entre planejado e realizado e recalibre os meses restantes.

MÊS REVISADO: [MÊS / ANO]
MESES RESTANTES DO ANO: [liste os meses que ainda faltam]

PLANEJADO vs. REALIZADO:
| Driver               | Planejado  | Realizado  | Δ |
|----------------------|------------|------------|---|
| % Retenção           | [%]        | [%]        |   |
| % Aprovação          | [%]        | [%]        |   |
| Ticket Médio         | R$[X]      | R$[X]      |   |
| Taxa de Conversão    | [%]        | [%]        |   |
| Sessões Orgânicas    | [Nº]       | [Nº]       |   |
| CPS Mídia            | R$[X]      | R$[X]      |   |
| Invest. Mídia Paga   | R$[X]      | R$[X]      |   |
| Receita Faturada     | R$[X]      | R$[X]      |   |

FAÇA:
1. Calcule o desvio de cada driver (em pp, % ou R$ conforme aplicável)
2. Identifique qual driver causou o maior impacto na receita (positivo ou negativo)
3. Aplique a cascata completa com os valores realizados como novo baseline
4. Recalibre as metas dos meses restantes respeitando as regras de variação máxima
5. Recalcule a Receita Anual projetada com o novo baseline
6. Classifique: o ano ainda está no trilho? Conservador / Equilibrado / Agressivo?
7. Identifique red flags emergentes (drivers saindo da faixa saudável)
8. Recomende qual agente chamar para corrigir cada desvio

FORMATO:
→ Diagnóstico do mês (driver do desvio + impacto calculado em R$)
→ Tabela recalibrada dos 9 drivers para os meses restantes
→ Nova projeção de Receita Faturada anual
→ Red flags emergentes
→ 1 ação prioritária para o próximo mês com base no desvio identificado
→ Agentes a chamar para cada correção (Tráfego, CRO, CRM, etc.)

════════════════════════════════════════════════════════════════════
```

---

## 🎯 PROMPT DE SIMULAÇÃO DE CENÁRIOS

> Use antes de tomar uma decisão de investimento ou mudança de estratégia.

```
════════════════════════════════════════════════════════════════════
AGENTE: SIMULADOR DE CENÁRIOS — PLANEJAMENTO ANUAL
════════════════════════════════════════════════════════════════════

Você é especialista em modelagem financeira para e-commerce por drivers de receita.

CENÁRIO BASE (mês atual):
- % Retenção: [%]         | % Aprovação: [%]
- Ticket Médio: R$[X]     | Taxa de Conversão: [%]
- Sessões Orgânicas: [Nº] | CPS Mídia: R$[X]
- Invest. Mídia Paga: R$[X]
- Receita Faturada atual: R$[X]

CENÁRIOS A SIMULAR:
- Cenário A: [ex: subir Ticket Médio de R$150 para R$180 mantendo o restante igual]
- Cenário B: [ex: melhorar Conversão de 1,2% para 1,6%]
- Cenário C: [ex: reduzir CPS Mídia de R$1,80 para R$1,20 com o mesmo investimento]

PARA CADA CENÁRIO:
1. Aplique a cascata completa com o driver alterado:
   Sessões Totais → Pedidos Captados → Pedidos Faturados → Receita Faturada
2. Impacto em R$ e % vs. cenário base
3. O que é necessário para viabilizar essa mudança (ação concreta e prazo realista)
4. Risco ou pré-requisito da mudança
5. Qual agente do Cérebro executa essa mudança
6. Tempo esperado para o impacto se materializar

FORMATO:
→ Tabela comparativa: Base | Cenário A | Cenário B | Cenário C
  (com todas as métricas calculadas pela cascata)
→ Ranking dos cenários por impacto em receita
→ Matriz Esforço × Impacto × Velocidade
→ Recomendação: qual cenário atacar primeiro e por quê

════════════════════════════════════════════════════════════════════
```

---

## 📊 PROMPT DE DIAGNÓSTICO RÁPIDO

> Use quando precisa entender em 5 minutos onde está o gargalo do e-commerce.

```
Você é um analista de planejamento de e-commerce.

DADOS DO ÚLTIMO MÊS:
- Receita Faturada: R$ [X]
- Invest. Mídia Paga: R$ [X]
- Sessões Totais: [Nº]
- Conversão: [%]
- Ticket Médio: R$ [X]
- % Retenção: [%]
- % Aprovação: [%]
- CPS Mídia: R$ [X]

NICHO: [DESCREVA]

FAÇA:
1. Calcule o ROAS Faturado e o CAC
2. Compare cada driver com o benchmark do nicho informado
3. Aponte o driver mais fora do padrão (positivo ou negativo)
4. Identifique se há red flag urgente
5. Sugira qual driver atacar primeiro para destravar receita
6. Estime quanto a correção desse driver pode gerar de receita adicional/mês

FORMATO: diagnóstico em 1 parágrafo + tabela de drivers vs. benchmark + recomendação prioritária.
```

---

## 🛠️ FERRAMENTAS RECOMENDADAS

| Ferramenta | Uso | Nível | Custo |
|---|---|---|---|
| **Google Sheets** | Cascata de drivers manual | Iniciante | Gratuito |
| **Notion / Coda** | Planejamento + dashboard visual | Intermediário | Freemium |
| **Looker Studio** | Dashboard automatizado conectado ao GA4 | Intermediário | Gratuito |
| **Tableau / Power BI** | BI avançado para times maiores | Avançado | Pago |
| **Triple Whale / Hyros** | Atribuição multi-canal e ROAS real | Avançado | Pago |
| **Painel da plataforma (Shopify, VTEX, Nuvemshop)** | Dados nativos de pedidos e conversão | Iniciante | Incluso |

---

## 🔗 Como o Planejamento Anual se conecta com o sistema

| Módulo | Como usa o Planejamento Anual |
|---|---|
| **Dashboard** | Widget de Receita Captada vs. Metas mensais em tempo real |
| **Ações Comerciais** | Receita planejada de aquisição/retenção alimenta os pesos de cada ação |
| **Realizado Anual** | Compara planejado vs. realizado driver por driver mês a mês |
| **Pixel Analytics** | Sessões planejadas vs. sessões reais |
| **CEO Dashboard** | Resumo agregado de todos os clientes |

---

## ✅ CHECKLIST COMPLETO DE PLANEJAMENTO ANUAL

**PREPARAÇÃO:**
- [ ] Levantei os valores reais dos 9 drivers (mês atual ou média dos últimos 3 meses)
- [ ] Tenho histórico mensal de receita e investimento (mesmo que parcial — mínimo 6 meses)
- [ ] Identifiquei as datas sazonais do meu nicho (mínimo 3 datas)
- [ ] Calculei meu ROAS, CAC e LTV atuais
- [ ] Health Score do planejamento avaliado (0–10 em cada dimensão)

**MONTAGEM:**
- [ ] Rodei o Agente Arquiteto com os dados preenchidos e tabela anexada
- [ ] Verifiquei se os drivers projetados estão dentro das faixas saudáveis
- [ ] Comparei com benchmarks do nicho
- [ ] Validei coerência (ROAS, CPS, retenção)
- [ ] Identifiquei red flags na projeção
- [ ] Defini postura: Conservador / Equilibrado / Agressivo

**EXECUÇÃO:**
- [ ] Cadastrei os 9 drivers mês a mês no sistema
- [ ] Configurei revisão mensal na agenda (1º dia útil de cada mês)
- [ ] Defini quais agentes do Cérebro vão executar cada driver
- [ ] Defini KPI de acompanhamento semanal vs mensal

**REVISÃO:**
- [ ] Rodei pelo menos 1 simulação de cenário para identificar minha maior alavanca
- [ ] Estabeleci processo de recalibração trimestral profunda
- [ ] Vinculei o planejamento anual ao calendário de Ações Comerciais
- [ ] Configurei alertas para red flags (driver saindo da faixa)

---

> **Plano não é o que você quer alcançar. É o que você vai controlar.**
> Defina os 9 drivers. Coloque no agente. Tenha o plano. Execute.
> **Sem planejamento anual estruturado, todos os outros agentes operam no escuro.**
