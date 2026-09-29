# Cockpit da Carteira — fundação v1

Entrega funcional: o Cockpit abre após o login e também está na navegação da agência e dos projetos. Usa o cadastro real de projetos do Supabase. Não depende da credencial Google para abrir, consultar ou editar os indicadores.

## O que já funciona

- Carteira por competência (mês/ano), squad, responsável, cliente e situação.
- Receita faturada, meta de receita, investimento, orçamento e ROAS consolidado.
- Projeção linear por data efetiva de apuração, com alerta de defasagem.
- Cadastro e edição nativos dos valores mensais, pedidos pagos, sessões e observações.
- Persistência no Supabase, revisão por competência/projeto e histórico das últimas 20 versões na tela.
- Exportação CSV e importação com prévia, validação e gravação atômica do lote.
- Campos desconhecidos, números negativos, competências incorretas e datas futuras são rejeitados. Edições simultâneas causam conflito explícito, sem sobrescrever a versão mais recente.

## Dados e cálculos

Grão: **um projeto × um mês**. Os valores de receita/investimento são acumulados até `as_of`, não valores diários. Metas e orçamento são mensais. Valores monetários em BRL, precisão de centavos; contagens inteiras. Vazio significa ausente, zero significa resultado zero. Importar CSV substitui os campos do registro, inclusive os vazios.

ROAS consolidado = soma das receitas / soma dos investimentos dos clientes que possuem ambos os valores. Não é média simples de ROAS. Totais de receita/meta/investimento somam apenas valores informados, com cobertura parcial indicada na tela.

Projeção = receita / (dia apurado / dias do mês). Ritmo = projeção / meta mensal. Crítico abaixo de 90%; atenção abaixo de 100%; no ritmo a partir de 100%. Apuração defasada em mais de dois dias tem prioridade como "Desatualizado". Meses futuros são "Planejado". Projeção não é garantia de fechamento.

## Estrutura aplicada

Migrações remotas `cockpit_foundation_v1` e `cockpit_atomic_import`, com SQL de referência em `database/`:

- `cockpit_private.monthly_metrics`: valores atuais, chave `(project_id, period)`, revisão, origem, autor e horário.
- `cockpit_private.metric_history`: retrato de cada versão gravada.
- RPCs públicas `cockpit_read_month`, `cockpit_save_month`, `cockpit_save_batch`, `cockpit_history` são SECURITY INVOKER. Delegam a funções privadas com acesso restrito e identidade verificada por `auth.uid()` e `auth.users`.
- As tabelas privadas não têm grants diretos para anon/authenticated. Nenhuma RLS ou política existente foi criada, alterada ou desabilitada. O esquema privado não deve ser adicionado aos esquemas expostos da Data API.
- A regra de carteira segue a aplicação existente: CEO vê todos; head vê seu squad; analista vê projetos de seu e-mail. Perfil existente é lido de `public.usuarios`. A segurança global desse cadastro continua com suas limitações anteriores; este lote não corrige RLS nem torna o SaaS inteiro seguro para produção multi-tenant.

## Validação

49 testes Python aprovados, incluindo os 25 já aceitos do P0.2 e 24 verificações de números, datas, ausência de dados, cálculos, cobertura, CSV e renderização do Cockpit. Teste transacional no banco, com ROLLBACK, aprovou gravação/histórico, conflitos, rejeição de acesso anônimo e de acesso direto às tabelas, e atomicidade de importação. Nenhum resultado financeiro de teste foi mantido.

## Limites desta entrega

A planilha consolidada anterior não foi fornecida neste lote. Não houve migração automática de histórico nem de resultados dos GPS. Para começar a substituir a planilha, baixar o modelo CSV na tela e importar os valores reais, ou preenchê-los no próprio Cockpit. Isso evita tratar ausência de integração como resultado zero. A credencial Google inválida já observada continua sendo uma pendência da integração anterior, sem impedir o Cockpit.

Cadastro de clientes reaproveitado; edição do cadastro, sincronização automática das plataformas, Creative Intelligence e RLS estão fora desta entrega. O aplicativo novo está na branch `feature/cockpit-carteira`; a fundação privada já está aplicada no Supabase. O PR #1 de autenticação foi integrado com os testes automatizados aceitos pelo usuário.
