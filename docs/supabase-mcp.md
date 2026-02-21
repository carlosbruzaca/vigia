# Supabase MCP Setup

Este documento registra a configuração mínima necessária para expor os dados do VigIA via um servidor MCP Supabase e para aplicar a migration inicial que cobre os domínios principais.

## 1. Migration baseline
- O schema inicial está em `generated/supabase/migrations/20260221_000000_schema_inicial.sql`. Ele cria tabelas `vigia_*`, índices, triggers e comentários descritos nas specs de banco.
- Para aplicar essa migration em um projeto Supabase existente, use o CLI oficial (que respeita `gen_random_uuid()` e `timestamptz` defaults):

```bash
supabase db set-migrations-dir generated/supabase/migrations
supabase db push
```

ou rode o SQL direto via `psql`/PGAdmin apontando para o banco, garantindo que `SUPABASE_DB_PASS` esteja definido.

## 2. Criar credenciais do Supabase
1. No dashboard do Supabase, abra *Settings > API*.
2. Copie o *Project URL* e o `service_role` (essas chaves têm permissão total). Esses valores abastecerão `SUPABASE_URL` e `SUPABASE_KEY` do `.env`.
3. Gere também um *personal access token* com o escopo mínimo para MCP (leitura/escrita). Ele não aparece novamente após ser copiado, então salve em um cofre.

## 3. MCP server local
1. O servidor Supabase MCP aceita tanto opções via arquivo `config.json` quanto variáveis de ambiente; o CLI oficial roda com:

```bash
npx -y @supabase/mcp-server-supabase@latest --read-only --project-ref=<project-ref>
```

Substitua `<project-ref>` pelo identificador do seu projeto (visível no dashboard e no `.supabase/config.toml` se existir).
2. Defina a variável `SUPABASE_ACCESS_TOKEN` com o token criado no passo anterior. Se preferir, o mesmo valor pode ir dentro de um bloco `env` do cliente (Cline, Claude, Cursor etc.).

## 4. Configuração típica do cliente MCP
Adicione ao JSON de configuração do cliente:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--read-only",
        "--project-ref=<project-ref>"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "<personal-access-token>"
      }
    }
  }
}
```

Os clientes (Claude Desktop, Cline, Cursor etc.) usam esse servidor para expor as tabelas `vigia_*` e a API definida na pasta `generated/supabase`.

## 5. Operação contínua
- Execute o servidor MCP como serviço (systemd, PM2, container) se vários membros precisarem de contexto.
- Mantenha o diretório `generated/supabase/migrations` versionado; novas alterações devem gerar arquivos numerados conforme `YYYYMMDD_HHMMSS_nome.sql`.
- Quando um novo MCP precisar de suporte a funções adicionais, documente a query no serviço correspondente (`src/services/...`) e mantenha o registro de scripts.
