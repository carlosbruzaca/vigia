# Spec: Router Service
## Serviço de Roteamento Principal (Python)

---

## 1. Propósito

O Router Service é o ponto de entrada de todas as mensagens do Telegram. Ele identifica o usuário, determina seu estado atual e direciona para o serviço apropriado (Onboarding, Operation ou responde diretamente se estiver pausado/bloqueado).

---

## 2. Responsabilidades

| Responsabilidade | Descrição |
|------------------|-----------|
| Identificação | Buscar usuário no banco pelo chat_id do Telegram |
| Criação | Criar empresa e usuário novos quando não existirem |
| Roteamento | Direcionar para o serviço correto baseado no estado |
| Validação | Garantir que dados essenciais estão presentes antes de prosseguir |

---

## 3. Estados e Destinos

| Estado do Usuário | Ação do Router |
|-------------------|----------------|
| `new` | Delegar para OnboardingService (início do onboarding) |
| `onboarding` | Delegar para OnboardingService (continua onboarding) |
| `active` | Delegar para OperationService (processar comandos) |
| `paused` | Responder com mensagem de conta suspensa |
| `blocked` | Responder com mensagem de conta cancelada |

---

## 4. Fluxo de Processamento

### 4.1 Recebimento de Mensagem

Quando uma mensagem chega do Telegram:

1. Extrair dados essenciais: chat_id, user_id (do Telegram), first_name, message_text
2. Validar que chat_id existe (se não, ignorar silenciosamente)
3. Buscar usuário na tabela vigia_users pelo chat_id

### 4.2 Usuário Existente

Se usuário for encontrado:

1. Preparar payload com: user_id, company_id, user_state, first_name, message_text, current_action
2. Atualizar last_interaction_at (opcional, pode ser fire-and-forget)
3. Verificar estado e rotear para destino apropriado

### 4.3 Novo Usuário

Se usuário não for encontrado:

1. Criar empresa na tabela vigia_companies com:
   - name: "{first_name} - Empresa"
   - status: "trial"
   - plan: "early_adopter"
   - valores padrão: fixed_cost_avg=0, variable_cost_percent=30, cash_minimum=5000
2. Criar usuário na tabela vigia_users com:
   - chat_id, telegram_id, first_name
   - state: "new"
   - onboarding_step: 0
   - company_id: id da empresa criada
3. Preparar payload marcando como novo usuário
4. Delegar para OnboardingService

---

## 5. Estrutura de Dados de Entrada

O serviço recebe do handler do Telegram:

```python
{
    "chat_id": int,           # ID do chat no Telegram (obrigatório)
    "telegram_user_id": int,  # ID do usuário no Telegram
    "first_name": str,        # Nome do usuário
    "last_name": str,         # Sobrenome (opcional)
    "username": str,          # @username (opcional)
    "message_text": str,      # Texto da mensagem (pode ser None)
    "message_id": int,        # ID da mensagem para referência
    "date": int               # Timestamp da mensagem
}

6. Estrutura de Dados de Saída

O serviço retorna para o handler:

{
    "chat_id": int,           # Para enviar resposta
    "response_text": str,     # Texto a ser enviado ao usuário
    "next_action": str,       # Opcional: ação pendente do sistema
    "log_data": dict          # Dados para auditoria em vigia_message_logs
}

Ou delega para outro serviço retornando:

{
    "delegate_to": str,       # Nome do serviço: "onboarding" | "operation"
    "payload": dict           # Dados a serem passados para o serviço
}

7. Tratamento de Erros

| Erro                               | Comportamento                                                      |
| ---------------------------------- | ------------------------------------------------------------------ |
| Supabase indisponível              | Retry 3x com backoff exponencial, depois mensagem genérica de erro |
| chat\_id inválido ou ausente       | Ignorar silenciosamente, logar warning                             |
| Erro na criação de empresa/usuário | Logar erro, retornar mensagem de erro técnico ao usuário           |
| Estado desconhecido                | Logar erro, tratar como "new" para segurança                       |

8. Integrações

8.1 Banco de Dados (Supabase)

Queries necessárias:
Buscar usuário por chat_id:

SELECT * FROM vigia_users WHERE chat_id = %s

Criar empresa:

INSERT INTO vigia_companies (name, status, plan, fixed_cost_avg, variable_cost_percent, cash_minimum)
VALUES (%s, 'trial', 'early_adopter', 0, 30, 5000)
RETURNING id

Criar usuário:

INSERT INTO vigia_users (chat_id, telegram_id, first_name, state, onboarding_step, company_id)
VALUES (%s, %s, %s, 'new', 0, %s)
RETURNING id

Atualizar last_interaction_at (opcional):

UPDATE vigia_users SET last_interaction_at = now() WHERE id = %s

8.2 Outros Serviços

| Serviço           | Quando Chamar                  | Dados Enviados                                                          |
| ----------------- | ------------------------------ | ----------------------------------------------------------------------- |
| OnboardingService | state in ('new', 'onboarding') | user\_id, company\_id, message\_text, onboarding\_step, current\_action |
| OperationService  | state == 'active'              | user\_id, company\_id, message\_text, current\_action, first\_name      |

9. Regras de Negócio Específicas

Criação atômica: Empresa e usuário devem ser criados na mesma transação lógica (se possível)
Precedência de estado: Comandos (/) devem ser detectados antes de verificar current_action, exceto quando em onboarding
Mensagem de boas-vindas para new: Se state='new' e message_text='/start', pode enviar mensagem de apresentação antes de delegar
Nunca expor dados de outra empresa: Sempre filtrar por company_id do usuário identificado

10. Critérios de Aceitação

[ ] Usuário novo recebe mensagem e é criado corretamente no banco
[ ] Usuário existente é identificado e direcionado corretamente
[ ] Usuário pausado recebe mensagem de suspensão sem acesso a funcionalidades
[ ] Erros de banco são tratados com retry e mensagem amigável
[ ] Logs de auditoria são gerados para todas as interações

11. Notas de Implementação

Usar cliente Supabase singleton (instanciado uma vez e reutilizado)
Funções principais devem ser async se usando asyncpg, ou sync com retry
Separar claramente entre: identificação, criação e roteamento
Manter funções puras (sem side effects) quando possível para facilitar testes
Usar type hints em todas as funções