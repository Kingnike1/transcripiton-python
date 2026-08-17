# Banco de dados atual

## Estratégia

- SQLAlchemy 2.x;
- SQLite para uso local/testes;
- PostgreSQL planejado quando houver necessidade real;
- Alembic como fonte oficial do schema;
- UTC como semântica temporal.

## Schema atual

```text
meetings
  ├── audios
  │     └── transcriptions
  │            ├── transcription_segments
  │            └── speaker_segments
  ├── participants
  ├── meeting_analysis (1:1)
  └── processing_jobs
```

## Participantes — Stack 11

`participants` representa a identidade humana associada a um rótulo de diarização dentro de uma reunião.

Campos principais:

- `meeting_id`;
- `speaker_label`;
- `display_name` opcional;
- `confirmed`;
- `created_at` / `updated_at`.

A constraint `uq_participants_meeting_speaker_label` garante um único registro por `(meeting_id, speaker_label)`. A migration `0007_participant_identities` cria a tabela e faz backfill dos rótulos já existentes em `speaker_segments`.

## Cadeia de migrations

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
  ↓
0004_processing_jobs
  ↓
0005_transcription_segments
  ↓
0006_speaker_segments
  ↓
0007_participant_identities
```

Banco novo ou atualização:

```bash
alembic upgrade head
```

Web e worker não criam/migram schema automaticamente.

## Dados de IA persistidos

- `transcriptions`: resultado principal do STT;
- `transcription_segments`: texto temporalizado;
- `speaker_segments`: resultado temporal da diarização;
- `participants`: identidade humana editável/confirmável por reunião.

O nome do participante não é duplicado em cada `speaker_segment`; a API faz o enriquecimento por `speaker_label`.

---

**Status:** Active  
**Last Updated:** 2026-08-17
