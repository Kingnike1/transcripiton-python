# Product Backlog

## Concluído

### Fundação e Sprint 5

- [x] FastAPI/SQLAlchemy/Pydantic/Jinja2
- [x] Repository Pattern e Service Layer
- [x] Configuração/exceções/logging
- [x] suíte inicial de testes
- [x] CRUD de reuniões
- [x] upload/armazenamento inicial de áudio

### Sprint 6A — Estabilização

#### P0.1 — Transações e Unit of Work
- [x] Unit of Work
- [x] Service Layer dona da transação
- [x] repositories transaction-neutral
- [x] transições persistentes
- [x] ADR-017 + quality gate + merge em `develop`

#### P0.2 — Alembic
- [x] baseline `0001_initial_schema`
- [x] upgrade/downgrade/drift/stamp
- [x] ADR-018 + merge

#### P0.3 — Upload streaming
- [x] chunks/staging/limite
- [x] `ffprobe`
- [x] promotion/compensação
- [x] migration `0002_audio_media_metadata`
- [x] ADR-019 + merge

#### P0.4 — Concorrência
- [x] um áudio ativo por reunião
- [x] índice único parcial + migration `0003`
- [x] race tratada no banco/service
- [x] ADR-020 + merge

#### P0.5 — Erros seguros
- [x] envelope público + request ID
- [x] detalhes internos removidos
- [x] `file_path` removido da API
- [x] ADR-021 + merge

#### P0.6 — Lifecycle/configuração
- [x] startup sem `create_all()`
- [x] lifespan/engine cleanup
- [x] Pydantic V2/settings seguros
- [x] UTC/stale-processing
- [x] ADR-022 + merge

#### P0.7 — Qualidade/governança
- [x] Python 3.11/3.12
- [x] CI + Quality
- [x] Ruff/mypy/migrations/Bandit/pip-audit bloqueantes
- [x] runtime/dev requirements separados
- [x] 27 advisories iniciais remediados; runtime sem vulnerabilidades conhecidas no fechamento
- [x] GitFlow adaptado + Conventional Commits
- [x] ADR-023
- [x] PR #8 + merge em `develop`
- [x] CI + Quality pós-merge verdes
- [!] branch protection da `main` continua controle administrativo externo pendente (integração retornou 403)

---

## P0.8 — Organização documental — EM EXECUÇÃO

- [x] criar `docs/README.md` como mapa documental
- [x] criar `docs/current/` para documentação implementada
- [x] criar `docs/roadmap/` para futuro planejado
- [x] criar `docs/archive/` para histórico/superseded
- [x] reescrever arquitetura atual
- [x] reescrever banco atual
- [x] mover/sincronizar API atual
- [x] reescrever deployment de acordo com infraestrutura realmente existente
- [x] reescrever contributing conforme GitFlow/Quality atuais
- [x] reescrever roadmap de frontend sem afirmar funcionalidades inexistentes
- [x] reescrever roadmap de IA com jobs persistentes antes de Whisper
- [x] atualizar `PROJECT_CONTEXT.md`
- [x] atualizar `README.md`
- [x] atualizar `docs/00_PROJECT_OVERVIEW.md`
- [x] atualizar `PROJECT_GOVERNANCE.md` para a nova taxonomia
- [x] atualizar `PROJECT_STATE.MD` e backlog após P0.7
- [ ] registrar decisão técnica/ADR da taxonomia documental
- [ ] remover caminhos antigos/superseded depois de atualizar referências
- [ ] procurar links antigos/quebrados
- [ ] CI + Quality
- [ ] PR + merge em `develop`
- [ ] CI + Quality pós-merge

---

## Sprint 6B — Jobs persistentes

**Prioridade:** crítica antes da transcrição real.

- [ ] criar `ProcessingJob` + migration
- [ ] repository/service de jobs
- [ ] estados persistentes, progresso, tentativas e erros
- [ ] job idempotente após upload
- [ ] endpoint de acompanhamento por reunião/job
- [ ] worker separado do processo HTTP
- [ ] lease/lock e heartbeat
- [ ] retry com backoff
- [ ] timeout/cancelamento onde aplicável
- [ ] recuperação de jobs interrompidos/stale
- [ ] concorrência e idempotência
- [ ] cobertura de `processing_service.py`
- [ ] ADR de arquitetura do worker/queue

## Transcrição — depois da Sprint 6B

- [ ] modelar segmentos de transcrição
- [ ] decidir um provider inicial (local **ou** API)
- [ ] executar via worker
- [ ] persistir texto/idioma/segmentos/timestamps
- [ ] timeout/retry
- [ ] contrato/API de consulta
- [ ] primeira vertical slice de frontend

## Áudio/UI restante

- [ ] UI de reuniões/upload
- [ ] player/streaming autenticado
- [ ] gravação por microfone no navegador
- [ ] remoção/substituição controlada de áudio

## Produção e segurança

- [ ] autenticação/autorização
- [ ] rate limiting/quotas
- [ ] PostgreSQL quando staging/produção multiusuário justificar
- [ ] storage persistente/remoto quando necessário
- [ ] backups/restore
- [ ] observabilidade/readiness
- [ ] políticas de retenção/LGPD
- [ ] reverse proxy/HTTPS/limite de upload no edge
- [ ] aplicar branch protection/ruleset na `main` por acesso administrativo

## Inteligência e recursos posteriores

- [ ] diarização
- [ ] análise por LLM
- [ ] action items estruturados
- [ ] busca textual
- [ ] busca semântica somente se justificada
- [ ] exportação Markdown/TXT/DOCX/PDF

**Document Version:** 2.0  
**Last Updated:** 2026-08-16  
**Status:** Active
