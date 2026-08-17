# Product Backlog

## Concluído

### Fundação / Sprint 5 / Sprint 6A / Sprint 6B

- [x] FastAPI, SQLAlchemy, Pydantic e Jinja2
- [x] Repository Pattern, Service Layer e Unit of Work
- [x] CRUD de reuniões
- [x] upload/armazenamento seguro de áudio
- [x] Alembic e migrations
- [x] jobs persistentes + worker separado
- [x] claim, lease, heartbeat, retry e recovery
- [x] CI/Quality, Python 3.11/3.12, Ruff, mypy, Bandit e pip-audit

### Stack 7 — Transcrição real
- [x] faster-whisper
- [x] persistência de texto/segmentos
- [x] job `TRANSCRIBE`

### Stack 8 — Interface utilizável
- [x] fluxo humano de reunião/upload/transcrição

### Stack 9 — Empacotamento
- [x] Docker/Compose, migrations, worker, healthcheck e smoke test

### Stack 10 — Diarização
- [x] pyannote, speaker segments, job `DIARIZE` e API

### Stack 11 — Identificação de participantes
- [x] `SPEAKER_XX` → identidade humana editável/confirmável
- [x] persistência, API, UI, testes e ADR-026

### Stack 12 — Inteligência por LLM
- [x] Ollama local como provider padrão
- [x] `qwen3:4b` como baseline configurável
- [x] resumo estruturado
- [x] action items e responsáveis
- [x] decisões
- [x] riscos
- [x] perguntas abertas e follow-ups
- [x] structured output validado por Pydantic/JSON Schema
- [x] evidências com timestamps/speaker/citação
- [x] atribuição a participantes confirmados
- [x] provider/modelo persistidos
- [x] job durável `SUMMARIZE`
- [x] API de análise
- [x] testes com provider fake e ADR-027

## Stacks ainda faltantes

### Stack 13 — Autenticação e autorização
- [ ] usuários/login
- [ ] autorização por recurso
- [ ] preparação multiusuário

### Stack 14 — Infra de produção
- [ ] PostgreSQL quando necessário
- [ ] storage remoto
- [ ] backups operacionais
- [ ] observabilidade/métricas/logs
- [ ] hardening e deploy production-ready

### Stack 15 — Busca
- [ ] busca textual em reuniões/transcrições
- [ ] PostgreSQL FTS antes de vector DB

### Stack 16 — Exportação
- [ ] Markdown
- [ ] TXT
- [ ] DOCX
- [ ] PDF

### Stack 17 — Gravação por microfone
- [ ] captura no navegador
- [ ] upload seguro para reunião
- [ ] integração com pipeline existente

## Pendências operacionais independentes

- [ ] instalar Ollama + `qwen3:4b` e executar smoke test real da análise
- [ ] smoke test com áudio real/modelos baixados na máquina de uso
- [!] branch protection administrativa da `main`, quando permissões permitirem

**Document Version:** 8.0  
**Last Updated:** 2026-08-17  
**Status:** Active
