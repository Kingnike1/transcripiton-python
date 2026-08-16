# ADR-020 — Uma reunião possui no máximo um áudio ativo

**Status:** Aceita  
**Data:** 2026-08-16  
**Stack:** P0.4 — Consistência e concorrência

## Contexto

O `AudioService` já rejeitava um segundo upload quando encontrava um áudio ativo para a reunião. Essa proteção era apenas application-level: duas requisições concorrentes poderiam executar o mesmo pre-check antes de qualquer uma confirmar a inserção, permitindo duas linhas ativas no banco.

Ao mesmo tempo, o modelo usa soft delete, portanto uma constraint simples `UNIQUE(meeting_id)` impediria que uma reunião recebesse um áudio substituto no futuro depois que o anterior fosse desativado.

## Decisão

Uma reunião pode possuir **no máximo um áudio com `deleted_at IS NULL`**.

A garantia é aplicada em duas camadas:

1. `AudioService` mantém o pre-check para evitar trabalho desnecessário no caso comum;
2. o banco mantém um índice único parcial `uq_audios_active_meeting` sobre `meeting_id WHERE deleted_at IS NULL` para resolver races.

A migration `0003_one_active_audio_per_meeting` verifica previamente se existem duplicidades ativas. Se existirem, ela falha com os IDs das reuniões conflitantes e exige correção explícita dos dados antes de prosseguir. A migration nunca escolhe ou apaga dados automaticamente.

## Tratamento de corrida

Se duas requisições passarem pelo pre-check simultaneamente, uma delas vencerá o commit. A outra recebe `IntegrityError` do banco. O `AudioService` reconhece especificamente a constraint de áudio ativo e converte a falha para `AudioAlreadyExistsError`, preservando o mesmo contrato de domínio do caminho normal.

Falhas de integridade não relacionadas não são convertidas e continuam propagando como erro de banco.

## Idempotência

Nesta fase, upload repetido após sucesso continua sendo tratado como conflito (`409`) e não como retorno idempotente do recurso existente.

Não será introduzido `Idempotency-Key` persistente ainda porque o sistema não possui identidade/tenant para dar escopo confiável às chaves. Criar uma chave global agora poderia causar colisões entre futuros usuários/organizações.

A estratégia é:

- P0.4: garantir retry seguro contra duplicidade por constraint + compensação de storage;
- Sprint 6B: idempotência de criação de jobs por reunião/áudio;
- após autenticação/organizações: avaliar `Idempotency-Key` HTTP com escopo por principal/tenant.

## Alternativas rejeitadas

### `UNIQUE(meeting_id)` simples

Rejeitada porque impediria substituição futura após soft delete.

### Lock de aplicação

Rejeitado porque locks in-memory não funcionam entre múltiplos processos/instâncias e não substituem integridade do banco.

### `SELECT ... FOR UPDATE`

Não adotado como regra principal nesta fase porque SQLite não oferece a mesma semântica de row locking do PostgreSQL. A constraint do banco é mais simples, portátil e suficiente para a invariável.

### Apagar automaticamente duplicatas durante migration

Rejeitado por risco de perda silenciosa de dados.

## Consequências

### Positivas

- corrida de dois uploads não pode deixar dois áudios ativos;
- soft-deleted permanece como histórico e não bloqueia substituição;
- comportamento é garantido pelo banco, não só pelo código Python;
- o mesmo contrato de conflito é mantido para pre-check e race de commit.

### Cuidados

- bancos com duplicidades ativas precisam ser corrigidos antes da `0003`;
- substituição de áudio ainda não possui endpoint e continuará fora do escopo até o lifecycle de mídia ser definido;
- idempotência HTTP completa fica adiada até existir contexto de identidade/tenant.
