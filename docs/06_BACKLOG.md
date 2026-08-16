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
- [x] Implementar FastAPI lifespan de recursos
- [x] Manter migrations externas via Alembic
- [x] `engine.dispose()` no shutdown
- [x] Restringir `reset_db()` a development/test
- [x] Corrigir `TemplateResponse` depreciado
- [x] Criar helper UTC e eliminar `datetime.utcnow()` conhecido
- [x] Corrigir `get_stale_processing(minutes)`
- [x] Usar `ProcessingStatus` no stale query
- [x] Migrar settings para `SettingsConfigDict`
- [x] Migrar schema restante para `ConfigDict`
- [x] Validar `ENVIRONMENT`, `DEBUG` e `SECRET_KEY`
- [x] Atualizar `.env.example`
- [x] Testar import sem criação de schema, lifecycle, settings e stale threshold
- [x] ADR-022 + arquitetura/banco/decisões atualizados
- [x] Quality gate de implementação: 122 testes, 87,29%, zero warnings pytest
- [x] PR #7 criado
- [ ] CI do head documental final
- [ ] Merge em `develop`

### P0.7 — itens antecipados para restaurar o gate

- [x] CI em `develop`
- [x] PRs para `develop`
- [x] `workflow_dispatch`
- [x] permissões mínimas de leitura
- [x] concurrency/cancelamento de runs redundantes

---

## P0 — Estabilização restante

### P0.7 — Qualidade e governança

- [ ] Adicionar verificação explícita de migrations ao CI
- [ ] Adicionar Ruff
- [ ] Adicionar type checking
- [ ] Adicionar auditoria de dependências e segurança
- [ ] Atualizar GitHub Actions com runtime não depreciado
- [ ] Proteger `main`
- [ ] Formalizar GitFlow adaptado e Conventional Commits
- [ ] Alinhar versão Python documentada com a suportada/testada

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

**Document Version:** 1.8  
**Last Updated:** 2026-08-16  
**Status:** Active
