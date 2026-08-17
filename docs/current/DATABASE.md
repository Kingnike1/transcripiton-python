# Banco de dados atual

## Estratégia

- SQLAlchemy 2.x;
- SQLite para uso local/testes;
- PostgreSQL planejado na Stack 14 quando houver necessidade real;
- Alembic como fonte oficial do schema;
- UTC como semântica temporal.

## Schema atual

```text
users
  ├── auth_sessions
  └── meetings
        ├── audios
        │     └── transcriptions
        │            ├── transcription_segments
        │            └── speaker_segments
        ├── participants
        ├── meeting_analysis (1:1)
        └── processing_jobs
```

## Autenticação — Stack 13

`users` armazena e-mail normalizado, hash de senha, status ativo e timestamps. Senha em texto puro nunca é persistida.

`auth_sessions` armazena `user_id`, `token_hash`, expiração e criação. O token entregue ao navegador é opaco e não é persistido diretamente.

`meetings.owner_id` referencia `users.id`. O campo permanece nullable apenas para permitir evolução de bancos legados; a primeira conta criada faz claim de reuniões antigas sem owner e o fluxo autenticado cria novas reuniões sempre com owner.

## Dados de IA

- `transcriptions`: resultado principal do STT;
- `transcription_segments`: texto temporalizado;
- `speaker_segments`: resultado temporal da diarização;
- `participants`: identidade humana por reunião;
- `meeting_analysis`: inteligência estruturada + provider/modelo.

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
  ↓
0008_analysis_provider_metadata
  ↓
0009_auth_ownership
```

Banco novo ou atualização:

```bash
alembic upgrade head
```

Web e worker não criam/migram schema automaticamente.

---

**Status:** Active  
**Last Updated:** 2026-08-17
