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
- [x] Validação de extensão e MIME type
- [x] Validação de assinatura binária básica
- [x] Limite de tamanho e rejeição de arquivo vazio
- [x] Nome físico com UUID
- [x] Compensação de arquivo em falha de banco
- [x] Rejeição de upload duplicado
- [x] Testes unitários e de integração
- [x] CI com cobertura mínima de 80%

## Próxima Sprint — Jobs persistentes

**Prioridade:** Crítica

- [ ] Criar modelo e repository de jobs
- [ ] Persistir status, progresso e mensagem de erro
- [ ] Criar job após upload de áudio
- [ ] Endpoint para consultar job por reunião
- [ ] Garantir idempotência
- [ ] Recuperar jobs interrompidos
- [ ] Testes de concorrência e transição de estado
- [ ] Documentar estratégia de retry

## Transcrição

- [ ] Implementar provider Whisper atrás de `ITranscriber`
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

- [ ] Diarização com pyannote
- [ ] Resumos e itens de ação por LLM
- [ ] Busca textual
- [ ] Exportação Markdown, PDF, TXT e DOCX
- [ ] Autenticação e autorização
- [ ] PostgreSQL e storage remoto

## Dívida técnica priorizada

| Item | Prioridade |
|---|---|
| Mover inicialização do banco para lifespan | Média |
| Remover detalhes internos do handler genérico | Alta |
| Substituir fila em memória antes do Whisper | Crítica |
| Adicionar migrations Alembic ao fluxo de entrega | Alta |
| Proteger branch `main` com CI obrigatório | Alta |

**Document Version:** 1.1  
**Last Updated:** 2026-08-04  
**Status:** Active
