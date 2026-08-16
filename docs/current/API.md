# API atual do AMIP

Este documento descreve **somente endpoints implementados**. A especificação OpenAPI gerada pelo FastAPI é a referência executável do contrato.

Base local padrão:

```text
http://localhost:8000
```

## Erros públicos

Erros normalizados usam:

```json
{
  "status": "error",
  "code": "NOT_FOUND",
  "detail": "Meeting not found",
  "request_id": "<uuid>"
}
```

A resposta inclui o mesmo identificador em:

```text
X-Request-ID: <uuid>
```

Detalhes internos, SQL, secrets, paths e stack traces não fazem parte do contrato público.

Códigos atuais incluem, conforme o caso:

| HTTP | `code` típico |
|---|---|
| 400 | `BAD_REQUEST`, `AUDIO_UPLOAD_ERROR`, `VALIDATION_ERROR` |
| 404 | `NOT_FOUND` |
| 409 | `CONFLICT` |
| 413 | `PAYLOAD_TOO_LARGE` |
| 415 | `UNSUPPORTED_MEDIA_TYPE` |
| 422 | `REQUEST_VALIDATION_ERROR` |
| 500 | `INTERNAL_ERROR`, `DATABASE_ERROR`, `AUDIO_ERROR` |
| 503 | `SERVICE_UNAVAILABLE` |

---

## Reuniões

### Listar

```http
GET /api/meetings?skip=0&limit=10&search=termo
```

- `skip`: >= 0, padrão 0;
- `limit`: 1–100, padrão 10;
- `search`: título/descrição opcional.

Resposta:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Reunião semanal",
      "description": "Acompanhamento",
      "status": "CREATED",
      "created_at": "2026-08-16T10:00:00Z",
      "updated_at": "2026-08-16T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Consultar

```http
GET /api/meetings/{meeting_id}
```

### Criar

```http
POST /api/meetings
Content-Type: application/json
```

```json
{
  "title": "Reunião semanal",
  "description": "Acompanhamento"
}
```

Sucesso: HTTP 201.

### Atualizar

```http
PUT /api/meetings/{meeting_id}
```

Campos de título/descrição são opcionais no payload de atualização.

### Remover

```http
DELETE /api/meetings/{meeting_id}
```

Soft delete. Sucesso: HTTP 204.

---

## Áudio

### Upload

```http
POST /api/meetings/{meeting_id}/audio
Content-Type: multipart/form-data
```

Campo:

```text
file=<arquivo>
```

Extensões aceitas atualmente:

- `.mp3`;
- `.wav`;
- `.m4a`;
- `.ogg`;
- `.webm`.

O backend:

- processa o stream em chunks em vez de `await file.read()` integral;
- aplica limite durante a escrita;
- faz staging temporário;
- valida nome/path, extensão, MIME e assinatura;
- usa `ffprobe` para confirmar stream de áudio e extrair metadados;
- promove o arquivo atomicamente;
- mantém no máximo um áudio ativo por reunião;
- compensa storage se a transação falhar antes do commit confirmado.

Exemplo de sucesso HTTP 201:

```json
{
  "meeting_id": 1,
  "audio": {
    "id": 5,
    "meeting_id": 1,
    "filename": "meeting.wav",
    "file_size": 123456,
    "mime_type": "audio/wav",
    "duration": 125,
    "codec_name": "pcm_s16le",
    "channels": 1,
    "sample_rate": 16000,
    "created_at": "2026-08-16T10:10:00Z"
  },
  "status": "AUDIO_UPLOADED"
}
```

`file_path` é detalhe interno e não faz parte de `AudioResponse`.

Respostas relevantes:

- 400 — upload/formato inválido;
- 404 — reunião inexistente;
- 409 — áudio ativo já existe;
- 503 — `ffprobe` indisponível.

### Metadados

```http
GET /api/meetings/{meeting_id}/audio
```

Retorna `AudioResponse` sem caminho de storage.

---

## Health

```http
GET /health
```

```json
{
  "status": "healthy",
  "version": "0.2.0"
}
```

É um **liveness check** simples. Readiness de banco/storage ainda não foi implementado.

---

## Não implementado

Não existem ainda endpoints operacionais de:

- jobs persistentes/retry/cancelamento;
- transcrição;
- diarização;
- análise por LLM;
- busca avançada;
- exportação;
- autenticação/autorização.

Esses contratos só serão adicionados aqui depois da implementação correspondente.

---

**Status:** Active  
**Last Updated:** 2026-08-16
