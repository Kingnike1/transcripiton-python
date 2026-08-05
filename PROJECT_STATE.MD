# PROJECT_STATE.MD

## Current Project Status

**Project:** AI Meeting Intelligence Platform (AMIP)  
**Last Updated:** 2026-08-04  
**Current Sprint:** Sprint 5 — Upload e Armazenamento Seguro de Áudio  
**Branch:** `agent/sprint-5-audio-upload`  
**Status:** Implementada; aguardando validação do CI e merge

## Fases

| Fase | Status | Observação |
|---|---|---|
| Fundação | Concluída | FastAPI, banco, testes e UI básica |
| Arquitetura central | Concluída | Repository, Service Layer, pipeline e jobs |
| Refatoração arquitetural | Concluída | Config, exceções, logging e providers |
| Módulo de áudio | Em andamento | Upload, validação, storage e metadados implementados; UI e microfone pendentes |
| Transcrição | Não iniciada | Próxima fase após jobs persistentes |
| Diarização | Não iniciada | Depende de transcrição |
| Análise por IA | Não iniciada | Depende de transcrição/diarização |
| Busca | Não iniciada | Planejada |
| Exportação | Não iniciada | Planejada |

## Sprint 5 — Entregas

- [x] Endpoint `POST /api/meetings/{meeting_id}/audio`
- [x] Endpoint `GET /api/meetings/{meeting_id}/audio`
- [x] `AudioRepository`
- [x] `AudioService` com transação e compensação de arquivo
- [x] `AudioValidator` para nome, extensão, MIME, tamanho e assinatura binária
- [x] Persistência de metadados no modelo `Audio`
- [x] Transição `CREATED/RECORDING -> AUDIO_UPLOADED`
- [x] Rejeição de upload duplicado
- [x] Testes unitários e de integração
- [x] Workflow de CI com cobertura mínima de 80%
- [x] Documentação e ADR atualizados
- [ ] UI de upload
- [ ] Gravação por microfone
- [ ] Extração de duração do áudio

## Decisões Técnicas

- O `AudioService` controla a unidade de trabalho.
- Repositories não executam commit no fluxo de upload.
- Arquivos são armazenados com UUID fora de `static/`.
- Falhas de banco removem o arquivo salvo.
- Whisper permanece fora desta Sprint.

## Riscos e Dívida Técnica

| Item | Prioridade | Tratamento |
|---|---|---|
| `init_db()` ainda ocorre durante importação | Média | Migrar para lifespan do FastAPI |
| Fila de jobs em memória | Alta antes do Whisper | Implementar job persistente na próxima Sprint |
| Handler genérico inclui detalhes internos | Alta | Remover detalhes da resposta antes de produção |
| Validação binária é intencionalmente básica | Média | Avaliar `ffprobe`/biblioteca especializada futuramente |
| SQLite limita concorrência | Média | Manter no MVP e planejar PostgreSQL |

## Próxima Sprint Recomendada

**Sprint 6 — Jobs persistentes e acompanhamento de processamento**

Objetivo: criar um job transacional após upload, persistir status/progresso/erro e fornecer endpoint de consulta. Isso prepara a integração do Whisper sem bloquear workers HTTP.

## Quality Gate

- Todos os testes devem passar no GitHub Actions.
- Cobertura deve permanecer em pelo menos 80%.
- A branch só deve ser integrada após CI verde.

**Document Version:** 1.4  
**Status:** Active
