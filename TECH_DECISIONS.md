# Technical Decisions Register

Este arquivo mantém o registro ativo das principais decisões técnicas do AMIP. Decisões arquiteturais relevantes possuem ADR dedicado em `docs/adr/`; o histórico completo permanece preservado no Git.

## Decisões vigentes

| ID | Decisão | Status |
|---|---|---|
| TD-001 | Monólito modular em camadas | Accepted |
| TD-002 | FastAPI como framework HTTP | Accepted |
| TD-003 | SQLite local/testes; PostgreSQL futuro | Accepted |
| TD-004 | Jinja2 + HTMX antes de SPA | Accepted |
| TD-005 | Bootstrap 5 | Accepted |
| TD-006 | Whisper como direção inicial de STT | Accepted, sujeito a revisão |
| TD-007 | pyannote como direção inicial de diarização | Accepted, futuro |
| TD-008 | Repository Pattern | Accepted |
| TD-009 | Service Layer | Accepted |
| TD-010 | Interfaces para providers de IA | Accepted |
| TD-011 | BackgroundTasks/fila em memória | Deprecated — será superseded na Sprint 6B |
| TD-012 | Storage local no MVP | Accepted |
| TD-013 | Arquitetura preparada para múltiplos providers | Accepted |
| TD-014 | KISS e YAGNI | Accepted |
| TD-015 | Desenvolvimento incremental por stacks | Accepted |
| TD-016 | Service Layer é proprietária das transações | Accepted |
| TD-017 | Alembic é a fonte oficial de evolução do schema | Accepted |
| TD-018 | Upload usa staging em chunks e ffprobe | Accepted |
| TD-019 | Uma reunião possui no máximo um áudio ativo | Accepted |

---

## TD-016 — Service Layer é proprietária das transações

**Data:** 2026-08-06  
**ADR:** `docs/adr/ADR-017-service-layer-transaction-ownership.md`

Repositories usam query/add/flush e não executam `commit()` ou `rollback()`. `SqlAlchemyUnitOfWork` coordena a Session compartilhada pelo caso de uso.

---

## TD-017 — Alembic é a fonte oficial de evolução do schema

**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-018-alembic-schema-baseline.md`

Bancos novos usam `alembic upgrade head`. Bancos legados devem ser marcados na revision que realmente representam e avançados pelas revisions posteriores. Toda mudança de schema deve possuir migration revisada.

---

## TD-018 — Upload usa staging em chunks e ffprobe

**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-019-streaming-audio-staging.md`

`UploadFile.file` é processado via threadpool, escrito em chunks de 1 MiB em staging temporário, validado e inspecionado com `ffprobe`, depois promovido atomicamente. O limite é aplicado durante a escrita e falhas antes do commit acionam limpeza/compensação.

---

## TD-019 — Uma reunião possui no máximo um áudio ativo

**Status:** Accepted  
**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-020-one-active-audio-per-meeting.md`

### Contexto

O pre-check do `AudioService` evitava duplicidade no caminho comum, mas não era suficiente contra duas requisições concorrentes. Uma `UNIQUE(meeting_id)` simples também seria incompatível com o soft delete, pois impediria substituição futura.

### Decisão

- uma reunião pode ter no máximo um `Audio` com `deleted_at IS NULL`;
- o model e a migration `0003` usam o índice único parcial `uq_audios_active_meeting`;
- o pre-check do service permanece como otimização;
- a constraint do banco é a autoridade final contra races;
- conflito da constraint é traduzido para `AudioAlreadyExistsError`;
- outros `IntegrityError` não são mascarados;
- a migration se recusa a avançar quando já existem duplicidades ativas e nunca apaga dados automaticamente.

### Idempotência

Upload HTTP repetido após sucesso continua retornando conflito. `Idempotency-Key` global foi adiado porque ainda não existe identidade/tenant para escopo seguro. A Sprint 6B implementará idempotência dos jobs; idempotência HTTP completa será revisitada após autenticação/organizações.

### Consequências

A invariável deixa de depender exclusivamente do processo Python e passa a sobreviver a concorrência, múltiplos workers e futuras instâncias. Soft-deleted continua disponível como histórico e não impede um áudio substituto.

---

**Document Version:** 1.4  
**Last Updated:** 2026-08-16  
**Status:** Active
