# Arquitetura atual do AMIP

## Visão

O AMIP é um **monólito modular em camadas**. O desenho atual prioriza simplicidade operacional, transações explícitas e evolução incremental antes de qualquer divisão em microservices.

```text
Client
  ↓ HTTP
FastAPI
  ├── request ID middleware
  ├── error boundary
  ├── lifespan de recursos
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
Storage local / ffprobe / providers futuros
```

## Estado real

| Área | Estado |
|---|---|
| CRUD de reuniões | Implementado |
| Upload de áudio | Implementado com streaming/staging |
| Inspeção de mídia | Implementada com `ffprobe` |
| Storage local | Implementado |
| Unit of Work | Implementada |
| Alembic | Implementado |
| Um áudio ativo por reunião | Garantido pelo banco |
| Contrato seguro de erros/request ID | Implementado |
| Lifecycle/configuração segura | Implementado |
| CI + Quality | Implementados |
| Jobs persistentes | **Não implementados** |
| Transcrição real | **Não implementada** |
| Diarização | **Não implementada** |
| Análise por LLM | **Não implementada** |
| Busca avançada | **Não implementada** |
| Exportação | **Não implementada** |
| Autenticação/autorização | **Não implementada** |

## Camadas

### API

Responsável por HTTP, validação Pydantic, dependency injection e tradução de erros. Routes não contêm SQL nem controlam transações de domínio.

### Application Services

Responsáveis pelos casos de uso. Operações de escrita definem aqui sua fronteira transacional e coordenam compensações de efeitos externos, como filesystem.

### Unit of Work e repositories

```text
Application Service
  ↓
SqlAlchemyUnitOfWork.transaction()
  ├── sucesso → commit
  └── exceção → rollback
        ↓
Repositories
  └── query / add / update / flush
```

Repositories não fazem `commit()` nem `rollback()`.

## Schema e migrations

Alembic é a única fonte oficial de evolução do schema.

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
```

O processo web não executa migrations automaticamente. Deployment deve executar `alembic upgrade head` antes de iniciar a aplicação.

## Upload de áudio

```text
POST /api/meetings/{meeting_id}/audio
  ↓
UploadFile.file
  ↓ threadpool
AudioUploadStager
  ↓ chunks + limite
AudioValidator
  ↓
FFprobeAudioInspector
  ↓
os.replace
  ↓
Storage final
  ↓
SqlAlchemyUnitOfWork
```

O upload não materializa o arquivo inteiro em RAM. Temporários são removidos em erro e falhas de banco antes do commit confirmado compensam o arquivo promovido.

## Erros e correlação

Toda requisição recebe `request_id`. Respostas de erro públicas não expõem SQL, paths internos, stack traces, credenciais ou detalhes de exceção.

## Runtime

- Python 3.11 e 3.12 são testados.
- FastAPI lifespan administra recursos e descarta o engine no shutdown.
- staging/produção rejeitam `DEBUG=true` e secrets fracas.
- `utc_now()` é o relógio comum do backend.
- bind padrão é `127.0.0.1`.

## Quality gates

### CI

- Python 3.11;
- suíte completa;
- cobertura >=80%.

### Quality

- Ruff (`F`/`E9`);
- mypy;
- migration integrity;
- Bandit medium/high;
- `pip-audit` bloqueante;
- suíte completa em Python 3.12.

## Próxima fronteira arquitetural

A próxima mudança estrutural é **Sprint 6B — Jobs persistentes**. O protótipo em memória não é adequado para Whisper/processamento pesado. O desenho alvo permanece um monólito modular com processo web e worker separados compartilhando banco/storage; Redis/Celery não entram sem necessidade comprovada.

## ADRs relacionados

- ADR-017 — ownership transacional;
- ADR-018 — Alembic baseline;
- ADR-019 — streaming/staging de áudio;
- ADR-020 — um áudio ativo por reunião;
- ADR-021 — contrato público de erros;
- ADR-022 — lifecycle/configuração;
- ADR-023 — quality gates/dependências.

---

**Status:** Active  
**Last Updated:** 2026-08-16
