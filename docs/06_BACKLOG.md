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
- [x] Validação de extensão, MIME, tamanho e assinatura binária básica
- [x] Nome físico com UUID
- [x] Compensação de arquivo em falha de banco
- [x] Rejeição de upload duplicado
- [x] Testes unitários e de integração
- [x] CI com cobertura mínima de 80%

### Sprint 6A — P0.1 Transações e Unit of Work

- [x] Criar `SqlAlchemyUnitOfWork`
- [x] Definir Service Layer como proprietária de commit/rollback
- [x] Tornar repositories transaction-neutral
- [x] Migrar CRUD do `MeetingService` para Unit of Work
- [x] Persistir transições de status em banco
- [x] Migrar `AudioService` para a mesma política transacional
- [x] Testar commit, rollback e persistência em nova sessão
- [x] Testar compensação do storage quando commit falha
- [x] Registrar ADR da decisão
- [ ] Quality gate final e merge em `develop`

### Sprint 6A — P0.2 Migrations com Alembic

- [x] Inicializar Alembic
- [x] Criar `alembic.ini` e ambiente de migrations
- [x] Criar baseline `0001_initial_schema`
- [x] Configurar SQLite batch migrations
- [x] Usar `settings.DATABASE_URL` como fonte de configuração
- [x] Validar `upgrade head` em banco vazio
- [x] Comparar schema migrado com `Base.metadata`
- [x] Validar adoção de banco legado via `stamp head`
- [x] Validar `downgrade base` em banco descartável
- [x] Registrar ADR-018
- [x] Atualizar documentação de banco
- [ ] Executar suíte completa no GitHub Actions quando o bloqueio de CI for resolvido
- [ ] Integrar após P0.1 passar pelo quality gate

## P0 — Estabilização emergencial restante

### P0.3 — Upload seguro em streaming

- [ ] Ler `UploadFile` em chunks
- [ ] Limitar tamanho durante escrita
- [ ] Usar arquivo temporário e movimentação atômica
- [ ] Validar/inspecionar mídia sem carregar o arquivo completo em RAM
- [ ] Integrar `ffprobe` para duração, codec, canais e sample rate
- [ ] Limpar temporários em erro/cancelamento

### P0.4 — Consistência e concorrência

- [ ] Decidir um ou múltiplos áudios por reunião
- [ ] Criar constraint correspondente via Alembic
- [ ] Cobrir uploads concorrentes
- [ ] Definir estratégia de idempotência

### P0.5 — Tratamento seguro de erros

- [ ] Remover detalhes internos das respostas genéricas
- [ ] Adicionar request ID
- [ ] Padronizar códigos de erro
- [ ] Remover `file_path` de contratos públicos

### P0.6 — Lifecycle e configuração

- [ ] Mover inicialização para lifespan do FastAPI
- [ ] Remover ocorrências restantes de `datetime.utcnow()`
- [ ] Concluir migração para Pydantic V2/`ConfigDict`
- [ ] Validar secrets e DEBUG por ambiente
- [ ] Corrigir `get_stale_processing(minutes)`
- [ ] Retirar `Base.metadata.create_all()` do fluxo normal depois da adoção do Alembic

### P0.7 — Qualidade e governança

- [ ] Expandir CI para `develop` e `stack/**`
- [ ] Resolver disparo do GitHub Actions para o fluxo atual de integração
- [ ] Adicionar verificação explícita de migrations ao CI
- [ ] Adicionar Ruff
- [ ] Adicionar type checking
- [ ] Adicionar auditoria de dependências e segurança
- [ ] Proteger `main`
- [ ] Formalizar GitFlow adaptado e Conventional Commits na governança

### P0.8 — Documentação

- [ ] Separar documentação atual, roadmap e archive
- [ ] Sincronizar contrato da API com OpenAPI real
- [ ] Arquivar prompts e documentos históricos obsoletos
- [ ] Revisar deployment e contributing

## Sprint 6B — Jobs persistentes

**Prioridade:** Crítica antes do Whisper

- [ ] Criar modelo e repository de jobs
- [ ] Persistir status, progresso e mensagem de erro
- [ ] Criar job após upload de áudio
- [ ] Endpoint para consultar job por reunião
- [ ] Garantir idempotência
- [ ] Recuperar jobs interrompidos
- [ ] Implementar worker separado
- [ ] Implementar lease, heartbeat, timeout e retry
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
- [ ] Extração de duração
- [ ] Remoção/substituição controlada de áudio
- [ ] Download ou streaming autenticado

## Fases posteriores

- [ ] Autenticação e autorização
- [ ] PostgreSQL para staging/produção multiusuário
- [ ] Storage remoto quando necessário
- [ ] Diarização
- [ ] Análise por LLM
- [ ] Busca textual
- [ ] Exportação Markdown, TXT, DOCX e PDF

**Document Version:** 1.3  
**Last Updated:** 2026-08-16  
**Status:** Active
