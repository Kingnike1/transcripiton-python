# Arquitetura atual do AMIP

## Visão

O AMIP é um **monólito modular em camadas** com dois processos operacionais: web e worker. Ambos compartilham banco e storage; processamento pesado não roda dentro do request HTTP.

```text
Client
  ↓ HTTP
FastAPI
  ↓
Application Services
  ↓
SqlAlchemyUnitOfWork
  ↓
Repositories
  ↓
Database

FastAPI ── cria/consulta ──> ProcessingJob
                              ↓
                         database queue
                              ↓ claim/lease
                         Worker separado
                              ↓
                     handler por JobType
                              ↓
                   providers / storage
```

Redis, Celery, microservices e Kubernetes continuam fora do desenho atual até existir necessidade comprovada.

## Estado real

| Área | Estado |
|---|---|
| CRUD de reuniões | Implementado |
| Upload de áudio | Implementado com streaming/staging |
| Inspeção de mídia | Implementada com `ffprobe` |
| Storage local | Implementado |
| Unit of Work | Implementada |
| Alembic | Implementado |
| Um áudio ativo por reunião | Garantido pelo banco |
| Erros/request ID | Implementados |
| Lifecycle/configuração | Implementados |
| CI + Quality | Implementados |
| Jobs persistentes | Implementados — Sprint 6B |
| Worker separado | Implementado — Sprint 6B |
| Transcrição real | **Não implementada** |
| Diarização | **Não implementada** |
| Análise por LLM | **Não implementada** |
| UI de uso completa | **Não implementada** |
| Autenticação/autorização | **Não implementada** |

## Transações

Application Services possuem as fronteiras transacionais por `SqlAlchemyUnitOfWork`. Repositories fazem query/add/update/flush e nunca `commit()`/`rollback()`.

## Jobs persistentes

`ProcessingJob` é a unidade durável de trabalho assíncrono.

Estados:

```text
PENDING
  ↓ claim
RUNNING
  ├── sucesso → COMPLETED
  ├── falha recuperável → RETRYING → RUNNING
  └── tentativas esgotadas → FAILED

PENDING/RETRYING → CANCELLED
```

### Concorrência e recuperação

- um índice único parcial impede mais de um job ativo do mesmo tipo para a mesma reunião;
- criação é idempotente enquanto existe job ativo;
- claim usa atualização condicional, não lock Python em memória;
- `locked_by`, `locked_at` e `heartbeat_at` representam ownership/lease;
- job `RUNNING` com heartbeat stale pode ser recuperado por outro worker;
- `attempt`, `max_attempts` e `available_at` controlam retry;
- worker só reclama `JobType` para o qual possui handler registrado.

### Limite atual

SQLite + polling no banco é intencional para uso pessoal/local e baixa concorrência. Uma fila especializada só será considerada quando houver throughput ou contenção que justifiquem o custo operacional.

## Worker

O processo separado é iniciado por:

```bash
python worker.py
```

`app/workers/registry.py` é o composition root dos handlers. Na conclusão da Sprint 6B ele não registra transcritor real; a Sprint 7 conectará o primeiro handler `TRANSCRIBE`.

## Schema e migrations

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
  ↓
0004_processing_jobs
```

Migrations continuam externas ao processo web: `alembic upgrade head` antes de iniciar web/worker.

## Quality gates

- Python 3.11: suíte completa + cobertura >=80%;
- Python 3.12: compatibilidade;
- Ruff;
- mypy;
- migration integrity;
- Bandit;
- `pip-audit`.

## Próxima fronteira arquitetural

**Sprint 7 — primeira transcrição real**: escolher um único provider, persistir segmentos e registrar o handler `TRANSCRIBE` no worker.

## ADRs relacionados

- ADR-017 — ownership transacional;
- ADR-018 — Alembic baseline;
- ADR-019 — streaming/staging de áudio;
- ADR-020 — um áudio ativo por reunião;
- ADR-021 — contrato público de erros;
- ADR-022 — lifecycle/configuração;
- ADR-023 — quality gates/dependências;
- ADR-024 — taxonomia documental;
- ADR-025 — jobs duráveis e worker separado.

---

**Status:** Active  
**Last Updated:** 2026-08-16
