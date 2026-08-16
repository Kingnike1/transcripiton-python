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

- [x] `SqlAlchemyUnitOfWork`
- [x] Service Layer proprietária de commit/rollback
- [x] Repositories transaction-neutral
- [x] CRUD e transições persistentes
- [x] Testes e ADR-017
- [x] Quality gate
- [x] Merge em `develop`

### Sprint 6A — P0.2 Migrations com Alembic

- [x] Alembic e baseline `0001_initial_schema`
- [x] SQLite batch migrations
- [x] Upgrade/downgrade/drift/stamp testados
- [x] ADR-018
- [x] Quality gate
- [x] Merge em `develop`

### Sprint 6A — P0.3 Upload seguro em streaming

- [x] Remover leitura integral do arquivo em RAM
- [x] Chunks de 1 MiB e staging temporário
- [x] Limite durante escrita
- [x] Validação de path/MIME/assinatura
- [x] `ffprobe` para stream/duração/codec/canais/sample rate
- [x] Promoção atômica e compensação
- [x] Migration `0002_audio_media_metadata`
- [x] Testes e ADR-019
- [x] Quality gate
- [x] Merge em `develop`

### Sprint 6A — P0.4 Consistência e concorrência

- [x] Um áudio ativo por reunião
- [x] Índice único parcial `uq_audios_active_meeting`
- [x] Migration `0003_one_active_audio_per_meeting`
- [x] Preflight de dados legados conflitantes
- [x] Constraint como defesa final contra race
- [x] Tradução específica de conflito no Service Layer
- [x] Estratégia incremental de idempotência
- [x] Testes e ADR-020
- [x] Quality gate
- [x] Merge em `develop`

### Sprint 6A — P0.5 Tratamento seguro de erros

- [x] Envelope público padronizado
- [x] `request_id` e `X-Request-ID`
- [x] Remover detalhes internos de 5xx
- [x] Normalizar `HTTPException`/`RequestValidationError`
- [x] Remover `file_path` do contrato público
- [x] Testes contra vazamento
- [x] `docs/03_API.md` sincronizado
- [x] ADR-021
- [x] Quality gate
- [x] Merge em `develop`

### P0.7 — itens antecipados para restaurar o gate

- [x] CI executa em `develop`
- [x] PRs para `develop` disparam CI
- [x] `workflow_dispatch` disponível
- [x] permissões do workflow reduzidas a leitura
- [x] cancelamento de runs redundantes por concurrency
- [x] `develop` integrada validada: 114 testes, 87,04% de cobertura

---

## P0 — Estabilização emergencial restante

### P0.6 — Lifecycle e configuração — EM EXECUÇÃO

- [ ] Remover `init_db()`/`create_all()` do startup normal
- [ ] Implementar lifespan de recursos no FastAPI
- [ ] Manter migrations fora do processo web via Alembic
- [ ] Corrigir `TemplateResponse` depreciado
- [ ] Eliminar `datetime.utcnow()` restante
- [ ] Padronizar helper de UTC
- [ ] Corrigir `get_stale_processing(minutes)`
- [ ] Usar `ProcessingStatus` no stale query
- [ ] Migrar settings para `SettingsConfigDict`
- [ ] Migrar schemas restantes para `ConfigDict`
- [ ] Validar `ENVIRONMENT`, `DEBUG` e `SECRET_KEY`
- [ ] Atualizar `.env.example`
- [ ] Testar import sem criação de schema, settings e stale threshold
- [ ] ADR/documentação/CI/merge em `develop`

### P0.7 — Qualidade e governança

- [x] Expandir CI para `develop`
- [x] Resolver disparo do Actions no fluxo atual
- [ ] Adicionar verificação explícita de migrations ao CI
- [ ] Adicionar Ruff
- [ ] Adicionar type checking
- [ ] Adicionar auditoria de dependências e segurança
- [ ] Atualizar actions com runtime não depreciado quando versões estáveis forem definidas
- [ ] Proteger `main`
- [ ] Formalizar GitFlow adaptado e Conventional Commits na governança
- [ ] Alinhar versão de Python documentada com a suportada/testada

### P0.8 — Documentação

- [ ] Separar documentação atual, roadmap e archive
- [ ] Sincronizar OpenAPI/documentação ativa
- [ ] Atualizar `PROJECT_CONTEXT.md` com status real das features
- [ ] Arquivar prompts e documentos históricos obsoletos
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

## Transcrição

- [ ] Modelar segmentos de transcrição
- [ ] Implementar um provider inicial atrás de `ITranscriber`
- [ ] Executar transcrição fora do request HTTP
- [ ] Persistir texto, idioma, segmentos e timestamps
- [ ] Tratar timeouts, limites e retry
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

**Document Version:** 1.7  
**Last Updated:** 2026-08-16  
**Status:** Active
