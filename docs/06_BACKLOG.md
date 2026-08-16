# Product Backlog

## Concluído

### Fundação e Sprint 5

- [x] FastAPI/SQLAlchemy/Pydantic/Jinja2
- [x] Repository Pattern e Service Layer
- [x] configuração/exceções/logging
- [x] CRUD de reuniões
- [x] upload/armazenamento inicial de áudio

### Sprint 6A — Estabilização

P0.1–P0.8 estão integradas em `develop` pelos PRs #2–#9 com CI/Quality pós-merge verdes.

Entregas principais:

- [x] Unit of Work/ownership transacional
- [x] Alembic e migrations
- [x] upload streaming/staging + `ffprobe`
- [x] integridade concorrente de áudio
- [x] erros seguros/request ID
- [x] lifecycle/configuração/UTC
- [x] Python 3.11/3.12 + Ruff/mypy/Bandit/pip-audit
- [x] documentação `current/roadmap/archive`
- [!] branch protection da `main` continua controle administrativo externo pendente

## Sprint 6B — Jobs persistentes — EM FECHAMENTO

- [x] `ProcessingJob` + migration `0004_processing_jobs`
- [x] repository/service de jobs
- [x] estados persistentes, progresso, tentativas e erros
- [x] criação idempotente por reunião/tipo
- [x] índice único parcial para job ativo
- [x] endpoints criar/consultar/listar/cancelar
- [x] worker separado do processo HTTP
- [x] claim/lease/lock/heartbeat
- [x] retry com `available_at` e `max_attempts`
- [x] recuperação de `RUNNING` stale
- [x] concorrência/ownership testados
- [x] fila e singleton em memória removidos
- [x] `ProcessingService` migrado e coberto por testes
- [x] ADR-025
- [x] migration integrity inclui `processing_jobs`
- [x] validação intermediária: 117 testes, 86,95% e Quality verde
- [ ] CI + Quality no head documental final
- [ ] PR → `develop`
- [ ] CI + Quality do PR
- [ ] merge + pós-merge verde

## Sprint 7 — Transcrição real

- [ ] modelar `TranscriptionSegment`
- [ ] definir estado `TRANSCRIBED`/fluxo de status
- [ ] escolher **um** provider inicial para uso pessoal/local
- [ ] manter dependência pesada isolada do processo web quando possível
- [ ] registrar handler `TRANSCRIBE` no worker
- [ ] persistir texto, idioma, segmentos, timestamps e confiança
- [ ] tratar retry/falha final sem marcar reunião como FAILED em tentativa recuperável
- [ ] API para consultar transcrição
- [ ] testes de contrato com provider fake
- [ ] validação manual com áudio real fora do CI

## Sprint 8 — Interface utilizável

- [ ] listar/criar reuniões
- [ ] detalhe da reunião
- [ ] upload de áudio
- [ ] iniciar transcrição
- [ ] acompanhar job/progresso
- [ ] visualizar transcrição
- [ ] fluxo ponta a ponta por Jinja2 + Bootstrap + HTMX/JS mínimo

## Sprint 9 — Empacotamento para uso interno

- [ ] Dockerfile
- [ ] Compose com migration + web + worker
- [ ] volume persistente para SQLite/storage/cache de modelo
- [ ] `ffmpeg/ffprobe` disponível no ambiente
- [ ] documentação simples: configurar, iniciar, parar, atualizar e backup
- [ ] smoke test do fluxo operacional

## Posterior ao primeiro uso interno

- [ ] autenticação/autorização antes de exposição pública/multiusuário
- [ ] PostgreSQL quando concorrência/produção justificar
- [ ] storage remoto, backups e observabilidade
- [ ] diarização
- [ ] análise por LLM/action items
- [ ] busca
- [ ] exportação
- [ ] gravação por microfone

**Document Version:** 3.0  
**Last Updated:** 2026-08-16  
**Status:** Active
