# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 8 — Interface utilizável  
**Branch:** `agent/sprint-8-interface`  
**Branch de integração:** `develop`  
**Status:** implementação da interface ponta a ponta concluída; validação por PR/CI em andamento

## Baseline

A Sprint 7 está integrada em `develop` pelo PR #11 e fornece transcrição real local com `faster-whisper`, persistência de texto/segmentos e processamento durável.

## Sprint 8 — implementada na branch

- [x] página de listagem de reuniões em `/meetings`;
- [x] criação de reunião pela interface;
- [x] página de detalhe em `/meetings/{id}`;
- [x] upload de áudio pela interface;
- [x] início do job `TRANSCRIBE` pela interface;
- [x] acompanhamento de status e progresso do job por polling;
- [x] exibição de falha do job;
- [x] consulta automática da transcrição concluída;
- [x] visualização do texto completo;
- [x] visualização dos segmentos com timestamps;
- [x] interface responsiva baseada em Jinja2 + Bootstrap + JavaScript mínimo;
- [x] reaproveitamento das APIs e services existentes, sem duplicar regras de negócio;
- [x] testes das novas rotas web;
- [x] versão da aplicação elevada para 0.5.0.

## Fluxo humano entregue

`listar/criar reunião → abrir detalhe → enviar áudio → iniciar transcrição → acompanhar job → visualizar transcrição e segmentos`

A aplicação web continua separada do worker: a interface apenas cria e consulta jobs persistentes; o processamento pesado permanece fora do processo HTTP.

## Gate final da Sprint 8

1. executar CI + Quality da branch/PR;
2. corrigir qualquer regressão;
3. mergear em `develop` somente com gates verdes;
4. validar pós-merge.

## Próxima prioridade após o fechamento

**Sprint 9 — Empacotamento para uso interno:** Dockerfile, Compose, migrations, web + worker, volumes persistentes, ffmpeg/ffprobe e documentação operacional.

## Ainda posterior

- diarização de speakers;
- identificação de participantes;
- análise por LLM, resumos e action items;
- autenticação/autorização;
- PostgreSQL quando necessário;
- deploy público production-ready.

**Document Version:** 5.0  
**Status:** Active
