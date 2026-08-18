# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-17  
**Stack atual:** Stack 16 — Exportação  
**Branch de integração:** `develop`  
**Branch da Stack 15:** `agent/stack-15-search`  
**Status esperado após gate/merge:** Stacks 7–15 concluídas; Stack 16 é a próxima prioridade

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
- interface e API de busca com snippet contextual.

## Stack 15 — Busca — IMPLEMENTADA

- [x] `SearchService` dedicado;
- [x] busca em título e descrição;
- [x] busca no texto integral das transcrições;
- [x] isolamento por `owner_id` antes da entrega de resultados;
- [x] `GET /api/search` com paginação;
- [x] indicação dos campos que produziram o match;
- [x] snippet contextual para conteúdo encontrado;
- [x] campo de busca na interface `/meetings`;
- [x] SQLite e PostgreSQL suportados sem serviço externo;
- [x] testes de busca, transcrição e isolamento;
- [x] ADR-030;
- [x] versão 0.11.0;
- [ ] CI + Quality + Docker verdes;
- [ ] PR integrado em `develop`.

## Decisão de evolução

O baseline usa SQL portável para preservar paridade entre desenvolvimento/testes e produção. PostgreSQL Full Text Search (`tsvector`/GIN) será introduzido quando métricas/volume justificarem. Vector database não será adicionado sem requisito de busca semântica comprovado.

## Próximas stacks

1. Stack 16 — exportação;
2. Stack 17 — gravação por microfone.

## Pendências operacionais independentes

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test com áudio real/modelos baixados na máquina de uso;
- configurar destino off-host para backups no ambiente de produção escolhido;
- configurar proxy/TLS e monitor externo no ambiente de produção escolhido;
- branch protection administrativa da `main` quando permissões permitirem.

## Próxima Stack

Após gate/merge da Stack 15, **Stack 16 — Exportação** é a próxima prioridade.

**Document Version:** 11.0  
**Status:** Active
