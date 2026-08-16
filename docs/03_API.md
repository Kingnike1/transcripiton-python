# API atual do AMIP

## Escopo deste documento

Este arquivo descreve **somente endpoints implementados no código atual**. Funcionalidades futuras como transcrição, diarização, análise por LLM, busca e exportação permanecem no backlog e não devem ser apresentadas aqui como disponíveis.

Base local padrão:

```text
http://localhost:8000
```

A documentação OpenAPI do FastAPI continua sendo a referência executável do contrato.

---

## Contrato de erro público

A partir da Stack P0.5, respostas de erro normalizadas usam:

```json
{
  "status": "error",
  "code": "NOT_FOUND",
  "detail": "Meeting not found",
  "request_id": "<uuid-gerado-pelo-servidor>"
}
```

A resposta inclui também:

```text
X-Request-ID: <mesmo UUID do corpo>
```

Regras:

- detalhes internos de exceção não são retornados ao cliente;
- SQL, caminhos internos, secrets e stack traces permanecem apenas nos logs;
- `RequestValidationError` não ecoa o payload recebido;
- erros HTTP explícitos são normalizados para o mesmo envelope;
- o servidor gera o `request_id`; valores enviados pelo cliente não são tratados como identificador confiável.

Códigos estáveis atualmente usados incluem:

| HTTP | `code` típico |
|---|---|
| 400 | `BAD_REQUEST` / `AUDIO_UPLOAD_ERROR` / `VALIDATION_ERROR` |
| 404 | `NOT_FOUND` |
| 409 | `CONFLICT` |
| 413 | `PAYLOAD_TOO_LARGE` |
| 415 | `UNSUPPORTED_MEDIA_TYPE` |
| 422 | `REQUEST_VALIDATION_ERROR` |
| 500 | `INTERNAL_ERROR`, `DATABASE_ERROR`, `AUDIO_ERROR`, etc. |
| 503 | `SERVICE_UNAVAILABLE` |

---

# Reuniões

## Listar reuniões

```http
GET /api/meetings?skip=0&limit=10&search=termo
```

Parâmetros:

- `skip`: inteiro >= 0, padrão 0;
- `limit`: inteiro entre 1 e 100, padrão 10;
- `search`: filtro opcional por título/descrição.

Resposta:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Reunião semanal",
      "description": "Acompanhamento do projeto",
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

## Consultar reunião

```http
GET /api/meetings/{meeting_id}
```

Retorna `MeetingResponse`. Reunião inexistente retorna 404 no envelope padrão.

## Criar reunião

```http
POST /api/meetings
Content-Type: application/json
```

```json
{
  "title": "Reunião semanal",
  "description": "Acompanhamento do projeto"
}
```

Sucesso: HTTP 201 com `MeetingResponse`.

## Atualizar reunião

```http
PUT /api/meetings/{meeting_id}
Content-Type: application/json
```

Campos são opcionais:

```json
{
  "title": "Novo título",
  "description": "Nova descrição"
}
```

## Remover reunião

```http
DELETE /api/meetings/{meeting_id}
```

A operação é soft delete. Sucesso: HTTP 204.

---

# Áudio da reunião

## Upload

```http
POST /api/meetings/{meeting_id}/audio
Content-Type: multipart/form-data
```

Campo multipart:

```text
file=<arquivo>
```

Formatos aceitos atualmente:

- `.mp3`;
- `.wav`;
- `.m4a`;
- `.ogg`;
- `.webm`.

Fluxo interno atual:

```text
UploadFile.file
  ↓ chunks de 1 MiB
storage/temp
  ↓ validação + ffprobe
promoção atômica
  ↓
Audio + Meeting status em uma Unit of Work
```

O processo:

- não usa `await file.read()` para materializar o upload inteiro em RAM;
- aplica limite durante a escrita;
- valida extensão, MIME, assinatura e presença de stream de áudio;
- usa `ffprobe` para duração, codec, canais e sample rate;
- mantém no máximo um áudio ativo por reunião;
- compensa o arquivo quando a transação de banco falha.

Sucesso: HTTP 201.

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

**`file_path` não faz parte do contrato público.** O caminho físico/relativo permanece detalhe interno de storage.

Possíveis respostas:

- 404: reunião não encontrada;
- 409: reunião já possui áudio ativo;
- 400: arquivo inválido/formato incompatível;
- 503: `ffprobe` indisponível no servidor.

## Consultar metadados do áudio

```http
GET /api/meetings/{meeting_id}/audio
```

Retorna `AudioResponse`, sem `file_path`.

---

# Health check

```http
GET /health
```

Resposta atual:

```json
{
  "status": "healthy",
  "version": "0.2.0"
}
```

O endpoint é atualmente apenas um liveness check. Readiness e verificação de dependências ainda serão tratados em stack posterior.

---

# Não implementado ainda

Os seguintes contratos **não fazem parte da API operacional atual**:

- início/consulta de transcrição;
- diarização/speaker identification;
- análise por LLM;
- busca textual avançada;
- exportação;
- autenticação/autorização;
- retry/cancelamento de jobs persistentes.

Esses itens permanecem no `docs/06_BACKLOG.md` e deverão entrar neste documento somente quando implementados.

---

**Document Version:** 2.0  
**Last Updated:** 2026-08-16  
**Status:** Active
