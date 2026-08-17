# API atual do AMIP

Este documento descreve somente endpoints implementados. A especificação OpenAPI do FastAPI é a referência executável.

Base local padrão: `http://localhost:8000`.

## Reuniões

- `GET /api/meetings`
- `GET /api/meetings/{meeting_id}`
- `POST /api/meetings`
- `PUT /api/meetings/{meeting_id}`
- `DELETE /api/meetings/{meeting_id}`

## Áudio

- `POST /api/meetings/{meeting_id}/audio`
- `GET /api/meetings/{meeting_id}/audio`

## Jobs persistentes

- `POST /api/meetings/{meeting_id}/jobs/transcription`
- `POST /api/meetings/{meeting_id}/jobs/diarization`
- `POST /api/meetings/{meeting_id}/jobs/analysis`
- `GET /api/jobs/{job_id}`
- `GET /api/meetings/{meeting_id}/jobs`
- `DELETE /api/jobs/{job_id}`

O job de análise usa `JobType.SUMMARIZE` e só pode ser criado quando a reunião está `DIARIZED` ou já `SUMMARIZING`.

## Transcrição

`GET /api/meetings/{meeting_id}/transcription`

## Diarização

`GET /api/meetings/{meeting_id}/diarization`

Retorna speaker labels, timestamps, texto reconciliado e identidade do participante quando confirmada.

## Participantes

- `GET /api/meetings/{meeting_id}/participants`
- `PATCH /api/meetings/{meeting_id}/participants/{speaker_label}`

## Inteligência por LLM — Stack 12

### Consultar análise

```http
GET /api/meetings/{meeting_id}/analysis
```

A resposta contém:

- `summary`;
- `action_items`;
- `decisions`;
- `risks`;
- `open_questions`;
- `follow_up_tasks`;
- `provider`;
- `model_name`.

Itens estruturados podem conter `owner` e uma lista de `evidence` com `speaker_label`, `participant_name`, `start_time`, `end_time` e `quote`.

A análise é produzida fora do request HTTP pelo worker. O provider inicial é Ollama com modelo local configurável; a saída é validada por JSON Schema/Pydantic antes da persistência.

## Interface web

- `GET /meetings`
- `GET /meetings/{meeting_id}`

## Health

`GET /health`

Versão da aplicação na Stack 12: `0.8.0`.

## Ainda não implementado

- autenticação/autorização;
- infraestrutura production-ready;
- busca;
- exportação;
- gravação por microfone.

---

**Status:** Active  
**Last Updated:** 2026-08-17
