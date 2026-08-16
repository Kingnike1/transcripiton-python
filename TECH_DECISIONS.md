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
| TD-021 | Lifecycle não altera schema; runtime é validado por ambiente | Accepted |
| TD-022 | CI/Quality bloqueiam regressões e runtime mantém superfície mínima | Accepted |

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

**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-020-one-active-audio-per-meeting.md`

Uma reunião pode possuir no máximo um `Audio` com `deleted_at IS NULL`. O índice único parcial `uq_audios_active_meeting` é a autoridade final contra concorrência; o pre-check do service continua como otimização. A migration recusa dados legados conflitantes sem apagá-los automaticamente.

Idempotência HTTP global continua adiada até existir identidade/tenant. A Sprint 6B tratará idempotência de jobs.

---

## TD-020 — Erros públicos são sanitizados e correlacionados por request ID

**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-021-public-error-contract.md`

Toda resposta de erro normalizada contém `status`, `code`, `detail` e `request_id`; `X-Request-ID` acompanha a resposta. Detalhes técnicos permanecem apenas nos logs. `AudioResponse` não expõe `file_path`.

---

## TD-021 — Lifecycle não altera schema; runtime é validado por ambiente

**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-022-lifecycle-runtime-configuration.md`

- o processo web não cria schema nem executa migrations;
- Alembic é aplicado explicitamente antes do app;
- FastAPI lifespan gerencia recursos e descarta o engine no shutdown;
- `reset_db()` é restrito a development/test;
- settings usam Pydantic V2;
- staging/produção rejeitam debug e segredo fraco;
- `utc_now()` é o relógio comum;
- `get_stale_processing(minutes)` respeita o limiar.

---

## TD-022 — CI/Quality bloqueiam regressões e runtime mantém superfície mínima

**Status:** Accepted  
**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-023-quality-gates-runtime-dependencies.md`

### Decisão

- Python 3.11 é a baseline mínima e Python 3.12 é compatibilidade obrigatória no CI;
- `CI` executa a suíte completa com cobertura >=80%;
- `Quality` executa Ruff (`F`/`E9`), mypy, migrations, Bandit e `pip-audit`;
- todos esses checks são bloqueantes;
- `actions/checkout` e `actions/setup-python` usam v6;
- `requirements.txt` contém apenas runtime ativo;
- testes/scanners ficam em `requirements-dev.txt`;
- bibliotecas de exportação não implementadas saem do runtime e retornam apenas quando a Stack correspondente existir;
- upgrades de segurança são direcionados e sempre passam por regressão completa;
- o bind padrão é `127.0.0.1`, exigindo configuração explícita para exposição externa;
- GitFlow adaptado e Conventional Commits são a política oficial.

### Evidência de segurança

A primeira auditoria encontrou 27 advisories em 7 pacotes. Após separar dependências e atualizar o núcleo HTTP/configuração, `pip-audit -r requirements.txt` retornou **No known vulnerabilities found**.

### Limitação administrativa

A proteção da `main` continua desejada, mas a integração GitHub disponível respondeu 403 ao endpoint de branch protection e não expõe ação autorizada para configurar rulesets. Portanto essa proteção permanece como controle administrativo externo pendente e **não deve ser descrita como ativa**.

---

**Document Version:** 1.7  
**Last Updated:** 2026-08-16  
**Status:** Active
