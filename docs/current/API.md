# API atual do AMIP

Este documento descreve **somente endpoints implementados**. A especificação OpenAPI do FastAPI é a referência executável.

Base local padrão: `http://localhost:8000`.

## Erros públicos

Erros normalizados incluem `status`, `code`, `detail` e `request_id`, além do header `X-Request-ID`. SQL, secrets, paths e stack traces permanecem internos.

## Reuniões

- `GET /api/meetings`
- `GET /api/meetings/{meeting_id}`
- `POST /api/meetings`
- `PUT /api/meetings/{meeting_id}`
- `DELETE /api/meetings/{meeting_id}`

## Áudio

- `POST /api/meetings/{meeting_id}/audio`
- `GET /api/meetings/{meeting_id}/audio`

O upload usa streaming/staging, limite durante escrita, inspeção por `ffprobe` e no máximo um áudio ativo por reunião. `file_path` não faz parte do contrato público.

## Jobs persistentes

- `POST /api/meetings/{meeting_id}/jobs/transcription`
- `POST /api/meetings/{meeting_id}/jobs/diarization`
- `GET /api/jobs/{job_id}`
- `GET /api/meetings/{meeting_id}/jobs`
- `DELETE /api/jobs/{job_id}`

Jobs usam `PENDING`, `RUNNING`, `RETRYING`, `COMPLETED`, `FAILED` e `CANCELLED`, com claim, lease, heartbeat, retry e recuperação stale.

## Transcrição

```http
GET /api/meetings/{meeting_id}/transcription
```

Retorna texto, idioma e segmentos persistidos com timestamps/confiança quando disponíveis.

## Diarização

```http
GET /api/meetings/{meeting_id}/diarization
```

Retorna os segmentos com `speaker_label`, timestamps e texto reconciliado. Na Stack 11 a resposta também inclui os participantes da reunião e, por segmento, `participant_name` e `participant_confirmed`.

## Participantes — Stack 11

### Listar identidades

```http
GET /api/meetings/{meeting_id}/participants
```

Cada item contém `speaker_label`, `display_name` e `confirmed`.

### Editar/confirmar identidade

```http
PATCH /api/meetings/{meeting_id}/participants/{speaker_label}
Content-Type: application/json
```

Exemplo:

```json
{
  "display_name": "Pablo",
  "confirmed": true
}
```

Uma identidade marcada como confirmada exige nome não vazio. O mapeamento é local à reunião; não representa reconhecimento biométrico global entre reuniões.

## Interface web

- `GET /meetings`
- `GET /meetings/{meeting_id}`

A tela de detalhe permite upload, transcrição, diarização e confirmação/edição dos participantes.

## Health

```http
GET /health
```

Versão da aplicação na Stack 11: `0.7.0`.

## Ainda não implementado

- inteligência por LLM;
- autenticação/autorização;
- infraestrutura production-ready;
- busca;
- exportação;
- gravação por microfone.

---

**Status:** Active  
**Last Updated:** 2026-08-17
