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
- [x] testes e gates verdes

### Stack 8 — Interface utilizável

- [x] listar/criar reuniões
- [x] detalhe da reunião
- [x] upload de áudio
- [x] iniciar transcrição
- [x] acompanhar job/progresso
- [x] visualizar transcrição/segmentos
- [x] fluxo Jinja2 + Bootstrap + JavaScript mínimo
- [x] PR #12 integrado em `develop`

### Stack 10 — Diarização — executada antes da 9 por decisão de sequência

- [x] provider `pyannote.audio` atrás de `ISpeakerIdentifier`
- [x] `speaker-diarization-community-1`
- [x] exclusive speaker diarization
- [x] estado `DIARIZED`
- [x] persistência em `speaker_segments`
- [x] alinhamento speaker ↔ texto por timestamps
- [x] job durável `DIARIZE`
- [x] API de consulta da diarização
- [x] CI + Quality verdes
- [x] PR #13 integrado em `develop`

## Stack 9 — Empacotamento para uso interno — EM FECHAMENTO

- [x] Dockerfile multi-target web/worker
- [x] Compose com migration + web + worker
- [x] volumes persistentes para SQLite/storage/logs/cache de modelo
- [x] ffmpeg/ffprobe no container
- [x] entrypoint real do worker
- [x] healthcheck
- [x] smoke test operacional
- [x] documentação de configurar/iniciar/parar/atualizar/backup
- [x] gate Docker para web target + `docker compose config`
- [ ] CI + Quality + Docker verdes no PR
- [ ] merge para `develop`

## Stacks ainda faltantes após a Stack 9

### Stack 11 — Identificação de participantes
- [ ] mapear `SPEAKER_XX` para pessoas/nomes
- [ ] edição/confirmação manual
- [ ] persistir identidade do participante

### Stack 12 — Inteligência por LLM
- [ ] resumo estruturado
- [ ] action items
- [ ] decisões
- [ ] riscos
- [ ] perguntas abertas/follow-ups
- [ ] validação estruturada e rastreabilidade

### Stack 13 — Autenticação e autorização
- [ ] usuários/login
- [ ] autorização por recurso
- [ ] preparação multiusuário

### Stack 14 — Infra de produção
- [ ] PostgreSQL quando necessário
- [ ] storage remoto
- [ ] backups operacionais
- [ ] observabilidade/métricas/logs de produção
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

**Document Version:** 6.0  
**Last Updated:** 2026-08-16  
**Status:** Active
