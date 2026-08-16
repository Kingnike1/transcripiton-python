# Arquitetura do Sistema

## Visão arquitetural

O AMIP é um **monólito modular em camadas**. O objetivo atual é manter uma única base de código e um único deploy lógico, com separação clara entre apresentação, API, casos de uso, persistência, storage e providers externos.

A arquitetura evita microservices enquanto não existir necessidade comprovada de escala ou isolamento operacional.

```text
Presentation (Jinja2 / Bootstrap / HTMX futuro)
        ↓ HTTP
API (FastAPI)
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
Storage / Media Inspection / Providers externos
```

## Estado real dos módulos

| Área | Estado |
|---|---|
| API de reuniões | Implementada |
| Service/Repository de reuniões | Implementados |
| Upload de áudio | Implementado com staging em chunks |
| Inspeção de mídia | Implementada com `ffprobe` |
| Storage local | Implementado |
| Unit of Work SQLAlchemy | Implementada na P0.1 |
| Alembic | Implementado na P0.2 |
| Jobs | Protótipo em memória; não persistente |
| Pipeline | Orquestrador/contratos, sem providers concretos |
| Transcrição | Planejada |
| Diarização | Planejada |
| Análise por LLM | Planejada |
| Busca avançada | Planejada |
| Exportação | Planejada |
| Autenticação/autorização | Planejada |

## Responsabilidades das camadas

### Presentation Layer

Responsável por renderização e interação com usuário.

Tecnologias definidas:

- Jinja2;
- Bootstrap 5;
- HTMX para interações incrementais;
- JavaScript mínimo quando necessário.

Regras:

- sem regra de negócio;
- sem SQL;
- preferir server-side rendering;
- acessibilidade e simplicidade antes de efeitos visuais.

### API Layer

Responsável pelo protocolo HTTP.

Regras:

- validar request/response com Pydantic;
- converter erros de aplicação em respostas HTTP;
- usar dependency injection;
- não executar queries SQL diretamente;
- não controlar transações de domínio;
- não materializar arquivos grandes em memória quando streaming for possível.

### Application Service Layer

Responsável pelos casos de uso e pelas fronteiras transacionais.

Exemplos atuais:

- `MeetingService`;
- `AudioService`;
- `ProcessingService` ainda não operacional como pipeline persistente.

Regras:

- toda operação de escrita define seu limite transacional aqui;
- services podem coordenar mais de um repository;
- falhas externas não transacionais precisam de compensação explícita;
- detalhes de HTTP não pertencem a esta camada.

## Política transacional — P0.1

Repositories não executam `commit()` ou `rollback()`.

```text
API
  ↓
Application Service
  ↓
SqlAlchemyUnitOfWork.transaction()
  ├── sucesso → commit
  └── exceção → rollback
        ↓
Repositories
  └── query / add / flush
```

A `Session` continua request-scoped no FastAPI. A Unit of Work não cria uma segunda sessão para o mesmo caso de uso.

## Banco e migrations — P0.2

Alembic é a fonte oficial de evolução do schema.

Estrutura atual:

```text
alembic.ini
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 0001_initial_schema.py
    └── 0002_audio_media_metadata.py
```

Regras:

- bancos novos: `alembic upgrade head`;
- bancos legados devem ser marcados na revision que realmente representam antes de avançar;
- SQLite usa batch migrations;
- revisions autogeradas sempre exigem revisão humana;
- `Base.metadata.create_all()` ainda existe no startup e será retirado do fluxo normal na P0.6.

## Fluxos atuais

### Criação de reunião

```text
POST /api/meetings
  ↓
MeetingService.create
  ↓
MeetingRepository.create (add + flush)
  ↓
SqlAlchemyUnitOfWork.commit
  ↓
response
```

### Transição de estado

```text
MeetingService.transition_status
  ↓
Meeting.transition_status valida domínio
  ↓
MeetingRepository.update (flush)
  ↓
Unit of Work commit
```

### Upload de áudio — P0.3

O endpoint mantém `multipart/form-data`, mas não executa `await file.read()` para materializar o arquivo completo.

```text
POST /api/meetings/{meeting_id}/audio
  ↓
UploadFile.file
  ↓ run_in_threadpool
AudioUploadStager
  ↓ chunks de 1 MiB
storage/temp/{uuid}.staged.{ext}
  ↓
AudioValidator
  ├── nome / path
  ├── MIME / extensão
  ├── tamanho
  └── assinatura binária
  ↓
FFprobeAudioInspector
  ├── confirma stream de áudio
  ├── duração
  ├── codec
  ├── canais
  └── sample rate
  ↓
os.replace
  ↓
storage/audio/{meeting_id}/{uuid}.{ext}
  ↓
SqlAlchemyUnitOfWork
  ├── cria Audio
  ├── altera Meeting.status
  └── commit único
```

### Compensação

Filesystem e banco não compartilham uma transação ACID. Portanto:

- falha durante staging → temporário removido;
- falha de validação/ffprobe → temporário removido;
- falha do banco depois da promoção e antes do commit confirmado → arquivo final removido;
- falha posterior a um commit confirmado não deve apagar o arquivo persistido.

## Dependência operacional de mídia

O servidor que recebe uploads precisa possuir `ffprobe`, normalmente distribuído com FFmpeg.

Configuração:

```text
FFPROBE_BINARY=ffprobe
FFPROBE_TIMEOUT_SECONDS=15
```

Ausência de `ffprobe` é tratada como indisponibilidade operacional (HTTP 503), e não como erro de formato do usuário.

## Estrutura atual relevante

```text
app/
├── api/
│   ├── audio.py
│   ├── dependencies.py
│   └── meetings.py
├── config/
├── core/
├── database/
│   ├── audio_repository.py
│   ├── base.py
│   ├── meeting_repository.py
│   ├── repository.py
│   ├── session.py
│   └── unit_of_work.py
├── exceptions/
├── models/
├── providers/
├── schemas/
└── services/
    ├── audio_inspector.py
    ├── audio_service.py
    ├── audio_upload_stager.py
    ├── audio_validator.py
    ├── interfaces.py
    ├── job_service.py
    ├── meeting_service.py
    ├── pipeline_service.py
    ├── processing_service.py
    └── storage_service.py

migrations/
└── versions/
    ├── 0001_initial_schema.py
    └── 0002_audio_media_metadata.py
```

## Provider architecture

Interfaces existem para transcrição, diarização, análise e exportação, mas providers concretos ainda não fazem parte do produto operacional.

```text
Application Service
  ↓ interface/port
Provider Adapter
  ↓
API ou modelo externo
```

Providers não controlam transações do banco da aplicação.

## Próxima evolução arquitetural

A P0.4 deve formalizar no banco a cardinalidade de áudio por reunião e eliminar a race condition entre uploads concorrentes. A Sprint 6B somente começará depois da estabilização P0 e criará jobs persistentes/worker recuperável.

## Regras de evolução

1. Não introduzir microservices sem necessidade comprovada.
2. Não colocar SQL em routes.
3. Não colocar `commit()` em repositories.
4. Não executar processamento pesado dentro do request HTTP.
5. Não materializar uploads grandes quando streaming for possível.
6. Não integrar Whisper antes de jobs persistentes.
7. Toda mudança arquitetural relevante deve gerar ADR.
8. Toda alteração de schema deve usar Alembic.
9. Documentação deve distinguir funcionalidade atual de roadmap.

## Decisões relacionadas

- `TECH_DECISIONS.md` — registro técnico ativo.
- `docs/adr/ADR-017-service-layer-transaction-ownership.md` — ownership transacional.
- `docs/adr/ADR-018-alembic-schema-baseline.md` — migrations.
- `docs/adr/ADR-019-streaming-audio-staging.md` — upload em chunks e inspeção de mídia.

---

**Document Version:** 1.2  
**Last Updated:** 2026-08-16  
**Status:** Active
