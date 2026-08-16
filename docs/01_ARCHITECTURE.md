# Arquitetura do Sistema

## Visão atual

O AMIP permanece um **monólito modular em camadas**, com uma única base de código e separação explícita entre HTTP, casos de uso, persistência, storage e providers externos.

```text
Client
  ↓ HTTP
FastAPI
  ├── Request ID middleware
  ├── error boundary / handlers
  └── routes
        ↓
Application Services
        ↓
SqlAlchemyUnitOfWork
        ↓
Repositories
        ↓
SQLAlchemy / Database

Application Services
  ↓
Storage / ffprobe / providers futuros
```

Microservices, Redis, Celery e Kubernetes continuam fora do desenho atual até existir necessidade comprovada.

## Estado real dos módulos

| Área | Estado |
|---|---|
| API CRUD de reuniões | Implementada |
| Upload de áudio | Implementado com streaming/staging |
| Inspeção de áudio | Implementada com `ffprobe` |
| Storage local | Implementado |
| Unit of Work | Implementada — P0.1 |
| Alembic | Implementado — P0.2 |
| Regra de um áudio ativo | Implementada no banco — P0.4 |
| Contrato seguro de erros | Implementado — P0.5 |
| Jobs persistentes | Não implementados |
| Transcrição real | Não implementada |
| Diarização | Não implementada |
| Análise por LLM | Não implementada |
| Autenticação/autorização | Não implementada |

---

# Camadas e responsabilidades

## API Layer

Responsável apenas por protocolo HTTP:

- request/response Pydantic;
- dependency injection;
- tradução de erros conhecidos para HTTP;
- nunca executar SQL diretamente;
- nunca controlar transações de domínio;
- não materializar uploads grandes em memória quando streaming for possível.

## Application Service Layer

Responsável pelos casos de uso e pela fronteira transacional.

Exemplos atuais:

- `MeetingService`;
- `AudioService`.

Regras:

- um caso de uso de escrita define um único limite transacional;
- múltiplos repositories podem participar da mesma Unit of Work;
- efeitos externos não ACID exigem compensação explícita;
- detalhes de HTTP não pertencem aos services.

## Repository Layer

Repositories são **transaction-neutral**:

```text
query / add / update / flush
```

Não executam `commit()` ou `rollback()`.

---

# P0.1 — Ownership transacional

```text
Application Service
  ↓
SqlAlchemyUnitOfWork.transaction()
  ├── sucesso → commit
  └── exceção → rollback
        ↓
Repositories
```

Isso garante que operações compostas possam ser confirmadas ou revertidas como um único caso de uso.

---

# P0.2–P0.4 — Schema e integridade

Alembic é a fonte oficial de evolução do banco.

Cadeia atual:

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
```

A `0003` introduz o índice único parcial:

```text
uq_audios_active_meeting
WHERE deleted_at IS NULL
```

Regra de domínio:

> uma reunião pode possuir no máximo um áudio ativo.

Soft-deleted permanece como histórico. O pre-check do service reduz trabalho desnecessário, mas a constraint do banco é a autoridade final contra race conditions.

A migration recusa dados legados conflitantes em vez de escolher ou apagar registros automaticamente.

---

# P0.3 — Upload de áudio

```text
POST /api/meetings/{meeting_id}/audio
  ↓
UploadFile.file
  ↓ run_in_threadpool
AudioUploadStager
  ↓ chunks de 1 MiB
storage/temp
  ↓
AudioValidator
  ↓
FFprobeAudioInspector
  ↓
os.replace
  ↓
storage/audio/{meeting_id}/{uuid}.{ext}
  ↓
SqlAlchemyUnitOfWork
  ├── cria Audio
  ├── altera Meeting.status
  └── commit
```

Garantias:

- limite aplicado durante a escrita;
- arquivo inteiro não é mantido em RAM;
- temporário é limpo em falha;
- `ffprobe` confirma stream de áudio e extrai metadados;
- promoção do arquivo é atômica;
- falha de banco antes de commit confirmado compensa o arquivo final.

Dependência operacional:

```text
ffprobe
```

Ausência do binário é falha de infraestrutura e retorna 503.

---

# P0.5 — Error boundary e request correlation

Toda requisição recebe um `request_id` gerado pelo servidor.

```text
Request
  ↓
Request ID middleware
  ↓
Route / Service
  ↓ sucesso
Response + X-Request-ID

ou

Exception
  ↓
Global handler
  ├── log interno + traceback + request_id
  └── resposta sanitizada + X-Request-ID
```

Envelope público:

```json
{
  "status": "error",
  "code": "INTERNAL_ERROR",
  "detail": "An unexpected error occurred",
  "request_id": "<uuid>"
}
```

Regras:

- `str(exc)`, `exc.details`, SQL, paths e stack traces não são enviados em 5xx;
- detalhes técnicos ficam nos logs internos;
- `HTTPException` e `RequestValidationError` são normalizados;
- o traceback recebido pelo handler é preservado explicitamente no log;
- `AudioResponse` não expõe `file_path`.

---

# Estrutura relevante

```text
app/
├── api/
│   ├── audio.py
│   ├── dependencies.py
│   └── meetings.py
├── core/
│   ├── handlers.py
│   └── request_context.py
├── database/
│   ├── audio_repository.py
│   ├── meeting_repository.py
│   ├── session.py
│   └── unit_of_work.py
├── models/
├── schemas/
└── services/
    ├── audio_inspector.py
    ├── audio_service.py
    ├── audio_upload_stager.py
    ├── audio_validator.py
    ├── meeting_service.py
    └── storage_service.py

migrations/
└── versions/
    ├── 0001_initial_schema.py
    ├── 0002_audio_media_metadata.py
    └── 0003_one_active_audio_per_meeting.py
```

---

# Próxima evolução

A próxima stack é **P0.6 — Lifecycle e configuração**:

- remover `init_db()`/`create_all()` do import normal;
- usar lifespan do FastAPI;
- concluir timezone-aware datetimes;
- concluir Pydantic V2/`ConfigDict`;
- corrigir `get_stale_processing(minutes)`;
- impedir defaults inseguros fora de desenvolvimento.

Depois disso, P0.7 deve tornar CI/governança reproduzíveis antes de qualquer integração definitiva das branches empilhadas.

---

## Regras de evolução

1. Não colocar SQL em routes.
2. Não colocar `commit()` em repositories.
3. Toda mudança de schema usa Alembic.
4. Toda decisão arquitetural relevante gera ADR.
5. Processamento pesado não roda no request HTTP.
6. Upload grande não deve ser materializado em memória.
7. Não integrar Whisper antes de jobs persistentes.
8. Erros públicos não expõem detalhes internos.
9. Documentação ativa descreve apenas funcionalidades realmente implementadas.

## ADRs relacionados

- ADR-017 — ownership transacional;
- ADR-018 — baseline Alembic;
- ADR-019 — streaming/staging de áudio;
- ADR-020 — um áudio ativo por reunião;
- ADR-021 — contrato público de erros.

---

**Document Version:** 1.3  
**Last Updated:** 2026-08-16  
**Status:** Active
