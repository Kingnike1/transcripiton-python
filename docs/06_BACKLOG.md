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
- [x] `TRANSCRIBED`
- [x] texto/idioma/segmentos/timestamps/confiança persistidos
- [x] handler `TRANSCRIBE`
- [x] API de transcrição

### Stack 8 — Interface utilizável

- [x] listar/criar reuniões
- [x] detalhe da reunião
- [x] upload de áudio
- [x] iniciar transcrição
- [x] acompanhar job/progresso
- [x] visualizar transcrição/segmentos

### Stack 9 — Empacotamento para uso interno

- [x] Dockerfile multi-target web/worker
- [x] Compose com migration + web + worker
- [x] volumes persistentes
- [x] ffmpeg/ffprobe no container
- [x] healthcheck e smoke test
- [x] documentação operacional/backup

### Stack 10 — Diarização

- [x] `pyannote.audio`
- [x] `speaker-diarization-community-1`
- [x] `DIARIZED`
- [x] `speaker_segments`
- [x] alinhamento speaker ↔ texto
- [x] job durável `DIARIZE`
- [x] API de consulta

### Stack 11 — Identificação de participantes

- [x] entidade `Participant` por reunião
- [x] `SPEAKER_XX` → identidade humana editável
- [x] confirmação manual
- [x] persistência com constraint única por reunião/rótulo
- [x] migration com backfill de diarizações existentes
- [x] criação automática de placeholders em novas diarizações
- [x] APIs de listagem e edição
- [x] diarização enriquecida com nome/confirmado
- [x] UI para iniciar diarização e confirmar participantes
- [x] testes e ADR-026

## Stacks ainda faltantes

### Stack 12 — Inteligência por LLM
- [ ] resumo estruturado
- [ ] action items
- [ ] decisões
- [ ] riscos
- [ ] perguntas abertas/follow-ups
- [ ] validação estruturada e rastreabilidade
- [ ] atribuição a participantes quando confirmados

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

- [ ] smoke test com áudio real/modelos baixados na máquina de uso
- [!] branch protection administrativa da `main`, quando permissões permitirem

**Document Version:** 7.0  
**Last Updated:** 2026-08-17  
**Status:** Active
