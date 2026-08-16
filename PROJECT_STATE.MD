# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack em execução:** P0.2 — Migrations com Alembic  
**Branch:** `agent/stack-p0-2-alembic`  
**Branch base:** `agent/stack-p0-1-transaction-uow`  
**Branch de integração:** `develop`  
**Status:** P0.2 implementada em branch dependente; integração bloqueada pelo quality gate da P0.1

## Baseline

- `main`: `017dc2127f4dd179c08a26308355fbc1b8ce066f`.
- Sprint 5 integrada na `main`.
- `develop` criada a partir da `main`.
- P0.1 implementada no PR #2, ainda sem GitHub Actions no head atual.
- Último CI confiável da `main`: 88 testes aprovados e 85,05% de cobertura.
- P0.2 foi criada sobre o head da P0.1 para permitir continuidade sem integrar código não validado em `develop`/`main`.

## P0.1 — Transações e Unit of Work

### Implementado

- [x] `SqlAlchemyUnitOfWork`.
- [x] Service Layer proprietária de commit/rollback.
- [x] Repositories transaction-neutral.
- [x] CRUD de reunião migrado para UoW.
- [x] Persistência real de transições de estado.
- [x] `AudioService` alinhado à UoW.
- [x] Testes de commit, rollback e persistência em nova sessão.
- [x] ADR-017 e documentação arquitetural.

### Pendente de integração

- [ ] CI no head atual.
- [ ] PR direcionado para `develop`.
- [ ] Merge em `develop`.

## P0.2 — Migrations com Alembic

### Objetivo

Tornar o schema versionável antes de introduzir constraints adicionais e jobs persistentes.

### Implementado

- [x] `alembic.ini`.
- [x] `migrations/env.py` conectado a `settings.DATABASE_URL`.
- [x] SQLite configurado com `render_as_batch=True`.
- [x] Comparação de tipos habilitada.
- [x] Template de revisions.
- [x] Revision `0001_initial_schema` com o schema atual.
- [x] Teste de `upgrade head` em banco vazio.
- [x] Teste de drift entre migration e `Base.metadata`.
- [x] Teste de adoção de banco legado por `stamp head`.
- [x] Teste de `downgrade base` em banco descartável.
- [x] ADR-018.
- [x] Documentação de banco atualizada.
- [x] Validação independente: upgrade/downgrade executados e comparação retornou zero diferenças.

### Regra de adoção

```text
Banco novo
  → alembic upgrade head

Banco preexistente criado antes do Alembic
  → backup
  → verificar compatibilidade do schema
  → alembic stamp head
  → migrations futuras via alembic upgrade head
```

`stamp` não deve ser usado para esconder drift de schema.

## Política Transacional Vigente

```text
API
  ↓
Application Service
  ↓ define commit/rollback
SqlAlchemyUnitOfWork
  ↓
Repositories (query/add/flush)
  ↓
SQLAlchemy Session
```

## Riscos e Dívidas Abertas

| Item | Prioridade | Estado |
|---|---|---|
| CI não dispara para commits feitos pela integração | Crítica para integração | Bloqueando merges |
| Upload lê arquivo inteiro em memória | Emergencial | P0.3 |
| Regra de um áudio não possui constraint de banco | Emergencial | P0.4 |
| Handler genérico expõe detalhes internos | Alta | P0.5 |
| `init_db()`/`create_all()` ainda participa do startup | Alta | P0.6 |
| `datetime.utcnow()` restante | Média/Alta | P0.6 |
| `get_stale_processing(minutes)` ignora `minutes` | Alta | P0.6 |
| `main` sem proteção obrigatória | Alta | P0.7 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |

## Próxima Stack Técnica

**P0.3 — Upload seguro em streaming**

Objetivo: remover a leitura integral do arquivo em RAM, introduzir escrita em chunks, arquivo temporário, limite durante a transferência e base para inspeção de mídia.

## Regra de Integração

Nenhuma stack dependente será mesclada em `develop` ou `main` enquanto a P0.1 não tiver um quality gate reproduzível. Branches seguintes podem ser desenvolvidas de forma empilhada para não bloquear o trabalho.

**Document Version:** 1.6  
**Status:** Active
