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

### Sprint 6B — Jobs persistentes

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

### Sprint 7 — Transcrição real — CONCLUÍDA

- [x] modelar `TranscriptionSegment`
- [x] definir estado `TRANSCRIBED` e fluxo `AUDIO_UPLOADED → TRANSCRIBING → TRANSCRIBED`
- [x] preservar compatibilidade `TRANSCRIBING → DIARIZING` para o pipeline futuro
- [x] escolher um provider inicial: `faster-whisper`
- [x] configurar modelo `base`, CPU e `int8` como defaults locais
- [x] manter dependência pesada isolada em `requirements-worker.txt`
- [x] registrar handler `TRANSCRIBE` no worker
- [x] persistir texto, idioma, segmentos, timestamps e confiança
- [x] tratar retry/falha final sem marcar reunião como FAILED em tentativa recuperável
- [x] manter heartbeat ativo durante transcrição longa
- [x] API para consultar transcrição
- [x] testes de contrato com provider fake
- [x] teste do adapter sem carregar modelo real
- [x] idempotência do resultado persistido
- [x] proteção contra path traversal no storage
- [x] CI do PR #11 verde
- [x] Quality do PR #11 verde
- [x] merge para `develop`
- [ ] smoke test operacional com áudio real/modelo baixado localmente

## Sprint 8 — Interface utilizável — ATUAL

- [ ] listar/criar reuniões
- [ ] detalhe da reunião
- [ ] upload de áudio
- [ ] iniciar transcrição
- [ ] acompanhar job/progresso
- [ ] visualizar transcrição e segmentos
- [ ] estados claros de erro/retry/conclusão
- [ ] fluxo ponta a ponta por Jinja2 + Bootstrap + HTMX/JS mínimo

## Sprint 9 — Empacotamento para uso interno

- [ ] Dockerfile
- [ ] Compose com migration + web + worker
- [ ] volume persistente para SQLite/storage/cache de modelo
- [ ] `ffmpeg/ffprobe` disponível no ambiente
- [ ] documentação simples: configurar, iniciar, parar, atualizar e backup
- [ ] smoke test do fluxo operacional

## Posterior ao primeiro uso interno

- [ ] diarização de speakers
- [ ] identificação de participantes
- [ ] análise por LLM/resumos/action items
- [ ] autenticação/autorização antes de exposição pública/multiusuário
- [ ] PostgreSQL quando concorrência/produção justificar
- [ ] storage remoto, backups e observabilidade
- [ ] busca
- [ ] exportação
- [ ] gravação por microfone

**Document Version:** 4.1  
**Last Updated:** 2026-08-16  
**Status:** Active
