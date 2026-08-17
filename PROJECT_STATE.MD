# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 9 — Empacotamento para uso interno  
**Branch de integração:** `develop`  
**Último merge:** PR #12 — Sprint 8  
**Commit de integração:** `01b1065b00d6f18a725e2b0bbdf2b3b7c41f96be`  
**Status:** Sprint 8 concluída e integrada; próxima prioridade é empacotamento operacional

## Baseline

A Sprint 7 fornece transcrição real local com `faster-whisper`, persistência de texto/segmentos e processamento durável.

A Sprint 8 foi integrada em `develop` pelo PR #12 e entrega o primeiro fluxo humano ponta a ponta do AMIP.

## Sprint 8 — concluída

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
- [x] versão da aplicação elevada para 0.5.0;
- [x] CI verde no PR #12;
- [x] Quality verde no PR #12;
- [x] merge na `develop` concluído.

## Fluxo humano entregue

`listar/criar reunião → abrir detalhe → enviar áudio → iniciar transcrição → acompanhar job → visualizar transcrição e segmentos`

A aplicação web continua separada do worker: a interface apenas cria e consulta jobs persistentes; o processamento pesado permanece fora do processo HTTP.

## Próxima prioridade — Sprint 9

**Empacotamento para uso interno:**

1. Dockerfile;
2. Compose com migrations + web + worker;
3. volumes persistentes para SQLite, storage e cache do modelo;
4. ffmpeg/ffprobe disponíveis no ambiente;
5. comandos simples para iniciar/parar/atualizar;
6. smoke test operacional do fluxo completo;
7. documentação de backup e recuperação básica.

## Ainda posterior

- diarização de speakers;
- identificação de participantes;
- análise por LLM, resumos e action items;
- autenticação/autorização;
- PostgreSQL quando necessário;
- deploy público production-ready.

**Document Version:** 5.1  
**Status:** Active
