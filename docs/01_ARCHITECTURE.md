# Arquitetura do Sistema

## Visão arquitetural

O AMIP é um **monólito modular em camadas**. O objetivo atual é manter uma única base de código e um único deploy lógico, com separação clara entre apresentação, API, casos de uso, persistência e providers externos.

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
Providers externos (futuros)
```

## Estado real dos módulos

| Área | Estado |
|---|---|
| API de reuniões | Implementada |
| Service/Repository de reuniões | Implementados |
| Upload e metadados de áudio | Implementados |
| Storage local | Implementado |
| Unit of Work SQLAlchemy | Implementada na Stack P0.1 |
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
- não controlar regra de negócio ou transação de domínio.

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

## Política transacional — Stack P0.1

A partir da ADR-017, **repositories não executam `commit()` ou `rollback()`**.

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

### Unit of Work

`app/database/unit_of_work.py` agrupa repositories que usam a mesma `Session` e oferece:

- `transaction()`;
- `commit()`;
- `rollback()`;
- `refresh()`.

A `Session` continua request-scoped no FastAPI. A Unit of Work não cria uma segunda conexão nem uma segunda sessão para o mesmo caso de uso.

### Repository Layer

Repositories encapsulam acesso ao banco e deixam as alterações preparadas para a transação do service.

Operações de escrita devem usar `add()`/`flush()` sem commit independente.

Isso permite casos de uso como:

```text
alterar Meeting
+ criar Audio
+ criar Job futuramente
= um único commit do caso de uso
```

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
ProcessingService ou outro caso de uso
  ↓
MeetingService.transition_status
  ↓
Meeting.transition_status valida domínio
  ↓
MeetingRepository.update (flush)
  ↓
Unit of Work commit
```

A Stack P0.1 corrige o comportamento anterior em que `transition_status()` alterava apenas o objeto da sessão sem garantir persistência.

### Upload de áudio

```text
POST /api/meetings/{meeting_id}/audio
  ↓
AudioService
  ├── valida reunião e arquivo
  ├── salva arquivo no storage
  ↓
Unit of Work
  ├── cria Audio
  ├── altera status da Meeting
  └── commit único
  ↓
refresh + response
```

Como filesystem e banco não participam da mesma transação ACID, uma falha antes do commit confirmado remove o arquivo armazenado. Após commit confirmado, uma falha posterior de leitura/refresh não deve apagar o arquivo persistido.

## Estrutura atual relevante

```text
app/
├── api/
│   ├── audio.py
│   ├── dependencies.py
│   └── meetings.py
├── config/
├── core/
│   ├── enums.py
│   ├── handlers.py
│   └── logging.py
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
    ├── audio_service.py
    ├── audio_validator.py
    ├── interfaces.py
    ├── job_service.py
    ├── meeting_service.py
    ├── pipeline_service.py
    ├── processing_service.py
    └── storage_service.py
```

## Provider architecture

Interfaces existem para transcrição, diarização, análise e exportação, mas providers concretos ainda não fazem parte do produto operacional.

Regra para futuras integrações:

```text
Application Service
  ↓ interface/port
Provider Adapter
  ↓
API ou modelo externo
```

Providers não devem controlar transações de banco da aplicação.

## Banco e migrations

- SQLite continua sendo o banco padrão de desenvolvimento.
- PostgreSQL permanece planejado para staging/produção multiusuário.
- SQLAlchemy é o ORM.
- Alembic é obrigatório pela governança, mas a infraestrutura de migrations ainda será implementada na Stack P0.2.
- `Base.metadata.create_all()` ainda existe e será tratado nas stacks de migrations/lifecycle.

## Testes arquiteturais relevantes

A política transacional deve ser protegida por testes que demonstrem:

- repository não commita sozinho;
- commit torna o dado visível em nova sessão;
- exceção causa rollback;
- transição de estado é durável;
- falha no commit do upload reverte banco e compensa filesystem.

## Regras de evolução

1. Não introduzir microservices sem necessidade comprovada.
2. Não colocar SQL em routes.
3. Não colocar `commit()` em repositories.
4. Não executar processamento pesado dentro do request HTTP.
5. Não integrar Whisper antes de jobs persistentes.
6. Toda mudança arquitetural relevante deve gerar ADR.
7. Documentação deve distinguir funcionalidade atual de roadmap.

## Decisões relacionadas

- `TECH_DECISIONS.md` — decisões gerais do projeto.
- `docs/adr/ADR-016-audio-upload-unit-of-work.md` — transação e compensação no upload.
- `docs/adr/ADR-017-service-layer-transaction-ownership.md` — ownership transacional global do Service Layer.

---

**Document Version:** 1.1  
**Last Updated:** 2026-08-06  
**Status:** Active
