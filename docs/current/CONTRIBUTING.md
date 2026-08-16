# Contribuindo com o AMIP

Este documento resume o fluxo operacional. As regras obrigatórias completas estão em [`../../PROJECT_GOVERNANCE.md`](../../PROJECT_GOVERNANCE.md).

## Pré-requisitos

- Python 3.11 ou 3.12;
- Git;
- ambiente virtual;
- `ffprobe` para testes manuais de upload real.

## Setup

```bash
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python
python -m venv .venv
```

Ative a venv e instale:

```bash
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
```

## Branches

O projeto usa GitFlow adaptado:

```text
main      → release estável
develop   → integração
agent/stack-* → Stack de trabalho
fix/*
hotfix/*
release/*
```

Uma nova Stack normalmente nasce da `develop` verde:

```bash
git checkout develop
git pull
git checkout -b agent/stack-nome
```

## Commits

Conventional Commits:

```text
feat: add persistent job model
fix: honor stale job threshold
refactor: isolate worker transaction
test: cover interrupted job recovery
docs: update job architecture
chore: pin worker dependency
ci: add worker smoke gate
```

Mantenha commits pequenos, coerentes e reversíveis.

## Antes de programar

Leia obrigatoriamente:

- `PROJECT_CONTEXT.md`;
- `PROJECT_GOVERNANCE.md`;
- `PROJECT_STATE.MD`;
- `TECH_DECISIONS.md`;
- `docs/current/ARCHITECTURE.md`;
- `docs/current/DATABASE.md`;
- `docs/current/API.md`;
- `docs/06_BACKLOG.md`;
- ADRs relevantes.

Depois faça análise crítica de escopo, dependências, segurança, performance, concorrência, rollback e testes.

## Gates locais

### Testes

```bash
pytest --cov=app --cov-fail-under=80 tests/
```

### Ruff

```bash
ruff check app tests main.py
```

### mypy

```bash
mypy app main.py
```

### Migrations

```bash
pytest -q tests/test_migrations.py
```

### Bandit

```bash
bandit -q -r app -ll
bandit -q main.py -ll
```

### Dependências

```bash
pip-audit -r requirements.txt
```

## Mudanças de banco

Toda alteração de schema usa Alembic:

```bash
alembic revision --autogenerate -m "descricao"
```

Revise a migration manualmente e valide:

```bash
alembic upgrade head
pytest -q tests/test_migrations.py
```

Repositories não executam `commit()`/`rollback()`; a Service Layer controla a Unit of Work.

## Pull Request

PRs de Stack normalmente apontam para `develop`.

A descrição deve informar:

- objetivo;
- dependências;
- escopo entregue;
- fora de escopo;
- testes/gates;
- migrations;
- riscos residuais;
- documentação/ADR alterados.

Fluxo:

```text
develop
  ↓
agent/stack-...
  ↓
PR para develop
  ↓
CI + Quality
  ↓
merge
  ↓
CI + Quality pós-merge
```

## Definition of Done

Uma Stack só termina quando:

- código/escopo concluídos;
- testes relevantes verdes;
- CI + Quality verdes;
- migrations válidas;
- segurança revisada;
- documentação sincronizada;
- `PROJECT_STATE.MD`, backlog e decisões atualizados;
- PR mergeado na branch correta;
- pós-merge verde.

## Documentação

Use as categorias corretas:

- `docs/current/` — somente implementação atual;
- `docs/roadmap/` — planos futuros;
- `docs/archive/` — histórico/superseded;
- `docs/adr/` — decisões arquiteturais;
- `docs/06_BACKLOG.md` — fila operacional.

Não documente endpoint ou funcionalidade futura como se já existisse.

## Segurança

- não commitar `.env`, tokens, secrets ou credenciais;
- não expor detalhes internos em respostas HTTP;
- não adicionar dependência ao runtime sem uso real;
- `pip-audit` precisa permanecer verde;
- uploads e mudanças de persistência exigem análise de concorrência/limites;
- exposição pública exige autenticação/autorização e demais controles previstos no backlog.

---

**Status:** Active  
**Last Updated:** 2026-08-16
