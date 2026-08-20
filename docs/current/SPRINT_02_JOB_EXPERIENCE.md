# Sprint 2 — Jobs, estados e pipeline visual

## Objetivo

Tornar o processamento assíncrono compreensível sem duplicar a máquina de estados do backend. `ProcessingJob.status` permanece a fonte durável da verdade; a camada `JobExperienceService` deriva somente apresentação, diagnóstico e próxima ação.

## Entregas

- tradução de `PENDING`, `RUNNING`, `RETRYING`, `COMPLETED`, `FAILED` e `CANCELLED` para linguagem humana;
- estado efetivo `BLOCKED` quando um job aguarda execução mas o Worker não possui heartbeat recente;
- detecção visual de job `RUNNING` sem atualização recente;
- progresso, tentativa atual e idade da última atualização;
- próxima ação recomendada;
- cancelamento para jobs pendentes/retrying;
- retry explícito e seguro para jobs `FAILED`;
- polling continua consultando o backend como fonte da verdade;
- testes para bloqueio, worker ativo, job estagnado e retry.

## Decisão sobre BLOCKED

Nesta Sprint `BLOCKED` é um **estado efetivo de UX**, não um novo valor persistido no banco. Isso evita migration e, principalmente, evita duplicar a fonte da verdade. O job continua `PENDING`/`RETRYING`; se o Worker estiver indisponível, a API deriva `effective_status=BLOCKED` com motivo e próxima ação.

Uma futura necessidade de bloqueios duráveis por pré-requisitos específicos poderá justificar estado persistido mediante ADR e migration.

## Segurança

- ownership continua sendo validado por `require_meeting_access` e `require_job_access`;
- retry/cancelamento não aceitam job arbitrário sem autorização;
- a UI não recebe stack trace;
- diagnóstico de Worker não expõe secrets;
- processamento pesado permanece no Worker.

## Critérios de aceite

1. Job pendente + Worker saudável = `Aguardando na fila`.
2. Job pendente/retrying + Worker offline = `Bloqueado por configuração`.
3. Job running mostra progresso e última atualização.
4. Job running sem atualização recente é sinalizado como estagnado.
5. Job failed oferece `Tentar novamente`.
6. Apenas failed pode ser reencaminhado por retry explícito.
7. Apenas pending/retrying pode ser cancelado.
8. API continua retornando `status` durável além de `effective_status` de UX.

## Migration

Não necessária: nenhuma coluna ou constraint de banco foi alterada.

## CI do ciclo UX

Os workflows originalmente escutavam pull requests apenas contra `main` e `develop`. Como o ciclo de UX usa `integration/ux-roadmap` como base intermediária, CI, Quality e Docker não eram disparados para o PR da Sprint 2. A configuração da branch de integração foi corrigida para incluir `integration/ux-roadmap`; este commit também força um novo evento de sincronização do PR para executar os gates no fluxo correto.
