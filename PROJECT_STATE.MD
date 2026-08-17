# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-17  
**Stack atual:** Stack 14 — Infraestrutura de produção  
**Branch de integração:** `develop`  
**Branch da Stack 14:** `agent/stack-14-production-infra`  
**Último merge:** PR #17 — Stack 13 Autenticação e autorização  
**Status:** Stack 14 implementada; aguardando gates e merge

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando configurado;
- identificação/confirmação de participantes;
- inteligência estruturada local via Ollama + Qwen3;
- autenticação, sessões revogáveis e ownership;
- Docker/Compose para desenvolvimento;
- baseline de produção com PostgreSQL, migrations one-shot, web, worker e backups;
- readiness dependente do banco e liveness HTTP;
- pooling/pre-ping de conexão para banco não-SQLite;
- runbook de deploy, restore, observabilidade e hardening.

## Stack 14 — Infraestrutura de produção — IMPLEMENTADA

- [x] PostgreSQL 16 como banco de produção;
- [x] SQLite preservado para desenvolvimento/testes;
- [x] driver `psycopg`;
- [x] pool SQLAlchemy configurável e `pool_pre_ping`;
- [x] `compose.production.yaml` sem exposição pública do PostgreSQL;
- [x] migrations Alembic executadas antes de web/worker;
- [x] storage persistente compartilhado entre web/worker;
- [x] `/health` para liveness;
- [x] `/ready` validando conectividade com banco;
- [x] backup periódico de PostgreSQL e storage;
- [x] retenção configurável;
- [x] runbook de restore e recomendação de cópia off-host;
- [x] hardening operacional documentado;
- [x] ADR-029;
- [x] versão 0.10.0;
- [ ] CI + Quality + Docker verdes;
- [ ] PR integrado em `develop`.

## Próximas stacks

1. Stack 15 — busca;
2. Stack 16 — exportação;
3. Stack 17 — gravação por microfone.

## Pendências operacionais independentes

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test com áudio real/modelos baixados na máquina de uso;
- configurar destino off-host para backups no ambiente de produção escolhido;
- configurar proxy/TLS e monitor externo no ambiente de produção escolhido;
- branch protection administrativa da `main` quando permissões permitirem.

## Próxima Stack

Após o gate/merge da Stack 14, **Stack 15 — Busca** passa a ser a próxima prioridade.

**Document Version:** 10.0  
**Status:** Active
