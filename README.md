# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para receber áudio de reuniões e, progressivamente, transformá-lo em transcrição e inteligência estruturada.

> **Estado atual:** o backend de reuniões/upload está funcional e a fundação técnica foi estabilizada. Jobs persistentes, transcrição real, diarização e análise por LLM ainda não estão implementados.

## O que funciona hoje

- CRUD de reuniões via API;
- upload de áudio por reunião;
- streaming/chunks com staging temporário;
- validação de arquivo e inspeção por `ffprobe`;
- persistência de metadados técnicos do áudio;
- Unit of Work e transações no Service Layer;
- migrations Alembic;
- proteção contra dois áudios ativos na mesma reunião;
- erros públicos sanitizados + `X-Request-ID`;
- lifecycle/configuração seguros;
- CI/Quality em Python 3.11 e 3.12;
- Ruff, mypy, migration checks, Bandit e `pip-audit` bloqueantes.

## Ainda não implementado

- jobs persistentes e worker recuperável;
- Whisper/provider real de transcrição;
- diarização;
- LLM/resumos/action items;
- UI completa de reuniões/processamento;
- autenticação/autorização;
- busca/exportação;
- deployment público production-ready.

## Arquitetura

```text
FastAPI
  ↓
Application Services
  ↓
SqlAlchemyUnitOfWork
  ↓
Repositories
  ↓
SQLAlchemy / SQLite

Services
  ↓
Storage local / ffprobe / providers futuros
```

O projeto permanece um **monólito modular**. A próxima evolução arquitetural é um worker separado com jobs persistidos, não microservices.

## Setup local

### Pré-requisitos

- Python 3.11 ou 3.12;
- Git;
- `ffprobe` disponível para upload real de áudio.

### Instalação

```bash
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python

python -m venv .venv
```

Ative o ambiente virtual e instale:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Configure:

```bash
cp .env.example .env
```

Crie/atualize o banco:

```bash
alembic upgrade head
```

Execute:

```bash
uvicorn main:app --reload
```

Aplicação:

```text
http://127.0.0.1:8000
```

OpenAPI:

```text
http://127.0.0.1:8000/docs
```

## Testes e quality

```bash
pytest --cov=app --cov-fail-under=80 tests/
ruff check app tests main.py
mypy app main.py
pytest -q tests/test_migrations.py
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
```

Os workflows `CI` e `Quality` executam esses gates automaticamente.

## Fluxo Git

```text
main      → release estável
develop   → integração
agent/stack-* → trabalho por Stack
```

Commits seguem Conventional Commits. As regras completas estão em [`PROJECT_GOVERNANCE.md`](PROJECT_GOVERNANCE.md).

## Documentação

Comece por [`docs/README.md`](docs/README.md).

### Estado atual

- [Arquitetura](docs/current/ARCHITECTURE.md)
- [Banco](docs/current/DATABASE.md)
- [API](docs/current/API.md)
- [Execução/deployment atual](docs/current/DEPLOYMENT.md)
- [Contribuição](docs/current/CONTRIBUTING.md)

### Planejamento

- [Backlog](docs/06_BACKLOG.md)
- [Roadmap de frontend](docs/roadmap/FRONTEND.md)
- [Roadmap de IA](docs/roadmap/AI_PIPELINE.md)

### Governança e estado

- [Contexto](PROJECT_CONTEXT.md)
- [Governança](PROJECT_GOVERNANCE.md)
- [Estado atual](PROJECT_STATE.MD)
- [Decisões técnicas](TECH_DECISIONS.md)
- [ADRs](docs/adr/)

## Próxima etapa

Depois da organização documental P0.8, a prioridade técnica é **Sprint 6B — Jobs persistentes**, necessária antes da primeira transcrição real.

## Licença

MIT — consulte [`LICENSE`](LICENSE).
