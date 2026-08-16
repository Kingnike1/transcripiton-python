# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-06  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack em execução:** P0.1 — Transações e Unit of Work  
**Branch:** `agent/stack-p0-1-transaction-uow`  
**Branch de integração:** `develop`  
**PR:** #2 — validação temporária contra `main` para acionar o CI legado  
**Status:** Implementação concluída; documentação e quality gate em andamento

## Baseline antes da Stack P0.1

- `main`: `017dc2127f4dd179c08a26308355fbc1b8ce066f`
- Sprint 5 integrada na `main`.
- Último CI da `main`: verde.
- Baseline do CI: 88 testes aprovados e 85,05% de cobertura.
- `develop` foi criada a partir da `main` para iniciar o GitFlow adaptado.

## Objetivo da Stack P0.1

Padronizar ownership transacional para que a camada de serviço coordene `commit` e `rollback`, repositories permaneçam transaction-neutral e transições de estado sejam duráveis.

## Entregas P0.1

- [x] Criar `SqlAlchemyUnitOfWork`.
- [x] Definir Service Layer como proprietária das transações.
- [x] Remover `commit()` de `MeetingRepository`.
- [x] Fazer repositories de escrita usarem `flush()` sem commit.
- [x] Migrar `MeetingService` para Unit of Work.
- [x] Persistir `MeetingService.transition_status()` corretamente.
- [x] Migrar `AudioService` para a mesma política transacional.
- [x] Evitar compensação destrutiva do arquivo após commit já confirmado.
- [x] Adicionar testes de commit, rollback e persistência em nova sessão.
- [x] Adicionar teste de rollback/compensação quando o commit do áudio falha.
- [x] Registrar ADR-017.
- [ ] GitHub Actions verde no head final.
- [ ] Retarget do PR #2 para `develop`.
- [ ] Merge em `develop` após quality gate.

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

Repositories não devem executar `commit()` ou `rollback()`.

## Itens Explicitamente Fora do Escopo desta Stack

- Alembic e migrations (P0.2).
- Upload em streaming (P0.3).
- Concorrência/constraint de áudio (P0.4).
- Sanitização global de erros (P0.5).
- Lifespan/Pydantic/timestamps (P0.6).
- Expansão do CI e branch protection (P0.7).
- Correção de `get_stale_processing(minutes)` — permanece registrada como bug para estabilização.
- Jobs persistentes e Whisper.

## Riscos e Dívidas Abertas

| Item | Prioridade | Estado |
|---|---|---|
| Alembic ainda não operacional | Emergencial | P0.2 |
| Upload lê arquivo inteiro em memória | Emergencial | P0.3 |
| Regra de um áudio não possui constraint de banco | Emergencial | P0.4 |
| Handler genérico expõe detalhes internos | Alta | P0.5 |
| `init_db()` ocorre durante importação | Média/Alta | P0.6 |
| `get_stale_processing(minutes)` ignora `minutes` | Alta | Pendente na estabilização |
| `main` sem proteção obrigatória | Alta | P0.7 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |

## Próxima Stack Recomendada

**P0.2 — Migrations com Alembic**

A próxima alteração estrutural será criar uma baseline de schema e tornar mudanças de banco versionáveis antes de adicionar constraints e jobs persistentes.

## Quality Gate

A Stack P0.1 só será considerada concluída após:

- todos os testes passarem no GitHub Actions;
- cobertura permanecer em pelo menos 80%;
- revisão do diff final;
- documentação sincronizada;
- PR direcionado para `develop`;
- merge sem ignorar falhas de CI.

**Document Version:** 1.5  
**Status:** Active
