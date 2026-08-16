# PROJECT_CONTEXT.md

## Projeto

**AMIP — AI Meeting Intelligence Platform**

O AMIP é uma plataforma web para transformar áudio de reuniões em informação estruturada. A visão de produto inclui upload/gravação, transcrição, identificação de speakers, análise por IA, busca e exportação.

Este documento separa explicitamente **visão de produto** de **capacidade implementada**.

---

## Objetivo de produto

Fluxo desejado de longo prazo:

```text
Reunião
  ↓
Áudio
  ↓
Processamento persistente
  ↓
Transcrição
  ↓
Diarização
  ↓
Análise por IA
  ↓
Busca / tarefas / exportação
```

A visão não implica que todas essas etapas já estejam disponíveis.

---

## Capacidade atual

### Implementado

- FastAPI + Pydantic + SQLAlchemy;
- CRUD de reuniões pela API;
- upload multipart de áudio por reunião;
- upload em streaming/chunks com staging temporário;
- limite de tamanho durante escrita;
- validação de extensão/MIME/assinatura;
- inspeção de mídia com `ffprobe`;
- persistência de duração, codec, canais e sample rate;
- storage local com compensação em falha transacional;
- no máximo um áudio ativo por reunião, garantido pelo banco;
- Unit of Work e repositories transaction-neutral;
- Alembic com migrations versionadas;
- error boundary sanitizado + request ID;
- lifecycle sem criação automática de schema;
- configuração fail-closed para staging/produção;
- CI/Quality com Python 3.11/3.12, Ruff, mypy, migrations, Bandit e `pip-audit`;
- documentação OpenAPI do FastAPI.

### Existe como scaffold/protótipo, mas não como produto operacional

- interfaces de providers;
- `pipeline_service.py`;
- `processing_service.py`;
- fila/jobs em memória;
- models de transcrição, speaker segments e análise.

### Não implementado

- jobs persistentes/worker recuperável;
- provider real de transcrição;
- diarização real;
- análise por LLM;
- UI completa de reuniões/upload/transcrição;
- autenticação/autorização;
- busca avançada;
- exportação;
- PostgreSQL de staging/produção;
- object storage;
- deployment público production-ready.

---

## Arquitetura vigente

Monólito modular em camadas:

```text
FastAPI
  ↓
Application Services
  ↓
SqlAlchemyUnitOfWork
  ↓
Repositories
  ↓
SQLAlchemy / Database
```

Storage, `ffprobe` e providers externos são adapters coordenados pelos services.

A próxima fronteira arquitetural é separar o **processo web** do **worker**, mantendo a mesma base de código e persistindo jobs no banco. Isso não exige microservices.

---

## Stack atual

### Runtime

- Python 3.11 e 3.12 testados;
- FastAPI;
- Starlette;
- SQLAlchemy;
- Alembic;
- Pydantic 2 / pydantic-settings;
- Jinja2;
- Uvicorn;
- SQLite em desenvolvimento/testes;
- filesystem local;
- `ffprobe` como dependência operacional do upload.

### Desenvolvimento/qualidade

- pytest + pytest-cov;
- Ruff;
- mypy;
- Bandit;
- pip-audit;
- GitHub Actions.

### Frontend

A direção é Jinja2 + Bootstrap + HTMX/JavaScript mínimo. A UI completa ainda não foi implementada.

---

## Ordem de evolução vigente

```text
P0.8 — organização documental
  ↓
Sprint 6B — jobs persistentes + worker
  ↓
Transcrição real
  ↓
Vertical slice de UI
  ↓
Autenticação/produção
  ↓
Diarização
  ↓
LLM
  ↓
Busca/exportação
```

A ordem pode ser revisada conforme evidência técnica, mas Whisper/processamento pesado não deve ser integrado antes de jobs persistentes.

---

## Restrições e decisões importantes

- não usar microservices por antecipação;
- não colocar `commit()` em repositories;
- não rodar migrations automaticamente no processo web;
- não materializar uploads grandes em RAM;
- não expor detalhes internos em HTTP;
- não adicionar dependência ao runtime sem uso real;
- não declarar roadmap como funcionalidade entregue;
- PostgreSQL/Redis/Celery/Kubernetes entram apenas quando a necessidade justificar;
- `main` representa release estável; `develop` representa integração.

---

## Onde buscar a verdade

1. código/migrations/testes/CI;
2. `PROJECT_GOVERNANCE.md`;
3. `PROJECT_STATE.MD`;
4. `TECH_DECISIONS.md` + ADRs;
5. `docs/current/`;
6. `docs/06_BACKLOG.md` para planejamento;
7. `docs/roadmap/` apenas para futuro;
8. `docs/archive/` apenas para histórico.

---

**Document Version:** 2.0  
**Last Updated:** 2026-08-16  
**Status:** Active
