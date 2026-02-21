# Spec: Onboarding Service
## Serviço de Coleta de Dados de Configuração (Python)

---

## 1. Propósito

O Onboarding Service gerencia o processo de configuração inicial do usuário, coletando 3 dados essenciais para o cálculo de burn rate: custo fixo mensal, percentual de custo variável e caixa mínimo desejado. O processo é guiado por uma máquina de estados simples (steps 1-4).

---

## 2. Responsabilidades

| Responsabilidade | Descrição |
|------------------|-----------|
| Determinar etapa | Identificar em qual step o usuário está baseado nos dados preenchidos |
| Validar input | Verificar se o valor informado é número válido e dentro do range esperado |
| Persistir dados | Salvar cada resposta na tabela vigia_companies |
| Gerenciar estado | Atualizar onboarding_step e current_action do usuário |
| Conduzir diálogo | Enviar perguntas apropriadas e mensagens de erro/ confirmação |

---

## 3. Máquina de Estados (Steps)

Step 0: Não iniciado (novo usuário)
└── Ação: Perguntar custo fixo
└── Próximo: Step 1
Step 1: Aguardando custo fixo
└── Validação: número > 0
└── Persistência: salvar em fixed_cost_avg
└── Ação: Perguntar % variável
└── Próximo: Step 2
Step 2: Aguardando % variável
└── Validação: 0 <= número <= 100
└── Persistência: salvar em variable_cost_percent
└── Ação: Perguntar caixa mínimo
└── Próximo: Step 3
Step 3: Aguardando caixa mínimo
└── Validação: número >= 0
└── Persistência: salvar em cash_minimum
└── Ação: Finalizar onboarding
└── Próximo: Step 4
Step 4: Completo
└── Ação: Ativar usuário (state='active')
└── Mensagem: Boas-vindas e lista de comandos


---

## 4. Lógica de Determinação de Step

O serviço deve determinar o step atual analisando os dados da empresa:

| Condição | Step | current_action |
|----------|------|----------------|
| fixed_cost_avg IS NULL OU = 0 | 1 | awaiting_fixed_cost |
| variable_cost_percent IS NULL OU = 30 (default) E step < 2 | 2 | awaiting_variable_cost |
| cash_minimum IS NULL OU = 5000 (default) E step < 3 | 3 | awaiting_cash_minimum |
| Todos preenchidos | 4 | NULL |

**Nota:** Os valores 30 e 5000 são defaults do banco, então deve-se verificar também o onboarding_step para distinguir entre "ainda não preenchido" e "preenchido com valor igual ao default".

---

## 5. Fluxo de Processamento

### 5.1 Entrada do Serviço

Recebe do Router Service:

```python
{
    "user_id": str,           # UUID do usuário
    "company_id": str,        # UUID da empresa
    "chat_id": int,           # Para enviar respostas
    "first_name": str,        # Nome para personalizar mensagens
    "message_text": str,      # Input do usuário (pode ser None na primeira interação)
    "onboarding_step": int,   # Step atual (0-4)
    "current_action": str     # Ação pendente ou None
}

5.2 Processamento
Buscar dados completos da empresa no banco (vigia_companies)
Determinar step atual baseado nos dados (função get_current_step)
Se não há input (message_text vazio ou None):
Retornar pergunta apropriada para o step atual
Se há input:
Validar input numérico (remover R$, pontos, espaços, converter vírgula)
Validar range específico do step
Se inválido: retornar mensagem de erro e repetir mesma pergunta
Se válido: persistir no banco, avançar step, retornar próxima pergunta ou mensagem final
5.3 Saída do Serviço
Retorna para o handler do Telegram:

{
    "chat_id": int,
    "response_text": str,     # Pergunta, confirmação ou mensagem de erro
    "update_user_state": bool, # Se deve atualizar state do usuário no banco
    "new_state": str,         # Novo state se update_user_state=True
    "new_onboarding_step": int # Novo step para atualizar no banco
}

6. Validações por Step

| Step | Campo                   | Validação     | Mensagem de Erro                         |
| ---- | ----------------------- | ------------- | ---------------------------------------- |
| 1    | fixed\_cost\_avg        | > 0           | "O custo fixo deve ser maior que zero"   |
| 2    | variable\_cost\_percent | 0 <= x <= 100 | "A porcentagem deve estar entre 0 e 100" |
| 3    | cash\_minimum           | >= 0          | "O caixa mínimo não pode ser negativo"   |

Validação de formato numérico:

Remover: R,r , espaços, pontos de milhar
Substituir vírgula decimal por ponto
Tentar converter para float
Se falhar: "Por favor, digite apenas números (ex: 5000)"

7. Mensagens do Diálogo

7.1 Perguntas

Step 1 - Custo Fixo:

💰 Vamos configurar sua vigilância financeira!

Qual seu custo fixo mensal médio? 
(Inclua aluguel, salários, internet, etc.)

Digite só o número em reais (ex: 5000)

Step 2 - % Variável:

✅ Custo fixo registrado: R$ {valor}

📊 Agora, qual porcentagem do seu faturamento vira custo variável?
(impostos, comissões, matéria-prima)

Digite um número de 0 a 100:

Step 3 - Caixa Mínimo:

✅ Custo variável: {valor}%

🛡️ Por último: qual valor mínimo de caixa você quer manter para se sentir seguro?
(ex: 10000 para cobrir 2 meses de custo fixo)

Digite o valor:

7.2 Mensagem Final (Step 4)

✅ Caixa mínimo: R$ {valor}

🎉 Configuração completa! 

Amanhã cedo você recebe seu primeiro relatório.

Comandos disponíveis:
/receita - Registrar faturamento do dia
/despesa - Registrar despesa do dia  
/relatorio - Ver situação atual agora
/ajuda - Ver todos os comandos

7.3 Mensagens de Erro

Input não é número:

❌ Não entendi esse valor.

Por favor, digite apenas números.
Exemplos: 5000, 12500, 10000

Input fora do range:

❌ {mensagem específica do step}

Tente novamente:

8. Integrações com Banco de Dados

8.1 Queries Necessárias
Buscar empresa:

SELECT * FROM vigia_companies WHERE id = %s

Atualizar custo fixo (Step 1):

UPDATE vigia_companies 
SET fixed_cost_avg = %s, updated_at = now() 
WHERE id = %s

Atualizar % variável (Step 2):

UPDATE vigia_companies 
SET variable_cost_percent = %s, updated_at = now() 
WHERE id = %s

Atualizar caixa mínimo (Step 3):

UPDATE vigia_companies 
SET cash_minimum = %s, updated_at = now() 
WHERE id = %s

Atualizar usuário (após cada step):

UPDATE vigia_users 
SET current_action = %s, 
    onboarding_step = %s, 
    last_interaction_at = now() 
WHERE id = %s

Ativar usuário (Step 4):

UPDATE vigia_users 
SET state = 'active',
    current_action = NULL,
    onboarding_step = 4,
    last_interaction_at = now() 
WHERE id = %s

9. Tratamento de Erros

| Cenário                                      | Comportamento                                                     |
| -------------------------------------------- | ----------------------------------------------------------------- |
| Empresa não encontrada                       | Logar erro crítico, retornar mensagem de erro técnico             |
| Falha ao salvar no banco                     | Retry 1x, se falhar: manter mesmo step, informar erro ao usuário  |
| Input vazio após step 0                      | Tratar como "usuário não respondeu ainda", reenviar pergunta      |
| Usuário manda comando (/) durante onboarding | Interromper onboarding, retornar sinal para Router tratar comando |


10. Regras de Negócio Específicas

Persistência obrigatória: Só avançar step se dado foi salvo com sucesso no banco
Idempotência: Se usuário enviar mesmo valor 2x, aceitar e avançar (não travar)
Formatação de moeda: Na confirmação, formatar com R$ e separador de milhar brasileiro
Progresso visível: Sempre confirmar o valor recebido antes de próxima pergunta
Cancelamento: Se usuário não completar em 7 dias, enviar lembrete (feature futura)

11. Critérios de Aceitação

[ ] Usuário novo completa onboarding em 3 mensagens
[ ] Validações rejeitam inputs inválidos com mensagem clara
[ ] Dados são persistidos corretamente na tabela vigia_companies
[ ] Ao final, usuário tem state='active' e onboarding_step=4
[ ] Mensagem final lista todos os comandos disponíveis
[ ] Se interrompido no meio, retoma do step correto ao voltar

12. Notas de Implementação

Função get_current_step(company: Company) -> int deve ser pura e testável
Função validate_input(value: str, step: int) -> tuple[bool, float, str] retorna (válido, valor_convertido, mensagem_erro)
Separar formatação de moeda em função utilitária reutilizável
Usar transações se cliente Supabase permitir (garantir atomicidade)
Manter estado mínimo: só depende dos dados do banco, não de variáveis em memória