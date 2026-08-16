# ADR-025 — Jobs persistentes e worker separado

**Status:** Accepted  
**Data:** 2026-08-16

## Contexto

O AMIP possuía uma fila em memória baseada em `dict` e singleton. Jobs desapareciam em restart, workers não compartilhavam estado e não havia lease, heartbeat, retry ou proteção de concorrência. Esse desenho não é seguro para transcrição pesada.

## Decisão

Usar inicialmente o próprio banco como fila durável:

- `ProcessingJob` persistente;
- estados `PENDING`, `RUNNING`, `RETRYING`, `COMPLETED`, `FAILED`, `CANCELLED`;
- índice único parcial para no máximo um job ativo por reunião/tipo;
- claim otimista condicionado por status/heartbeat;
- lease e heartbeat para recuperar worker interrompido;
- contador de tentativas e retry com `available_at`;
- worker em processo separado do FastAPI;
- handlers registrados por `JobType`;
- worker nunca reclama jobs sem handler registrado;
- API para criar, consultar, listar e cancelar jobs;
- banco/Service Layer continuam proprietários das transações.

## Alternativas rejeitadas agora

### Redis + Celery/RQ/Dramatiq

São opções válidas quando volume e throughput justificarem, mas adicionariam infraestrutura antes de existir carga real.

### BackgroundTasks/FastAPI

Não sobrevive a restart e mantém processamento pesado acoplado ao processo web.

### Fila somente em memória

Foi removida por perder jobs e impedir coordenação entre processos.

## Consequências

### Positivas

- restart não perde trabalho;
- um segundo worker não assume lease saudável;
- worker morto pode ter job recuperado após expiração;
- retry e tentativas ficam auditáveis;
- a Sprint de transcrição recebe uma base operacional real.

### Limitações

- polling no banco não é solução de throughput massivo;
- SQLite continua adequado apenas ao uso pessoal/local e baixa concorrência;
- cancelamento de job já em execução não é preemptivo nesta versão;
- heartbeat depende do handler reportar progresso durante operações longas; a Sprint de transcrição deve manter lease adequado ao tempo de inferência.

## Critério de revisão

Reavaliar fila especializada quando houver múltiplos workers concorrentes, alta taxa de jobs, necessidade de scheduling avançado ou contenção perceptível no banco.
