# Technical Decisions Register

Este arquivo mantém o registro ativo das principais decisões técnicas do AMIP. ADRs dedicados ficam em `docs/adr/`.

## Decisões vigentes

| ID | Decisão | Status |
|---|---|---|
| TD-001 | Monólito modular em camadas | Accepted |
| TD-002 | FastAPI como framework HTTP | Accepted |
| TD-003 | SQLite local/testes; PostgreSQL futuro | Accepted |
| TD-004 | Jinja2 + HTMX antes de SPA | Accepted |
| TD-005 | Bootstrap 5 | Accepted |
| TD-006 | Whisper como direção inicial de STT | Accepted |
| TD-007 | pyannote como direção inicial de diarização | Accepted, futuro |
| TD-008 | Repository Pattern | Accepted |
| TD-009 | Service Layer | Accepted |
| TD-010 | Interfaces para providers de IA | Accepted |
| TD-011 | BackgroundTasks/fila em memória | **Superseded por TD-024** |
| TD-012 | Storage local no MVP | Accepted |
| TD-013 | Arquitetura preparada para múltiplos providers | Accepted |
| TD-014 | KISS e YAGNI | Accepted |
| TD-015 | Desenvolvimento incremental por stacks | Accepted |
| TD-016 | Service Layer é proprietária das transações | Accepted |
| TD-017 | Alembic é a fonte oficial de evolução do schema | Accepted |
| TD-018 | Upload usa staging em chunks e ffprobe | Accepted |
| TD-019 | Uma reunião possui no máximo um áudio ativo | Accepted |
| TD-020 | Erros públicos são sanitizados/request ID | Accepted |
| TD-021 | Lifecycle não altera schema; runtime validado | Accepted |
| TD-022 | CI/Quality bloqueiam regressões | Accepted |
| TD-023 | Documentação separa current/roadmap/archive | Accepted |
| TD-024 | Banco é a fila durável inicial; worker é processo separado | Accepted |
| TD-025 | `faster-whisper` é o provider STT inicial local, isolado no worker | Accepted |

## TD-016 — Ownership transacional

**ADR:** `docs/adr/ADR-017-service-layer-transaction-ownership.md`

Repositories usam query/add/flush. `SqlAlchemyUnitOfWork` coordena commit/rollback no Service Layer.

## TD-017 — Alembic

**ADR:** `docs/adr/ADR-018-alembic-schema-baseline.md`

Alembic é a fonte oficial do schema e migrations são externas ao processo web.

## TD-018 — Upload streaming

**ADR:** `docs/adr/ADR-019-streaming-audio-staging.md`

Upload usa chunks, staging, validação, `ffprobe` e promoção atômica.

## TD-019 — Um áudio ativo

**ADR:** `docs/adr/ADR-020-one-active-audio-per-meeting.md`

Índice único parcial é a defesa final contra concorrência.

## TD-020 — Contrato de erro público

**ADR:** `docs/adr/ADR-021-public-error-contract.md`

Erros públicos são sanitizados e correlacionados por request ID; paths/SQL/secrets ficam internos.

## TD-021 — Lifecycle/configuração

**ADR:** `docs/adr/ADR-022-lifecycle-runtime-configuration.md`

Web não cria schema; settings de ambientes não locais falham fechadas quando inseguras; UTC é o relógio comum.

## TD-022 — Quality gates

**ADR:** `docs/adr/ADR-023-quality-gates-runtime-dependencies.md`

Python 3.11/3.12, pytest/cobertura, Ruff, mypy, migration integrity, Bandit e `pip-audit` são gates. Runtime contém somente dependências ativas.

## TD-023 — Taxonomia documental

**ADR:** `docs/adr/ADR-024-documentation-taxonomy.md`

`docs/current/` é comportamento real; `roadmap/` é planejado; `archive/` é histórico; código/migrations/testes/CI têm autoridade superior.

## TD-024 — Banco como fila durável inicial

**Status:** Accepted  
**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-025-durable-database-jobs-worker.md`

### Decisão

- `ProcessingJob` persiste estado/progresso/tentativas/payload/result/erro;
- índice parcial impede job ativo duplicado por reunião/tipo;
- criação é idempotente enquanto um job ativo existe;
- worker separado do FastAPI reclama jobs por update condicionado;
- lease/heartbeat permitem recuperação de job abandonado;
- retry usa `available_at` e `max_attempts`;
- worker só reclama tipos com handler registrado;
- SQLite/database polling é suficiente para o estágio pessoal/local.

### Alternativas adiadas

Redis, Celery, RQ e Dramatiq só serão considerados com evidência de throughput/contenção que justifique infraestrutura adicional.

### Supersession

TD-011 (BackgroundTasks/fila em memória) está superseded. A implementação antiga e seus testes foram removidos na Sprint 6B.

## TD-025 — Provider STT inicial local

**Status:** Accepted  
**Data:** 2026-08-16

### Decisão

- usar `faster-whisper` como primeira implementação concreta de `ITranscriber`;
- manter o provider fora do processo web e executá-lo pelo worker durável;
- usar por padrão modelo `base`, `device=cpu`, `compute_type=int8` e VAD ligado;
- permitir idioma automático ou fixo por configuração;
- persistir o resultado em `Transcription` + `TranscriptionSegment`;
- manter a dependência pesada em `requirements-worker.txt`;
- CI testa o contrato por fakes e não baixa/carrega modelo real.

### Motivo

Essa escolha entrega uma transcrição local real com custo operacional baixo e mantém o domínio desacoplado da biblioteca específica. A interface `ITranscriber` permite trocar modelo/provider posteriormente sem reescrever o pipeline de jobs ou persistência.

### Alternativas adiadas

APIs externas de STT e modelos maiores poderão ser avaliados quando houver requisito de qualidade, latência, hardware ou escala que justifique custo/complexidade adicionais.

---

**Document Version:** 2.0  
**Last Updated:** 2026-08-16  
**Status:** Active
