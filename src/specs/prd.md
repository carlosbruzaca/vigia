# VigIA - Product Requirements Document
## Versão 1.0 - MVP (Stack Python + Supabase)
### Data: 2026-02-21

---

## 1. Visão do Produto

### 1.1 Problema
PMEs brasileiras (especialmente em São Luís/MA) descobrem problemas de caixa quando já é tarde. Não têm previsibilidade financeira e sofrem com surpresas de falta de dinheiro para pagar fornecedores, salários ou impostos.

### 1.2 Solução
VigIA é um bot do Telegram que funciona como "vigia" do caixa. Pergunta diariamente os valores de entrada/saída e avisa com antecedência quando o caixa vai acabar, dando tempo para o empresário tomar decisões (negociar prazo, cobrar cliente, adiar compra).

### 1.3 Diferencial
- **Simples:** Sem planilhas, sem apps para instalar, sem integração bancária complexa
- **Proativo:** Avisa antes do problema, não só registra o passado
- **Conversacional:** Interface natural (conversa no Telegram), não formulários

---

## 2. Personas

### 2.1 Dono de PME (Principal)
- **Nome:** Renato, 42 anos, dono de agência de eventos em São Luís
- **Dores:** Não entende de finanças, usa planilha desatualizada, descobre que vai faltar dinheiro quando o fornecedor liga cobrando
- **Ganhos:** Quer saber com 10-15 dias de antecedência se precisa se preocupar
- **Comportamento:** Usa WhatsApp/Telegram o dia todo, prefere texto a planilhas

### 2.2 Contador Parceiro (Secundário)
- **Nome:** Carla, contadora de 8 PMEs locais
- **Dores:** Clientes desorganizados, não enviam dados no prazo, surpresas na hora do imposto
- **Ganhos:** Cliente organizado sem ter que ensinar a usar sistema complexo

---

## 3. Funcionalidades MVP (Fase 1)

### 3.1 Onboarding (Configuração Inicial)
- [ ] Cadastro via conversa no Telegram
- [ ] Coleta de: custo fixo mensal, % de custo variável, caixa mínimo desejado
- [ ] Explicação dos comandos básicos
- [ ] Ativação automática após configuração

### 3.2 Operação Diária
- [ ] Comando `/receita` para lançar faturamento do dia
- [ ] Comando `/despesa` para lançar pagamento do dia
- [ ] Comando `/relatorio` para ver situação atual
- [ ] Validação de inputs (só aceita números válidos)

### 3.3 Relatório Automático
- [ ] Envio diário às 7h da manhã
- [ ] Conteúdo: faturamento ontem, variação vs média, clientes em atraso, saldo atual, dias até quebrar
- [ ] Alerta visual (🔴/⚠️) baseado em dias de caixa restante

### 3.4 Gestão de Inadimplência
- [ ] Comando `/receber` para cadastrar cliente em atraso
- [ ] Inclusão automática no relatório diário
- [ ] Cálculo de "ganho de dias" se receber os atrasados

### 3.5 Cobrança de Dados
- [ ] Notificação após 2 dias sem lançamento
- [ ] Mensagem: "Faz 2 dias que não recebo dados. Poderia me informar agora?"

---

## 4. Funcionalidades Pós-MVP (Fase 2+)

### 4.2 Importação Histórica (Mês 3)
- Serviço avulso de R$ 350 para importar 6-12 meses de histórico via Excel
- Feito manualmente pelo time VigIA (não automatizado ainda)

### 4.3 Integração Bancária (Mês 4+)
- Leitura automática de extratos (Open Finance)
- Reduzir fricção de lançamento manual

### 4.4 Multi-usuário (Plano Pro)
- Vários funcionários da mesma empresa lançando dados
- Permissões (só dono vê relatório completo)

---

## 5. Requisitos Não-Funcionais

| Aspecto | Requisito |
|---------|-----------|
| **Plataforma** | Apenas Telegram (sem app web no MVP) |
| **Tempo de Resposta** | < 3 segundos entre mensagem e resposta do bot |
| **Disponibilidade** | 99% uptime (manutenção agendada fora do horário comercial) |
| **Segurança** | Dados isolados por empresa (preparação para RLS) |
| **Backup** | Retenção de 1 ano de logs e dados financeiros |
| **Compliance** | LGPD básica (exclusão de dados sob demanda) |

---

## 6. Métricas de Sucesso (OKRs)

### Trimestre 1 (Lançamento)
- **KR1:** 30 empresas cadastradas e ativas
- **KR2:** 80% dos usuários fazem pelo menos 3 lançamentos por semana
- **KR3:** NPS > 50 (pesquisa com 20+ usuários)

### Trimestre 2 (Validação)
- **KR1:** 50 clientes pagos (recorrência mensal)
- **KR2:** Churn mensal < 10%
- **KR3:** Ticket médio R$ 120 (mix de planos)

### Trimestre 3 (Escala)
- **KR1:** 100 clientes pagos
- **KR2:** Expansão para outros 3 municípios do MA
- **KR3:** Lucro líquido R$ 5.000/mês

---

## 7. Roadmap de Lançamento

| Fase | Período | Entregáveis |
|------|---------|-------------|
| **Alpha** | Semana 1-2 | Router + Onboarding funcionando, 2 empresas teste |
| **Beta** | Semana 3-4 | Operação + Relatório diário, 10 empresas (early adopters) |
| **Launch** | Mês 2 | Cobrança de dados + Ajustes, abertura para público |
| **Scale** | Mês 3+ | Importação histórica + Marketing local |

---

## 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Cliente não entende o valor | Média | Alto | Onboarding humano nos primeiros 20 clientes |
| Concorrência de ERPs grandes | Baixa | Médio | Foco em simplicidade, não competir em features |
| Dependência do Telegram | Baixa | Alto | Arquitetura preparada para WhatsApp Business API futuro |
| Sazonalidade forte em SLZ | Alta | Médio | Foco em comércios de eventos/safras que entendem variação |

---

## 9. Glossário

- **Burn Rate:** Velocidade de queima de caixa (quanto gasta por dia)
- **Runway:** Dias de caixa restantes até acabar
- **Early Adopter:** Primeiros 15 clientes com desconto (R$ 79) em troca de feedback
- **VigIA:** "Vigilância Inteligente Artificial" (trocadilho com "vigiar")

---

## 10. Stack Tecnológica (Especificada)

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Linguagem | Python 3.11+ | Simples, grande comunidade, bibliotecas maduras |
| Bot Telegram | python-telegram-bot | Oficial, bem documentada, async |
| Banco | Supabase (PostgreSQL) | Managed, realtime, auth integrado |
| Agendamento | APScheduler | Nativo Python, flexível |
| Deploy | VPS + PM2/Docker | Custo baixo, controle total |
| Logs | logging (stdlib) | Sem dependência externa |

