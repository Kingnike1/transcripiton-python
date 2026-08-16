# Banco de dados atual

## Estratégia

- SQLAlchemy 2.x;
- SQLite para uso local/testes;
- PostgreSQL planejado quando houver uso multiusuário relevante;
- Alembic como fonte oficial do schema;
- Service Layer dona das transações;
- UTC como semântica temporal.

## Schema atual

```text
meetings
  ├── audios
  │     └── transcriptions
  │            └── speaker_segments
  ├── meeting_analysis (1:1)
  └── processing_jobs
```

Modelos de transcrição/diarização/análise ainda não representam providers operacionais.

## Áudio

`0002_audio_media_metadata` adicionou codec/canais/sample rate. `0003_one_active_audio_per_meeting` garante no máximo um áudio com `deleted_at IS NULL` por reunião.

## ProcessingJob — Sprint 6B

A migration `0004_processing_jobs` adiciona trabalho assíncrono durável.

Campos operacionais principais:

- `id`, `meeting_id`, `job_type`, `status`;
- `progress`, `attempt`, `max_attempts`;
- `payload`, `result`, `error_message`;
- `available_at`;
- `locked_by`, `locked_at`, `heartbeat_at`;
- `created_at`, `updated_at`, `started_at`, `completed_at`.

Índices:

```text
ix_processing_jobs_status_available
(status, available_at, created_at)

uq_processing_jobs_active_meeting_type
UNIQUE (meeting_id, job_type)
WHERE status IN ('PENDING', 'RUNNING', 'RETRYING')
```

A constraint é a última defesa contra duas criações concorrentes do mesmo job ativo.

## Claim/lease

O worker procura job disponível e tenta um update condicionado ao estado observado. `RUNNING` só pode ser recuperado quando o heartbeat do lease está stale. Isso evita depender de locks em memória e permite recuperação depois de restart/crash.

## Cadeia de migrations

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
  ↓
0004_processing_jobs
```

Banco novo:

```bash
alembic upgrade head
```

Banco legado na baseline:

```bash
alembic stamp 0001_initial_schema
alembic upgrade head
```

`stamp` somente registra schema comprovadamente equivalente; não corrige drift.

## Lifecycle

Web e worker não criam/migram schema automaticamente. Deployment executa migrations explicitamente antes dos processos.

## Gates

`tests/test_migrations.py` valida banco vazio, drift, baseline legada, downgrade, integridade do áudio e a constraint de job ativo. O workflow Quality executa migration integrity como gate bloqueante.

## Evolução seguinte

Sprint 7 adicionará persistência de segmentos de transcrição. PostgreSQL permanece adiado enquanto o uso for pessoal/local e a concorrência baixa.

---

**Status:** Active  
**Last Updated:** 2026-08-16
