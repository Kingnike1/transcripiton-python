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

## TD-024 — Banco como fila durável inicial

`ProcessingJob` persiste estado/progresso/tentativas; worker separado usa claim/lease/heartbeat/retry. SQLite/database polling é suficiente para o estágio atual. ADR-025.

## TD-025 — Provider STT inicial local

`faster-whisper` implementa `ITranscriber`, roda somente no worker e persiste `Transcription` + `TranscriptionSegment`. O CI usa fakes e não baixa modelo real.

## TD-026 — Participant identity layer

`Participant` pertence à reunião e mapeia `speaker_label` para `display_name` + `confirmed`, mantendo identidade humana separada de `SpeakerSegment`. ADR-026.

## TD-027 — LLM local estruturado

**Status:** Accepted  
**Data:** 2026-08-17  
**ADR:** `docs/adr/ADR-027-local-llm-structured-intelligence.md`

### Decisão

- Ollama é o primeiro adapter LLM;
- `qwen3:4b` é o baseline local configurável;
- jobs `SUMMARIZE` executam a análise fora do processo HTTP;
- a entrada inclui timestamps, speaker labels e participantes confirmados;
- a saída usa JSON Schema e é validada por Pydantic;
- resumo, action items, decisões, riscos e follow-ups são persistidos;
- itens podem carregar `owner` e evidências rastreáveis;
- provider e modelo usados são persistidos;
- providers pagos permanecem adapters futuros, não dependências do domínio.

### Motivo

Entrega inteligência útil sem cobrança obrigatória por token, mantém dados de reunião locais por padrão e reduz risco de hallucination ao exigir estrutura e evidências. O contrato permanece substituível quando houver necessidade de outro provider/modelo.

---

**Document Version:** 4.0  
**Last Updated:** 2026-08-17  
**Status:** Active
