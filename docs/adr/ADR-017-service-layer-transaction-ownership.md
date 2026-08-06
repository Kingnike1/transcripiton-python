# ADR-017 — Service Layer como proprietária das transações

**Status:** Aceita  
**Data:** 2026-08-06  
**Stack:** P0.1 — Transações e Unit of Work

## Contexto

O projeto possuía dois modelos transacionais incompatíveis. `MeetingRepository` executava `commit()` em operações CRUD, enquanto `AudioService` já coordenava a transação do upload. Além disso, `MeetingService.transition_status()` alterava o modelo sem executar commit, permitindo que transições desaparecessem ao encerrar a sessão.

Essa inconsistência impede casos de uso atômicos que envolvam múltiplos repositories e seria um risco direto para jobs persistentes e para o pipeline de transcrição.

## Decisão

A camada de serviço será a única proprietária das fronteiras transacionais.

- Repositories executam consultas, `add()` e `flush()`, mas nunca `commit()` ou `rollback()`.
- `SqlAlchemyUnitOfWork` agrupa repositories que compartilham a mesma `Session`.
- `SqlAlchemyUnitOfWork.transaction()` executa commit ao concluir e rollback quando uma exceção ocorre.
- Services de escrita usam a Unit of Work para coordenar uma operação completa.
- O `AudioService` mantém compensação do filesystem porque banco e filesystem não participam da mesma transação ACID.

Fluxo padrão:

```text
API
  ↓
Application Service
  ↓ define fronteira transacional
SqlAlchemyUnitOfWork
  ↓
Repositories (query/add/flush)
  ↓
SQLAlchemy Session
```

## Alternativas rejeitadas

### Commit em cada repository

Rejeitada porque impede compor operações atômicas entre vários repositories e foi a causa da inconsistência encontrada no `MeetingService`.

### Adicionar apenas `db.commit()` em `transition_status()`

Rejeitada porque corrigiria o sintoma mantendo dois modelos de ownership transacional no sistema.

### Introduzir framework externo de Unit of Work

Rejeitada por YAGNI. A aplicação precisa apenas de uma coordenação pequena sobre a `Session` existente.

## Consequências positivas

- Transições de estado passam a ser duráveis.
- CRUD e upload usam a mesma política transacional.
- Casos de uso futuros podem envolver múltiplos repositories atomicamente.
- Rollback passa a ter um único ponto de responsabilidade.
- A futura Stack de jobs persistentes ganha uma base transacional previsível.

## Consequências e cuidados

- Todo novo repository deve permanecer transaction-neutral.
- Todo novo caso de uso de escrita deve definir sua fronteira no Service Layer.
- Operações externas, como filesystem ou APIs, ainda exigem compensação ou padrões como outbox quando necessário.
- Uma falha após commit confirmado não pode ser tratada como se o banco ainda pudesse sofrer rollback.

## Critérios de validação

- Repository não chama `commit()`.
- Alteração confirmada fica visível em uma nova sessão.
- Exceção durante uma Unit of Work remove alterações não commitadas.
- `MeetingService.transition_status()` persiste o novo estado.
- Falha de commit no upload reverte banco e remove o arquivo ainda não confirmado.
