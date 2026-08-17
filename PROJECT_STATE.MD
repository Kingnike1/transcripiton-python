# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-17  
**Stack atual:** Stack 13 — Autenticação e autorização  
**Branch de integração:** `develop`  
**Stack 12:** inteligência por LLM implementada em `agent/stack-12-llm-intelligence`  
**Status esperado após gate/merge:** Stacks 7–12 concluídas; Stack 13 é a próxima prioridade

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando configurado;
- identificação/confirmacão de participantes por reunião;
- inteligência estruturada local via Ollama + Qwen3 configurável;
- resumo, action items, decisões, riscos, perguntas abertas e follow-ups;
- saída do LLM validada por Pydantic/JSON Schema;
- evidências com speaker/timestamps/citação para rastreabilidade;
- provider/modelo persistidos junto à análise;
- job durável `SUMMARIZE` fora do request HTTP;
- API de consulta da análise;
- Docker/Compose com migrations, web e worker.

## Stack 12 — Inteligência por LLM — IMPLEMENTADA

- [x] provider local Ollama desacoplado;
- [x] baseline `qwen3:4b`, configurável por ambiente;
- [x] structured outputs via JSON Schema;
- [x] validação Pydantic antes de persistir;
- [x] transcript grounded com timestamps, speaker labels e nomes confirmados;
- [x] resumo estruturado;
- [x] action items e responsáveis;
- [x] decisões;
- [x] riscos;
- [x] perguntas abertas e follow-ups;
- [x] evidências/rastreabilidade;
- [x] persistência do provider/modelo;
- [x] job `SUMMARIZE` no worker durável;
- [x] API `GET /api/meetings/{id}/analysis`;
- [x] migration `0008_analysis_provider_metadata`;
- [x] testes com provider fake;
- [x] ADR-027.

## Próximas stacks

1. Stack 13 — autenticação/autorização;
2. Stack 14 — infraestrutura de produção;
3. Stack 15 — busca;
4. Stack 16 — exportação;
5. Stack 17 — gravação por microfone.

## Pendências operacionais independentes

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test com áudio real/modelos baixados na máquina de uso;
- branch protection administrativa da `main` quando permissões permitirem.

## Próxima Stack

**Stack 13 — Autenticação e autorização** deve introduzir usuários/login e ownership/autorização por recurso sem quebrar o modo local atual.

**Document Version:** 8.0  
**Status:** Active
