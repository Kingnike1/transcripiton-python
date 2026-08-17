# Product Backlog

## Concluído

### Fundação / Sprint 5 / Sprint 6A / Sprint 6B
- [x] FastAPI, SQLAlchemy, Pydantic e Jinja2
- [x] Repository Pattern, Service Layer e Unit of Work
- [x] CRUD de reuniões
- [x] upload/armazenamento seguro de áudio
- [x] Alembic e migrations
- [x] jobs persistentes + worker separado
- [x] CI/Quality, Python 3.11/3.12, Ruff, mypy, Bandit e pip-audit

### Stack 7 — Transcrição real
- [x] faster-whisper, persistência e job `TRANSCRIBE`

### Stack 8 — Interface utilizável
- [x] fluxo humano de reunião/upload/transcrição

### Stack 9 — Empacotamento
- [x] Docker/Compose, migrations, worker, healthcheck e smoke test

### Stack 10 — Diarização
- [x] pyannote, speaker segments, job `DIARIZE` e API

### Stack 11 — Identificação de participantes
- [x] `SPEAKER_XX` → identidade humana editável/confirmável

### Stack 12 — Inteligência por LLM
- [x] Ollama + `qwen3:4b`, structured outputs, rastreabilidade e job `SUMMARIZE`

### Stack 13 — Autenticação e autorização
- [x] usuários e contas
- [x] login/logout e sessões revogáveis
- [x] hashing de senha com scrypt
- [x] `Meeting.owner_id`
- [x] isolamento por usuário em CRUD, áudio, transcrição, diarização, participantes, análise e jobs
- [x] primeira conta assume dados legados sem owner
- [x] modo local preservado antes da criação de contas
- [x] UI de autenticação
- [x] migration `0009_auth_ownership`
- [x] testes multiusuário e ADR-028

## Stacks ainda faltantes

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

**Document Version:** 9.0  
**Last Updated:** 2026-08-17  
**Status:** Active
