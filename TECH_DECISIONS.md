# Technical Decisions Register

Este arquivo mantém o registro ativo das principais decisões técnicas do AMIP. ADRs dedicados ficam em `docs/adr/`.

## Decisões vigentes

| ID | Decisão | Status |
|---|---|---|
| TD-001 | Monólito modular em camadas | Accepted |
| TD-002 | FastAPI como framework HTTP | Accepted |
| TD-003 | SQLite local/testes; PostgreSQL futuro | Accepted |
| TD-004 | Jinja2 + HTMX/JavaScript mínimo antes de SPA | Accepted |
| TD-005 | Bootstrap 5 | Accepted |
| TD-006 | Whisper como direção inicial de STT | Accepted |
| TD-007 | pyannote como direção inicial de diarização | Accepted |
| TD-008 | Repository Pattern | Accepted |
| TD-009 | Service Layer | Accepted |
| TD-010 | Interfaces para providers de IA | Accepted |
| TD-011 | BackgroundTasks/fila em memória | Superseded por TD-024 |
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
| TD-025 | `faster-whisper` é o provider STT inicial local | Accepted |
| TD-026 | Identidade humana é separada dos speaker segments | Accepted |

## TD-016 — Ownership transacional

Repositories fazem query/add/flush. `SqlAlchemyUnitOfWork` coordena commit/rollback no Service Layer. ADR-017.

## TD-017 — Alembic

Alembic é a fonte oficial do schema e migrations são externas ao processo web. ADR-018.

## TD-018 — Upload streaming

Upload usa chunks, staging, validação, `ffprobe` e promoção atômica. ADR-019.

## TD-019 — Um áudio ativo

Índice único parcial é a defesa final contra concorrência. ADR-020.

## TD-020 — Contrato de erro público

Erros públicos são sanitizados e correlacionados por request ID. ADR-021.

## TD-021 — Lifecycle/configuração

Web não cria schema; ambientes não locais falham fechados quando inseguros; UTC é o relógio comum. ADR-022.

## TD-022 — Quality gates

Python 3.11/3.12, pytest/cobertura, Ruff, mypy, migration integrity, Bandit e `pip-audit` são gates. ADR-023.

## TD-023 — Taxonomia documental

`docs/current/` é comportamento real; `roadmap/` é planejado; `archive/` é histórico. ADR-024.

## TD-024 — Banco como fila durável inicial

`ProcessingJob` persiste estado/progresso/tentativas; worker separado usa claim/lease/heartbeat/retry. SQLite/database polling é suficiente para o estágio atual. ADR-025.

## TD-025 — Provider STT inicial local

`faster-whisper` implementa `ITranscriber`, roda somente no worker e persiste `Transcription` + `TranscriptionSegment`. O CI usa fakes e não baixa modelo real.

## TD-026 — Participant identity layer

**Status:** Accepted  
**Data:** 2026-08-17  
**ADR:** `docs/adr/ADR-026-participant-identity-layer.md`

### Decisão

- `SpeakerSegment` continua sendo o dado temporal bruto da diarização;
- `Participant` pertence à reunião e mapeia `speaker_label` para `display_name` + `confirmed`;
- `(meeting_id, speaker_label)` é único;
- novas diarizações criam placeholders automaticamente;
- a migration `0007_participant_identities` faz backfill das diarizações existentes;
- confirmação humana exige nome não vazio;
- não há reconhecimento biométrico global entre reuniões.

### Motivo

Separar rótulo técnico de identidade humana evita duplicação em cada segmento, permite correções sem reprocessar áudio e prepara a Stack 12 para atribuir decisões e action items a participantes confirmados.

---

**Document Version:** 3.0  
**Last Updated:** 2026-08-17  
**Status:** Active
