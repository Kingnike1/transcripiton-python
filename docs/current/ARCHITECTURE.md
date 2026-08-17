# Arquitetura atual do AMIP

## Visão

O AMIP é um **monólito modular em camadas** com dois processos operacionais: web e worker. Ambos compartilham banco e storage; processamento pesado não roda dentro do request HTTP.

```text
Client
  ↓ HTTP
FastAPI / Jinja2 UI
  ↓
Application Services
  ↓
SQLAlchemy / Repositories
  ↓
Database

FastAPI ── cria/consulta ──> ProcessingJob
                              ↓
                         database queue
                              ↓ claim/lease
                         Worker separado
                              ↓
              TRANSCRIBE / DIARIZE handlers
                              ↓
             faster-whisper / pyannote.audio
```

## Estado real

| Área | Estado |
|---|---|
| CRUD de reuniões | Implementado |
| Upload/inspeção de áudio | Implementado |
| Jobs persistentes/worker | Implementado |
| Transcrição real | Implementada com `faster-whisper` |
| Interface de reunião | Implementada |
| Diarização | Implementada com `pyannote.audio` quando configurado |
| Identificação de participantes | Implementada — Stack 11 |
| Empacotamento Docker local | Implementado |
| Análise por LLM | Não implementada |
| Autenticação/autorização | Não implementada |

## Pipeline atual

```text
Meeting
  ↓ upload
Audio
  ↓ TRANSCRIBE
Transcription + TranscriptionSegment
  ↓ DIARIZE
SpeakerSegment (SPEAKER_XX)
  ↓ confirmação humana
Participant (display_name + confirmed)
  ↓ próxima etapa
LLM intelligence (Stack 12)
```

## Identidade de participantes

A Stack 11 separa o dado bruto da diarização da identidade humana. `SpeakerSegment` continua registrando `speaker_label`; `Participant` pertence à reunião e guarda o nome editável/confirmado para aquele rótulo.

Essa separação permite corrigir nomes sem reprocessar áudio e prepara a Stack 12 para atribuir decisões e action items a participantes confirmados. Não existe reconhecimento biométrico global entre reuniões.

## Jobs e concorrência

`ProcessingJob` mantém estado, progresso, tentativas e lease. O worker executa STT e diarização fora do processo web. SQLite + polling continua intencional para uso pessoal/local e baixa concorrência.

## Schema e migrations

A cadeia atual termina em `0007_participant_identities`. Migrations são executadas externamente com `alembic upgrade head` antes de web/worker.

## Quality gates

- Python 3.11: suíte completa + cobertura >=80%;
- Python 3.12;
- Ruff;
- mypy;
- migration integrity;
- Bandit;
- `pip-audit`;
- validação Docker/Compose.

## Próxima fronteira arquitetural

**Stack 12 — Inteligência por LLM**: produzir resumo estruturado, decisões, action items, riscos e follow-ups com rastreabilidade para a transcrição e participantes.

## ADRs relacionados

ADRs 017–025 cobrem fundação, migrations, upload, segurança, quality, documentação e jobs. A Stack 11 adiciona **ADR-026 — participant identity layer**.

---

**Status:** Active  
**Last Updated:** 2026-08-17
