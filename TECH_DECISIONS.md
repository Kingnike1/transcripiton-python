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
| TD-020 | Erros públicos são sanitizados e correlacionados por request ID | Accepted |

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

Uma reunião pode possuir no máximo um `Audio` com `deleted_at IS NULL`. O índice único parcial `uq_audios_active_meeting` é a autoridade final contra concorrência; o pre-check do service continua como otimização. A migration recusa dados legados conflitantes sem apagá-los automaticamente.

Idempotência HTTP global continua adiada até existir identidade/tenant. A Sprint 6B tratará idempotência de jobs.

---

## TD-020 — Erros públicos são sanitizados e correlacionados por request ID

**Status:** Accepted  
**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-021-public-error-contract.md`

### Contexto

Os handlers anteriores devolviam `exc.details` ao cliente e o erro genérico retornava `str(exc)`. Isso podia revelar SQL, caminhos locais, credenciais ou detalhes de SDK/infraestrutura. O contrato de áudio também expunha `file_path`.

### Decisão

- toda resposta de erro normalizada contém `status`, `code`, `detail` e `request_id`;
- o servidor gera o `request_id` e também o envia em `X-Request-ID`;
- `str(exc)`, stack traces e `exc.details` nunca são enviados em respostas 5xx;
- detalhes técnicos e traceback permanecem nos logs internos associados ao mesmo `request_id`;
- `HTTPException` e `RequestValidationError` passam pelo mesmo envelope;
- `file_path` é removido de `AudioResponse` e permanece detalhe interno de storage;
- mensagens de validação de upload podem ser públicas somente quando representarem feedback seguro sobre a entrada do usuário.

### Consequências

A API ganha um contrato de erro rastreável sem expor infraestrutura. Suporte e observabilidade devem usar `request_id` para correlacionar resposta e logs. Novos endpoints devem reutilizar esse envelope em vez de criar formatos próprios.

---

**Document Version:** 1.5  
**Last Updated:** 2026-08-16  
**Status:** Active
