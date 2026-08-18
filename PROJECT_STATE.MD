# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-18  
**Stack atual:** Stack 17 — Gravação por microfone  
**Branch de integração:** `develop`  
**Branch da Stack 16:** `agent/stack-16-export`  
**Status esperado após gate/merge:** Stacks 7–16 concluídas; Stack 17 é a próxima prioridade

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando configurado;
- identificação/confirmação de participantes;
- inteligência estruturada local via Ollama + Qwen3;
- autenticação, sessões revogáveis e ownership;
- baseline de produção com PostgreSQL, migrations, web, worker e backups;
- busca textual ownership-aware em título, descrição e transcrição;
- exportação sob demanda em TXT, Markdown, JSON, DOCX e PDF.

## Stack 16 — Exportação — IMPLEMENTADA

- [x] `ExportService` dedicado;
- [x] pacote unificado com metadados, participantes, transcrição e análise;
- [x] exportação TXT;
- [x] exportação Markdown;
- [x] exportação JSON estruturado;
- [x] exportação DOCX editável;
- [x] exportação PDF para distribuição;
- [x] funcionamento mesmo com transcrição/análise ainda ausentes;
- [x] isolamento por `owner_id` antes da geração do arquivo;
- [x] `GET /api/meetings/{meeting_id}/export?format=...`;
- [x] `Content-Disposition` para download;
- [x] arquivos gerados em memória, sem duplicação em storage;
- [x] testes de formatos, dados incompletos e ownership;
- [x] ADR-031;
- [x] versão 0.12.0;
- [ ] CI + Quality + Docker verdes;
- [ ] PR integrado em `develop`.

## Decisão de evolução

Exports são gerados sob demanda e não persistidos. Isso evita cópias redundantes e problemas de sincronização. Caso documentos muito grandes se tornem comuns, geração assíncrona/streaming poderá ser adicionada mantendo o contrato funcional.

## Próximas stacks

1. Stack 17 — gravação por microfone.

## Pendências operacionais independentes

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test com áudio real/modelos baixados na máquina de uso;
- configurar destino off-host para backups no ambiente de produção escolhido;
- configurar proxy/TLS e monitor externo no ambiente de produção escolhido;
- branch protection administrativa da `main` quando permissões permitirem.

## Próxima Stack

Após gate/merge da Stack 16, **Stack 17 — Gravação por microfone** é a próxima prioridade.

**Document Version:** 12.0  
**Status:** Active
