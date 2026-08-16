# Product Backlog

## Concluído

### Fundação e arquitetura

- [x] Estrutura FastAPI, SQLAlchemy, Pydantic e Jinja2
- [x] Repository Pattern e Service Layer
- [x] Pipeline e contratos de providers
- [x] Configuração e exceções modularizadas
- [x] Logging centralizado
- [x] Suíte inicial de testes

### Sprint 5 — Upload e armazenamento seguro de áudio

- [x] AudioRepository
- [x] AudioService transacional
- [x] Upload multipart por reunião
- [x] Consulta de metadados
- [x] Validação básica de extensão, MIME, tamanho e assinatura
- [x] Nome físico com UUID
- [x] Compensação de arquivo em falha de banco
- [x] Rejeição de upload duplicado
- [x] CI com cobertura mínima de 80%

### Sprint 6A — P0.1 Transações e Unit of Work

- [x] Unit of Work e ownership transacional no Service Layer
- [x] Repositories transaction-neutral
- [x] CRUD/transições persistentes
- [x] Testes e ADR-017
- [x] Quality gate e merge em `develop`

### Sprint 6A — P0.2 Migrations com Alembic

- [x] Alembic e baseline `0001_initial_schema`
- [x] SQLite batch migrations
- [x] Upgrade/downgrade/drift/stamp testados
- [x] ADR-018
- [x] Quality gate e merge em `develop`

### Sprint 6A — P0.3 Upload seguro em streaming

- [x] Upload em chunks/staging
- [x] Limite durante escrita
- [x] Validação e `ffprobe`
- [x] Promoção atômica/compensação
- [x] Migration `0002_audio_media_metadata`
- [x] Testes e ADR-019
- [x] Quality gate e merge em `develop`

### Sprint 6A — P0.4 Consistência e concorrência

- [x] Um áudio ativo por reunião
- [x] Índice único parcial e migration `0003`
- [x] Preflight de dados conflitantes
- [x] Constraint como defesa final contra race
- [x] Estratégia incremental de idempotência
- [x] Testes e ADR-020
- [x] Quality gate e merge em `develop`

### Sprint 6A — P0.5 Tratamento seguro de erros

- [x] Envelope público padronizado
- [x] request ID / `X-Request-ID`
- [x] Remover detalhes internos de 5xx
- [x] Normalizar HTTP/validation errors
- [x] Remover `file_path` público
- [x] Testes, API docs e ADR-021
- [x] Quality gate e merge em `develop`

### Sprint 6A — P0.6 Lifecycle e configuração

- [x] Remover `init_db()`/`create_all()` do startup normal
- [x] FastAPI lifespan e `engine.dispose()` no shutdown
- [x] Migrations externas via Alembic
- [x] `reset_db()` restrito a development/test
- [x] Pydantic V2/ConfigDict/SettingsConfigDict
- [x] `ENVIRONMENT`, DEBUG e SECRET_KEY seguros
- [x] UTC comum e stale-processing corrigido
- [x] Testes e ADR-022
- [x] Quality gate: 122 testes, 87,29%, zero warnings no fechamento
- [x] PR #7 e merge em `develop`
- [x] CI pós-merge verde

### Sprint 6A — P0.7 Qualidade e governança — EM FECHAMENTO

- [x] `actions/checkout@v6` e `actions/setup-python@v6`
- [x] CI em `main`, `develop` e `agent/**`
- [x] PRs para `main`/`develop` e `workflow_dispatch`
- [x] permissões mínimas e concurrency
- [x] Python 3.11 baseline + Python 3.12 compatibility gate
- [x] Ruff bloqueante (`F`/`E9`)
- [x] mypy bloqueante
- [x] migration integrity explícito
- [x] Bandit medium/high bloqueante
- [x] `pip-audit` runtime bloqueante
- [x] separar runtime (`requirements.txt`) e ferramentas (`requirements-dev.txt`)
- [x] remover dependências de exportação ainda não implementadas do runtime
- [x] remediar 27 advisories encontrados na auditoria inicial
- [x] runtime auditado: `No known vulnerabilities found`
- [x] bind seguro padrão `127.0.0.1`
- [x] TestClient migrado para `httpx2`
- [x] GitFlow adaptado e Conventional Commits formalizados
- [x] Python documentado alinhado a 3.11/3.12 realmente testados
- [x] ADR-023 e decisão técnica
- [ ] quality gate do head documental final
- [ ] PR e merge em `develop`
- [ ] CI/Quality pós-merge
- [!] proteção da `main`: bloqueada por permissão administrativa da integração (403); controle externo pendente

---

## P0 — Estabilização restante

### P0.8 — Documentação

- [ ] Separar documentação atual, roadmap e archive
- [ ] Sincronizar OpenAPI/documentação ativa
- [ ] Atualizar `PROJECT_CONTEXT.md` com status real
- [ ] Arquivar prompts/documentos históricos
- [ ] Revisar deployment e contributing

---

## Sprint 6B — Jobs persistentes

**Prioridade:** Crítica antes do Whisper

- [ ] Criar modelo e repository de jobs
- [ ] Persistir status, progresso, tentativas e erros
- [ ] Criar job após upload de áudio
- [ ] Endpoint para consultar job por reunião
- [ ] Garantir idempotência
- [ ] Recuperar jobs interrompidos
- [ ] Implementar worker separado
- [ ] Lease, heartbeat, timeout e retry
- [ ] Testes de concorrência e recuperação
- [ ] Cobrir `processing_service.py`

## Transcrição

- [ ] Modelar segmentos de transcrição
- [ ] Implementar um provider inicial atrás de `ITranscriber`
- [ ] Executar transcrição fora do request HTTP
- [ ] Persistir texto, idioma, segmentos e timestamps
- [ ] Tratar timeout/limites/retry
- [ ] Exibir transcrição no frontend

## Módulo de áudio — itens restantes

- [ ] UI de upload
- [ ] Player de áudio
- [ ] Gravação por microfone
- [x] Extração de duração
- [ ] Remoção/substituição controlada de áudio
- [ ] Download/streaming autenticado

## Fases posteriores

- [ ] Autenticação e autorização
- [ ] PostgreSQL para staging/produção multiusuário
- [ ] Storage remoto quando necessário
- [ ] Diarização
- [ ] Análise por LLM
- [ ] Busca textual
- [ ] Exportação Markdown, TXT, DOCX e PDF

**Document Version:** 1.9  
**Last Updated:** 2026-08-16  
**Status:** Active
