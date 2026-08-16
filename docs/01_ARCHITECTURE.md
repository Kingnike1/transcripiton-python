# Arquitetura do Sistema

## Visão atual

O AMIP é um **monólito modular em camadas**. A base de código continua única, com separação explícita entre HTTP, casos de uso, persistência, storage e providers externos.

```text
Client
  ↓ HTTP
FastAPI
  ├── request ID middleware
  ├── error boundary
  ├── lifespan de recursos
  └── routes
        ↓
Application Services
        ↓
SqlAlchemyUnitOfWork
        ↓
Repositories
        ↓
SQLAlchemy / Database

Application Services
  ↓
Storage / ffprobe / providers futuros
```

Microservices, Redis, Celery e Kubernetes continuam fora do desenho atual até existir necessidade comprovada.

## Estado real dos módulos

| Área | Estado |
|---|---|
| API CRUD de reuniões | Implementada |
| Upload de áudio | Implementado com streaming/staging |
| Inspeção de áudio | Implementada com `ffprobe` |
| Storage local | Implementado |
| Unit of Work | Implementada — P0.1 |
| Alembic | Implementado — P0.2 |
| Um áudio ativo por reunião | Implementado — P0.4 |
| Contrato seguro de erros | Implementado — P0.5 |
| Lifecycle/configuração segura | Implementado na P0.6 |
| Jobs persistentes | Não implementados |
| Transcrição real | Não implementada |
| Diarização | Não implementada |
| Análise por LLM | Não implementada |
| Autenticação/autorização | Não implementada |

---

# Camadas e responsabilidades

## API Layer

- protocolo HTTP e Pydantic;
- dependency injection;
- tradução de erros conhecidos;
- sem SQL ou transações de domínio;
- upload grande não deve ser materializado em memória.

## Application Service Layer

- casos de uso;
- fronteiras transacionais;
- coordenação de repositories;
- compensação explícita para efeitos externos não ACID.

## Repository Layer

Repositories são transaction-neutral:

```text
query / add / update / flush
```

Não executam `commit()` ou `rollback()`.

---

# P0.1 — Ownership transacional

```text
Application Service
  ↓
SqlAlchemyUnitOfWork.transaction()
  ├── sucesso → commit
  └── exceção → rollback
        ↓
Repositories
```

---

# P0.2–P0.4 — Schema e integridade

Alembic é a fonte oficial de evolução do schema.

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
```

A `0003` garante no máximo um áudio ativo por reunião por índice único parcial. Soft-deleted permanece como histórico.

---

# P0.3 — Pipeline de upload

```text
POST /api/meetings/{meeting_id}/audio
  ↓
UploadFile.file
  ↓ threadpool
AudioUploadStager (chunks)
  ↓
AudioValidator
  ↓
FFprobeAudioInspector
  ↓
os.replace
  ↓
Storage final
  ↓
SqlAlchemyUnitOfWork
```

O limite é aplicado durante a escrita, temporários são limpos em erro e falha de banco antes do commit confirmado compensa o arquivo final.

---

# P0.5 — Error boundary

Toda requisição recebe `request_id`. Erros públicos usam somente:

```json
{
  "status": "error",
  "code": "INTERNAL_ERROR",
  "detail": "An unexpected error occurred",
  "request_id": "<uuid>"
}
```

SQL, paths, credenciais, stack traces e detalhes internos permanecem apenas nos logs.

---

# P0.6 — Lifecycle e configuração

## Startup/shutdown

O processo web não altera o schema.

```text
Deployment
  ↓
alembic upgrade head
  ↓
FastAPI startup
  ↓
requests
  ↓
FastAPI shutdown
  ↓
engine.dispose()
```

O lifespan serve somente para lifecycle de recursos. Não executa `create_all()` nem migrations.

`reset_db()` é uma ferramenta explícita restrita a desenvolvimento/testes.

## Settings

Todos os módulos herdam de `AMIPBaseSettings` e usam `SettingsConfigDict`.

```text
ENVIRONMENT = development | test | staging | production
```

Staging/produção falham cedo quando:

- `DEBUG=true`;
- `SECRET_KEY` é curta ou placeholder.

## Tempo

`app.core.time.utc_now()` é o relógio comum. O backend produz timestamps em UTC e não usa mais `datetime.utcnow()` nos models legados.

SQLite continua usando colunas `DateTime` existentes; não foi criada migration cosmética para `timezone=True`, pois SQLite não garante preservação de `tzinfo`. Esse ponto será revisto com PostgreSQL.

`get_stale_processing(minutes)` agora respeita o limiar solicitado e usa `ProcessingStatus`.

---

# CI e integração

P0.1–P0.5 foram integradas em `develop`. O head integrado passou no CI com 114 testes e 87,04% de cobertura.

O workflow atual cobre:

- `main`;
- `develop`;
- `agent/**`;
- PRs para `main` e `develop`;
- execução manual por `workflow_dispatch`.

P0.7 ainda deverá acrescentar lint, type checking, auditoria de dependências, segurança e proteção da `main`.

---

# Regras de evolução

1. Não colocar SQL em routes.
2. Não colocar `commit()` em repositories.
3. Toda mudança de schema usa Alembic.
4. Migrations não rodam automaticamente no processo web.
5. Processamento pesado não roda no request HTTP.
6. Upload grande não deve ser materializado em memória.
7. Não integrar Whisper antes de jobs persistentes.
8. Erros públicos não expõem detalhes internos.
9. Configuração de staging/produção deve falhar fechada quando insegura.
10. Documentação ativa descreve apenas funcionalidades realmente implementadas.

## ADRs relacionados

- ADR-017 — ownership transacional;
- ADR-018 — baseline Alembic;
- ADR-019 — streaming/staging de áudio;
- ADR-020 — um áudio ativo por reunião;
- ADR-021 — contrato público de erros;
- ADR-022 — lifecycle e configuração de runtime.

## Próxima evolução

Depois da P0.6: **P0.7 — Qualidade e governança**, P0.8 documental e então Sprint 6B — Jobs persistentes.

---

**Document Version:** 1.4  
**Last Updated:** 2026-08-16  
**Status:** Active
