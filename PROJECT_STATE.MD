# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6B — Jobs persistentes  
**Branch:** `agent/sprint-6b-persistent-jobs`  
**Branch base / integração:** `develop`  
**Status:** implementação da 6B concluída na branch; documentação/PR e gates finais em fechamento

## Baseline

P0.1–P0.8 estão integradas em `develop` pelos PRs #2–#9. O merge da P0.8 é `2e3e0ca32ae20fd8ee70f6e2e5c97ea328b82360`, com CI e Quality pós-merge verdes.

`main` continua como release estável anterior à Sprint 6A; branch protection administrativa permanece pendente por falta de permissão da integração.

## Sprint 6B — entregue na branch

- [x] `ProcessingJob` persistente.
- [x] migration `0004_processing_jobs`.
- [x] estados `PENDING/RUNNING/RETRYING/COMPLETED/FAILED/CANCELLED`.
- [x] progresso, tentativas, payload, resultado e erro persistidos.
- [x] `available_at`, lease, lock e heartbeat.
- [x] índice único parcial: no máximo um job ativo por reunião/tipo.
- [x] criação idempotente com defesa no banco.
- [x] claim otimista e recuperação de lease stale.
- [x] retry até `max_attempts`.
- [x] worker separado do FastAPI.
- [x] worker só reclama tipos com handler registrado.
- [x] API para criar job de transcrição, consultar, listar por reunião e cancelar pendentes.
- [x] fila/singleton em memória removidos.
- [x] `ProcessingService` migrado para jobs persistentes.
- [x] testes de persistência em nova sessão, ownership, stale recovery, retry e worker.
- [x] migration integrity atualizada para `processing_jobs`.
- [x] ADR-025.

## Validação já obtida

Head funcional antes do fechamento documental:

- Python 3.11: **117 testes aprovados**;
- cobertura: **86,95%**;
- Python 3.12: verde;
- Ruff: verde;
- mypy: verde;
- migrations: verdes;
- Bandit: verde;
- `pip-audit`: verde.

## Próximo gate

Após sincronizar arquitetura/API/banco/backlog/decisões:

1. CI + Quality no head documental final;
2. PR da Sprint 6B para `develop`;
3. merge somente com gates verdes;
4. CI + Quality pós-merge;
5. iniciar Sprint 7 — primeira transcrição real com um único provider.

## Capacidade após a 6B

### Funcional

- CRUD de reuniões;
- upload/armazenamento de áudio;
- jobs duráveis e worker separado;
- API de acompanhamento de processamento;
- base pronta para transcrição real.

### Ainda não funcional

- provider real de transcrição;
- transcrição persistida/segmentos;
- interface de uso ponta a ponta;
- deploy local simplificado para usuário final;
- diarização/LLM e recursos posteriores.

**Document Version:** 3.0  
**Status:** Active
