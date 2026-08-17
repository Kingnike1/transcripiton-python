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
| TD-027 | Ollama/Qwen3 é o provider LLM local inicial com saída estruturada | Accepted |
| TD-028 | Sessão opaca + ownership de Meeting é a fronteira multiusuário inicial | Accepted |

## TD-024 — Banco como fila durável inicial

`ProcessingJob` persiste estado/progresso/tentativas; worker separado usa claim/lease/heartbeat/retry. SQLite/database polling é suficiente para o estágio atual. ADR-025.

## TD-025 — Provider STT inicial local

`faster-whisper` implementa `ITranscriber`, roda somente no worker e persiste `Transcription` + `TranscriptionSegment`.

## TD-026 — Participant identity layer

`Participant` pertence à reunião e mapeia `speaker_label` para `display_name` + `confirmed`. ADR-026.

## TD-027 — LLM local estruturado

Ollama é o primeiro adapter LLM; `qwen3:4b` é o baseline configurável; a saída é estruturada/validada e a análise roda em job `SUMMARIZE`. ADR-027.

## TD-028 — Authentication and resource ownership

**Status:** Accepted  
**Data:** 2026-08-17  
**ADR:** `docs/adr/ADR-028-authentication-and-resource-ownership.md`

### Decisão

- `User` representa uma conta;
- senha usa `hashlib.scrypt` com salt aleatório;
- sessão usa token opaco aleatório e revogável;
- somente SHA-256 do token de sessão é persistido;
- cookie é HttpOnly, SameSite=Lax e Secure fora do ambiente local;
- `Meeting.owner_id` é a raiz da autorização;
- recursos derivados herdam autorização da reunião-pai;
- acesso cruzado retorna 404;
- modo local sem contas continua disponível;
- a primeira conta assume reuniões legadas sem owner;
- JWT, OAuth/SSO, RBAC e MFA permanecem adiados até requisito real.

### Motivo

Esta solução entrega isolamento multiusuário, logout/revogação e proteção de credenciais com baixo custo operacional, sem Redis, IdP externo ou infraestrutura prematura. Ela também mantém workers desacoplados da sessão HTTP.

---

**Document Version:** 5.0  
**Last Updated:** 2026-08-17  
**Status:** Active
