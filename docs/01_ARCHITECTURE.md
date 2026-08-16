# Arquitetura do Sistema

## Visão atual

O AMIP é um **monólito modular em camadas** com separação entre HTTP, casos de uso, persistência, storage e providers externos.

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
| Um áudio ativo por reunião | Implementado — P0.4 |
| Contrato seguro de erros | Implementado — P0.5 |
| Lifecycle/configuração segura | Implementado — P0.6 |
| CI/Quality estático e segurança | Implementado na P0.7 |
| Jobs persistentes | Não implementados |
| Transcrição real | Não implementada |
| Diarização | Não implementada |
| Análise por LLM | Não implementada |
| Autenticação/autorização | Não implementada |

---

# Camadas e responsabilidades

## API Layer

- protocolo HTTP e Pydantic;
- dependency injection;
- tradução de erros conhecidos;
- sem SQL ou transações de domínio;
- upload grande não deve ser materializado em memória.

## Application Service Layer

- casos de uso;
- fronteiras transacionais;
- coordenação de repositories;
- compensação explícita para efeitos externos não ACID.

## Repository Layer

Repositories são transaction-neutral e usam query/add/update/flush. Não executam `commit()` ou `rollback()`.

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

---

# P0.2–P0.4 — Schema e integridade

Alembic é a fonte oficial de evolução do schema.

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
```

A `0003` garante no máximo um áudio ativo por reunião por índice único parcial. Soft-deleted permanece como histórico.

---

# P0.3 — Pipeline de upload

```text
POST /api/meetings/{meeting_id}/audio
  ↓
UploadFile.file
  ↓ threadpool
AudioUploadStager (chunks)
  ↓
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

O limite é aplicado durante a escrita, temporários são limpos em erro e falha de banco antes do commit confirmado compensa o arquivo final.

---

# P0.5 — Error boundary

Toda requisição recebe `request_id`. Erros públicos usam `status`, `code`, `detail` e `request_id`. SQL, paths, credenciais, stack traces e detalhes internos permanecem apenas nos logs.

---

# P0.6 — Lifecycle e configuração

O processo web não altera o schema:

```text
Deployment
  ↓
alembic upgrade head
  ↓
FastAPI startup
  ↓
requests
  ↓
FastAPI shutdown
  ↓
engine.dispose()
```

- lifespan administra apenas recursos;
- `reset_db()` é restrito a desenvolvimento/testes;
- settings usam Pydantic V2;
- staging/produção rejeitam `DEBUG=true` e secret fraca;
- `utc_now()` é o relógio comum;
- `get_stale_processing(minutes)` respeita o limiar.

---

# P0.7 — CI, Quality e dependências

## Workflows

O repositório possui dois gates complementares:

### CI

- Python 3.11;
- suíte completa;
- cobertura mínima de 80%.

### Quality

- Ruff (`F`/`E9`);
- mypy;
- `tests/test_migrations.py` explicitamente;
- Bandit para severidade média/alta;
- `pip-audit` bloqueante sobre `requirements.txt`;
- suíte completa de compatibilidade em Python 3.12.

Ambos usam `actions/checkout@v6` e `actions/setup-python@v6`, permissões mínimas e cancelamento de execuções redundantes.

## Dependências

```text
requirements.txt
  → somente runtime realmente utilizado

requirements-dev.txt
  → pytest / coverage / httpx2
  → Ruff / mypy / Bandit / pip-audit
```

Bibliotecas de exportação DOCX/PDF/Markdown foram removidas do runtime enquanto essa funcionalidade não existe. Elas serão reintroduzidas apenas na Stack de exportação, com versões auditadas naquele momento.

A auditoria inicial encontrou 27 advisories em 7 pacotes. Após atualização direcionada e redução da superfície de runtime, `pip-audit -r requirements.txt` passou a retornar **No known vulnerabilities found**.

O bind padrão do servidor é `127.0.0.1`; exposição externa é uma decisão explícita do deployment.

## Git e governança

- `main`: release estável;
- `develop`: integração;
- branches `agent/stack-*`: trabalho por Stack;
- Conventional Commits obrigatório;
- Python 3.11 e 3.12 são as versões oficialmente testadas.

A proteção administrativa da `main` continua desejada, mas a integração disponível não possui permissão para configurar/consultar branch protection (403). Não considerar a branch protegida até esse controle ser aplicado externamente.

---

# Regras de evolução

1. Não colocar SQL em routes.
2. Não colocar `commit()` em repositories.
3. Toda mudança de schema usa Alembic.
4. Migrations não rodam automaticamente no processo web.
5. Processamento pesado não roda no request HTTP.
6. Upload grande não deve ser materializado em memória.
7. Não integrar Whisper antes de jobs persistentes.
8. Erros públicos não expõem detalhes internos.
9. Configuração de staging/produção deve falhar fechada quando insegura.
10. Dependência não utilizada não pertence ao runtime.
11. CI e Quality devem estar verdes antes de merge.
12. Documentação ativa descreve apenas funcionalidades realmente implementadas.

## ADRs relacionados

- ADR-017 — ownership transacional;
- ADR-018 — baseline Alembic;
- ADR-019 — streaming/staging de áudio;
- ADR-020 — um áudio ativo por reunião;
- ADR-021 — contrato público de erros;
- ADR-022 — lifecycle e configuração de runtime;
- ADR-023 — quality gates e superfície de dependências.

## Próxima evolução

Depois da P0.7: **P0.8 — organização documental**, seguida pela **Sprint 6B — Jobs persistentes**.

---

**Document Version:** 1.5  
**Last Updated:** 2026-08-16  
**Status:** Active
