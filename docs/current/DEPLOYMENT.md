# Execução e deployment atual

## Estado de prontidão

O AMIP está pronto para **desenvolvimento local e integração técnica**, mas **ainda não está aprovado para exposição pública/produção multiusuário**.

Faltam antes de produção, entre outros itens:

- autenticação e autorização;
- rate limiting/quotas;
- PostgreSQL para concorrência multiusuário relevante;
- storage persistente/remoto quando necessário;
- backup/restore operacional;
- readiness/observabilidade completa;
- políticas de privacidade/LGPD;
- jobs persistentes e worker;
- reverse proxy/HTTPS e limites de upload no edge.

Não existe Dockerfile/Compose oficial no repositório atual. Exemplos antigos de Docker/cloud foram removidos da documentação ativa para não serem confundidos com infraestrutura entregue.

## Requisitos locais

- Python 3.11 ou 3.12;
- Git;
- `ffprobe` disponível no PATH para upload real de áudio;
- SQLite para o fluxo padrão de desenvolvimento.

## Setup

```bash
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python

python -m venv .venv
```

Ativação:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instalação para desenvolvimento:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Configuração:

```bash
cp .env.example .env
```

No Windows, copie `.env.example` para `.env` manualmente se necessário.

## Banco

A aplicação não cria schema no startup.

Antes de iniciar:

```bash
alembic upgrade head
```

Nunca substitua esse fluxo por `Base.metadata.create_all()` em deployment.

## Executar aplicação

```bash
uvicorn main:app --reload
```

Com os defaults locais:

```text
http://127.0.0.1:8000
```

OpenAPI:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
GET /health
```

## `ffprobe`

Uploads reais exigem `ffprobe`, normalmente distribuído com FFmpeg.

Configuração:

```text
FFPROBE_BINARY=ffprobe
FFPROBE_TIMEOUT_SECONDS=15
```

Se `ffprobe` não estiver disponível, o endpoint de upload responde 503 em vez de aceitar mídia sem inspeção.

## Ambientes

```text
ENVIRONMENT=development | test | staging | production
```

Staging/produção recusam:

- `DEBUG=true`;
- `SECRET_KEY` curta ou placeholder.

O bind padrão é `127.0.0.1`. Exposição em `0.0.0.0` ou outra interface precisa ser configurada explicitamente pelo ambiente/deployment.

## Testes e quality gates locais

Suíte:

```bash
pytest --cov=app --cov-fail-under=80 tests/
```

Lint:

```bash
ruff check app tests main.py
```

Tipos:

```bash
mypy app main.py
```

Migrations:

```bash
pytest -q tests/test_migrations.py
```

Segurança estática:

```bash
bandit -q -r app -ll
bandit -q main.py -ll
```

Dependências de runtime:

```bash
pip-audit -r requirements.txt
```

Os workflows `CI` e `Quality` executam esses gates automaticamente conforme a governança.

## Atualização de schema

Fluxo:

```bash
alembic revision --autogenerate -m "descricao"
# revisar a migration manualmente
alembic upgrade head
```

Migrations destrutivas exigem backup e plano de rollback antes de deployment.

## Logs

O projeto possui logging local com console/arquivo. Logging centralizado, métricas, traces e alertas ainda não são uma solução operacional de produção.

## Checklist antes de um futuro staging público

- [ ] autenticação/autorização implementadas;
- [ ] PostgreSQL decidido/configurado;
- [ ] storage persistente definido;
- [ ] worker/jobs persistentes operacionais;
- [ ] reverse proxy + HTTPS;
- [ ] limite de upload no edge;
- [ ] secrets gerenciadas fora do repositório;
- [ ] backup/restore testados;
- [ ] readiness e observabilidade;
- [ ] políticas de retenção/LGPD;
- [ ] CI + Quality verdes;
- [ ] migrations aplicadas e verificadas;
- [ ] plano de rollback.

---

**Status:** Active — development/integration only  
**Last Updated:** 2026-08-16
