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

### Upload

```http
POST /api/meetings/{meeting_id}/audio
Content-Type: multipart/form-data
```

O backend processa em chunks/staging, aplica limite durante escrita, valida arquivo, usa `ffprobe`, promove atomicamente e garante no máximo um áudio ativo.

### Metadados

```http
GET /api/meetings/{meeting_id}/audio
```

`file_path` não faz parte do contrato público.

## Jobs persistentes — Sprint 6B

### Criar/obter job ativo de transcrição

```http
POST /api/meetings/{meeting_id}/jobs/transcription
```

Pré-condições:

- reunião existe;
- reunião possui áudio ativo.

A criação é idempotente enquanto houver um job `PENDING`, `RUNNING` ou `RETRYING` do tipo `TRANSCRIBE` para a reunião. Chamadas repetidas retornam o mesmo job ativo.

Exemplo:

```json
{
  "id": "<uuid>",
  "meeting_id": 1,
  "job_type": "TRANSCRIBE",
  "status": "PENDING",
  "progress": 0,
  "attempt": 0,
  "max_attempts": 3,
  "error_message": null,
  "result": null,
  "available_at": "2026-08-16T22:00:00",
  "created_at": "2026-08-16T22:00:00",
  "started_at": null,
  "completed_at": null
}
```

### Consultar job

```http
GET /api/jobs/{job_id}
```

### Listar jobs da reunião

```http
GET /api/meetings/{meeting_id}/jobs
```

### Cancelar

```http
DELETE /api/jobs/{job_id}
```

Sucesso: HTTP 204. Somente `PENDING` ou `RETRYING` são canceláveis nesta versão. Cancelamento preemptivo de job já em execução não está implementado.

### Estados

```text
PENDING
RUNNING
RETRYING
COMPLETED
FAILED
CANCELLED
```

O worker usa lease/heartbeat. Jobs `RUNNING` cujo heartbeat expirou podem ser recuperados por outro worker.

## Health

```http
GET /health
```

A versão da aplicação após a Sprint 6B é `0.3.0`. O endpoint continua sendo liveness simples.

## Ainda não implementado

- transcrição real e consulta de transcript;
- diarização;
- LLM;
- busca/exportação;
- autenticação/autorização.

---

**Status:** Active  
**Last Updated:** 2026-08-16
