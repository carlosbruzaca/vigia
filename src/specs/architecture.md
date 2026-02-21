# VigIA - Architecture Document
## Arquitetura Técnica e Decisões de Design (Stack Python + Supabase)

---

## 1. Visão Geral da Arquitetura

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Telegram      │────▶│     Python      │────▶│   Supabase      │
│   (Cliente)     │◄────│    (Backend)    │◄────│  (PostgreSQL)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
│
▼
┌──────────────┐
│  APScheduler │
│  (Agendador) │
└──────────────┘


**Estilo Arquitetural:** Modular, event-driven via webhooks, stateless nos serviços, stateful no banco.

---

## 2. Componentes

### 2.1 Telegram Bot (python-telegram-bot)
- **Função:** Interface única com o usuário
- **Responsabilidade:** Receber mensagens, enviar respostas formatadas
- **Não faz:** Lógica de negócio, cálculos, persistência
- **Padrão:** Handlers registrados no `main.py`, chamam serviços

### 2.2 Python Backend (Serviços)
- **Função:** Orquestração e processamento de regras de negócio
- **Estrutura:** Módulos separados por domínio em `src/services/`
- **Responsabilidade:** 
  - Roteamento por estado do usuário
  - Validação de inputs
  - Cálculos (burn rate)
  - Agendamento (relatório 7h)
- **Não faz:** Armazenar estado (usa Supabase)

### 2.3 Supabase (Backend de Dados)
- **Função:** Fonte única de verdade
- **Tecnologia:** PostgreSQL 15 + PostgREST
- **Responsabilidade:**
  - Estado dos usuários (state machine)
  - Dados financeiros (receitas, despesas, atrasos)
  - Configurações de negócio (custos, alertas)
  - Logs de auditoria
- **Acesso:** Via `supabase-py` ou queries SQL diretas

### 2.4 APScheduler
- **Função:** Agendamento de tarefas periódicas
- **Responsabilidade:** Disparar relatório diário às 7h, verificar inatividade às 18h
- **Execução:** Thread separada ou processo async


---

## 4. Modelo de Estados (State Machine)

┌─────────┐    cadastro     ┌─────────────┐   coleta dados   ┌─────────┐
│   NEW   │ ───────────────▶│  ONBOARDING │ ────────────────▶│ ACTIVE  │
└─────────┘                 └─────────────┘                  └────┬────┘
▲                                                            │
│                    ┌─────────────┐                         │
└────────────────────│   PAUSED    │◄────────────────────────┘
reativação        │  (pagamento)│    pausa por inadimplência
└──────┬──────┘
│
▼
┌─────────────┐
│   BLOCKED   │
│  (cancelado)│
└─────────────┘


**Transições:**
- `new` → `onboarding`: Criação do usuário (automático)
- `onboarding` → `active`: Conclusão da coleta de 3 dados
- `active` → `paused`: Falta de pagamento ou solicitação
- `paused` → `active`: Pagamento confirmado ou reativação
- `any` → `blocked`: Cancelamento definitivo

---

## 5. Fluxo de Dados por Evento

### 5.1 Mensagem do Usuário

Telegram Webhook → main.py handler → RouterService.identify_user()
→ RouterService.route_by_state() → [OnboardingService | OperationService]
→ Telegram API resposta

### 5.2 Relatório Agendado

APScheduler 7h → DailyReportService.generate_all()
→ Para cada empresa ativa: calcular métricas → formatar mensagem
→ Telegram API envio → log em vigia_alerts


### 5.3 Webhook de Pagamento (Futuro)

Asaas → HTTP endpoint em main.py → SubscriptionService.process_webhook()
→ Atualiza status → notifica usuário se ativação


---

## 6. Serviços Python (Especificação)

### 6.1 RouterService (`src/services/router.py`)
**Responsabilidade:** Receber toda mensagem, identificar usuário, direcionar.

**Métodos principais:**
- `identify_user(chat_id: int) -> User | None` - Busca ou cria usuário
- `route_by_state(user: User, message: str) -> str` - Retorna resposta ou delega
- `create_new_user(chat_id: int, user_data: dict) -> User` - Cria empresa + usuário

**Fluxo:**
1. Recebe `chat_id` e `message_text`
2. Busca usuário no Supabase por `chat_id`
3. Se não existe: cria empresa → cria usuário → state='new'
4. Baseado em `user.state`, delega para serviço apropriado
5. Retorna resposta para enviar ao Telegram

### 6.2 OnboardingService (`src/services/onboarding.py`)
**Responsabilidade:** Coletar 3 dados de configuração.

**Métodos principais:**
- `get_current_step(user: User) -> int` - Determina etapa baseada nos dados
- `process_input(user: User, input_text: str) -> str` - Valida e salva
- `ask_question(step: int) -> str` - Retorna mensagem apropriada

**Lógica de steps:**
- Step 1: Pergunta `fixed_cost_avg` → valida > 0 → salva → step 2
- Step 2: Pergunta `variable_cost_percent` → valida 0-100 → salva → step 3  
- Step 3: Pergunta `cash_minimum` → valida >= 0 → salva → ativa usuário
- Step 4: Completo, retorna mensagem de boas-vindas

### 6.3 OperationService (`src/services/operation.py`)
**Responsabilidade:** Processar comandos diários.

**Métodos principais:**
- `handle_command(user: User, command: str) -> str` - /start, /receita, /despesa, /relatorio, /ajuda
- `set_pending_action(user: User, action: str)` - Define `current_action` no banco
- `process_number_input(user: User, value: float) -> str` - Salva receita/despesa
- `format_confirmation(entry_type: str, value: float) -> str` - Mensagem de sucesso

**Comandos:**
- `/start` → Mensagem de boas-vindas
- `/receita` → Set `awaiting_revenue_value` → pergunta valor
- `/despesa` → Set `awaiting_expense_value` → pergunta valor
- `/relatorio` → Chama `DailyReportService.generate_single(user.company_id)`
- `/ajuda` → Lista de comandos

### 6.4 DailyReportService (`src/services/daily_report.py`)
**Responsabilidade:** Gerar e enviar relatórios.

**Métodos principais:**
- `generate_all()` - Chamado pelo scheduler, lista empresas ativas
- `generate_single(company_id: str, chat_id: int | None = None)` - Gera um relatório
- `calculate_metrics(company_id: str) -> Metrics` - Queries no Supabase
- `format_message(metrics: Metrics, company: Company) -> str` - Template da mensagem
- `send_report(chat_id: int, message: str)` - Envia via Telegram
- `log_alert(company_id: str, message: str, data: dict)` - Salva em vigia_alerts

**Queries necessárias:**
- Faturamento ontem: `SUM(amount) WHERE type='revenue' AND entry_date=CURRENT_DATE-1`
- Média 7 dias: `SUM(amount)/7 WHERE type='revenue' AND entry_date>=CURRENT_DATE-7`
- Saldo atual: `SUM(CASE type WHEN 'revenue' THEN amount ELSE -amount END)`
- Atrasos: `COUNT(*), SUM(amount) FROM vigia_receivables WHERE status IN ('pending','overdue')`

---

## 7. Modelos de Dados (Python)

### 7.1 Dataclasses (src/models/database.py)

```python
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

@dataclass
class Company:
    id: str
    name: str
    cnpj: Optional[str]
    email: Optional[str]
    fixed_cost_avg: Decimal
    variable_cost_percent: Decimal
    cash_minimum: Decimal
    alert_days_threshold: int
    status: str  # 'active', 'paused', 'cancelled', 'trial'
    plan: str  # 'basic', 'pro', 'early_adopter'
    created_at: datetime
    updated_at: datetime

@dataclass
class User:
    id: str
    company_id: str
    chat_id: int
    telegram_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    state: str  # 'new', 'onboarding', 'active', 'paused', 'blocked'
    current_action: Optional[str]
    onboarding_step: int
    last_interaction_at: datetime
    created_at: datetime
    updated_at: datetime

@dataclass
class Entry:
    id: str
    company_id: str
    user_id: Optional[str]
    entry_date: date
    amount: Decimal
    type: str  # 'revenue', 'expense'
    source: str  # 'manual', 'import', 'projection'
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Metrics:
    revenue_yesterday: Decimal
    revenue_avg_7days: Decimal
    cash_balance: Decimal
    overdue_count: int
    overdue_total: Decimal
    daily_burn: Decimal
    days_to_zero: int
    variation_percent: float
    alert_level: str  # 'critical', 'warning', 'normal'

9. Tratamento de Erros

| Cenário                               | Ação                                                         |
| ------------------------------------- | ------------------------------------------------------------ |
| Supabase indisponível                 | Retry 3x com backoff, log erro, mensagem genérica ao usuário |
| Input inválido                        | Mensagem específica de erro, mantém estado atual             |
| Usuário não encontrado                | Cria novo (fluxo normal)                                     |
| Cálculo impossível (divisão por zero) | Retorna "dias infinitos" ou mensagem de segurança            |
| Telegram API falha                    | Log erro, não quebra fluxo                                   |

11. Segurança
11.1 Isolamento de Dados
Cada query filtra por company_id
Nunca expor dados de outras empresas
Logs sem dados sensíveis (valores ok, CPF não)
