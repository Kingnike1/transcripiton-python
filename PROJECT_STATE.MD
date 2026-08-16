# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack atual:** P0.6 — Lifecycle e configuração  
**Branch:** `agent/stack-p0-6-lifecycle-config`  
**Branch base / integração:** `develop`  
**PR:** #7  
**Status:** P0.6 implementada e validada; aguardando quality gate do head documental final antes do merge em `develop`

## Baseline integrada

P0.1–P0.5 estão integradas em `develop` pelos PRs #2–#6.

O head `5eb893c4014d089902eb507c3055253c65cc4e65` de `develop` passou no GitHub Actions com:

- 114 testes aprovados;
- cobertura total de 87,04%;
- gate mínimo de 80% aprovado.

`main` permanece fora da integração até uma etapa futura de release.

---

## P0.1–P0.5

| Stack | Estado |
|---|---|
| P0.1 — Unit of Work | Integrada em `develop` |
| P0.2 — Alembic | Integrada em `develop` |
| P0.3 — Upload streaming | Integrada em `develop` |
| P0.4 — Concorrência de áudio | Integrada em `develop` |
| P0.5 — Erros seguros/request ID | Integrada em `develop` |

---

## P0.6 — Lifecycle e configuração

### Implementado

- [x] `init_db()` removido do startup/import normal.
- [x] `Base.metadata.create_all()` removido do fluxo normal da aplicação.
- [x] Alembic mantido como fonte oficial de schema; deployment usa `alembic upgrade head` explicitamente.
- [x] FastAPI lifespan criado para lifecycle de recursos.
- [x] `engine.dispose()` executado no shutdown.
- [x] `reset_db()` restrito a `development/test`.
- [x] assinatura moderna de `TemplateResponse`.
- [x] `AMIPBaseSettings` com `SettingsConfigDict`.
- [x] settings modulares migrados para Pydantic V2.
- [x] `MeetingResponse` migrado para `ConfigDict`.
- [x] `ENVIRONMENT` adicionado (`development/test/staging/production`).
- [x] staging/produção rejeitam `DEBUG=true`.
- [x] staging/produção rejeitam `SECRET_KEY` curta/placeholder.
- [x] `.env.example` atualizado.
- [x] `utc_now()` criado como relógio comum.
- [x] usos conhecidos de `datetime.utcnow()` removidos dos models legados.
- [x] `MeetingService`/`AudioService` alinhados ao relógio comum.
- [x] `get_stale_processing(minutes)` corrigido para respeitar o limiar.
- [x] stale query usa `ProcessingStatus` em vez de strings duplicadas.
- [x] testes de import sem criação de banco.
- [x] teste de descarte do engine no shutdown.
- [x] teste de proteção de `reset_db()`.
- [x] testes de configuração insegura/segura de produção.
- [x] testes de stale threshold.
- [x] ADR-022.
- [x] arquitetura, banco, decisões técnicas e backlog atualizados.
- [x] PR #7 criado para `develop`.

### Quality gate

Run #113 no commit `993965c6fd5499560f4577f56b1c1524c5de776d`:

- **122 testes aprovados**;
- **0 falhas**;
- **87,29% de cobertura**;
- gate >=80% aprovado;
- **0 warnings do pytest**.

Os 9 warnings da baseline (Pydantic class-based Config + TemplateResponse legado) foram eliminados.

### Decisão temporal

A aplicação produz timestamps semanticamente em UTC por `utc_now()`. Não foi criada migration apenas para `DateTime(timezone=True)`, pois SQLite não preserva `tzinfo` de forma equivalente a PostgreSQL. Esse ponto será reavaliado junto da migração para PostgreSQL.

### Pendente

- [ ] CI do head final após esta sincronização documental.
- [ ] marcar PR #7 pronto para review.
- [ ] merge em `develop`.
- [ ] CI pós-merge em `develop`.

---

## Próxima stack

**P0.7 — Qualidade e governança**

Prioridades:

- migration check explícito no CI;
- Ruff;
- type checking;
- auditoria de dependências/segurança;
- proteção de `main`;
- atualizar governança para GitFlow adaptado + Conventional Commits;
- alinhar Python documentado com a versão realmente suportada/testada;
- atualizar actions cujo runtime está em depreciação.

Depois: P0.8 documental → Sprint 6B Jobs persistentes.

**Document Version:** 2.2  
**Status:** Active
