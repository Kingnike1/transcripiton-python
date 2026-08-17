# AMIP Production Runbook

## Topologia

A Stack 14 mantém o monólito modular e separa apenas processos operacionais: `web`, `worker`, migration one-shot, PostgreSQL e backup. O storage de áudio continua em volume persistente compartilhado entre web e worker.

## Requisitos

- Docker Engine + Compose;
- host Linux com disco persistente e espaço compatível com os áudios;
- TLS terminado por proxy/plataforma na frente da porta do AMIP;
- `.env.production` fora do Git, com `ENVIRONMENT=production`, `DEBUG=false`, `SECRET_KEY` forte e `POSTGRES_PASSWORD` forte.

## Deploy

1. Copie `.env.example` para `.env.production` e substitua todos os segredos/placeholders.
2. Execute `docker compose -f compose.production.yaml build`.
3. Execute `docker compose -f compose.production.yaml up -d db` e aguarde o healthcheck.
4. Execute `docker compose -f compose.production.yaml run --rm migrate`.
5. Execute `docker compose -f compose.production.yaml up -d web worker backup`.
6. Valide `/health` (liveness) e `/ready` (banco acessível).

Nunca execute `reset_db` em staging/produção. Migrations Alembic são o único mecanismo de alteração de schema nesses ambientes.

## Backups

O serviço `backup` cria diariamente:

- dump PostgreSQL em formato custom (`pg_dump -Fc`);
- arquivo compactado do storage de áudio;
- retenção local padrão de 14 dias.

Para produção real, o diretório/volume de backup deve também ser replicado para um destino externo ao host. Backup no mesmo host protege contra erro lógico, mas não contra perda total da máquina.

### Restore de banco

Pare `web` e `worker`, crie/limpe o banco alvo e use `pg_restore` sobre o dump escolhido. Em seguida execute `alembic upgrade head` antes de religar os processos.

### Restore de storage

Pare `web` e `worker`, restaure o `tar.gz` no volume persistente preservando a raiz `storage/`, valide permissões e só então religue os processos.

Teste de restore deve ser feito periodicamente; backup não testado não é garantia de recuperação.

## Observabilidade

- `/health`: confirma que o processo HTTP está vivo;
- `/ready`: confirma que o processo consegue alcançar o banco;
- logs incluem request IDs já existentes e devem ser coletados pelo runtime/plataforma;
- reinícios são `unless-stopped`;
- PostgreSQL possui healthcheck antes de migrations e aplicação.

Alertas externos devem observar ao menos indisponibilidade de `/ready`, reinícios repetidos, disco e falha/idade do último backup.

## Hardening

- não exponha a porta 5432 publicamente;
- use TLS no endpoint público;
- mantenha `.env.production` fora do repositório;
- use senhas/segredos únicos e longos;
- limite acesso ao host e ao volume de backups;
- aplique atualizações de imagem/dependências após os gates do projeto;
- não execute modelos/worker com privilégios de host desnecessários.

## Rollback

Rollback de aplicação deve reutilizar uma imagem/commit anterior compatível com o schema atual. Antes de qualquer migration destrutiva futura, produza backup verificável e defina explicitamente o procedimento de downgrade.
