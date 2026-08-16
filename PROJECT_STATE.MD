# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack atual:** P0.8 — Organização documental  
**Branch:** `agent/stack-p0-8-documentation`  
**Branch base / integração:** `develop`  
**Head base verde:** `af4b4a5946f0633e733dcc0a4072629ee5c77031`  
**Status:** P0.1–P0.7 integradas em `develop`; P0.8 em execução

## Baseline

P0.1–P0.7 estão integradas em `develop` pelos PRs #2–#8.

A P0.7 passou em CI e Quality no PR e novamente após merge em `develop`:

- Python 3.11: suíte completa + cobertura >=80%;
- Python 3.12: suíte completa;
- Ruff: verde;
- mypy: verde;
- migrations: verdes;
- Bandit: verde;
- `pip-audit`: sem vulnerabilidades conhecidas no runtime.

`main` permanece como release estável anterior à Sprint 6A. A proteção administrativa da `main` continua recomendada, mas não pôde ser configurada pela integração atual (403).

## Estado das stacks P0

| Stack | Estado |
|---|---|
| P0.1 — Unit of Work | Integrada em `develop` |
| P0.2 — Alembic | Integrada em `develop` |
| P0.3 — Upload streaming | Integrada em `develop` |
| P0.4 — Concorrência de áudio | Integrada em `develop` |
| P0.5 — Erros seguros/request ID | Integrada em `develop` |
| P0.6 — Lifecycle/configuração | Integrada em `develop` |
| P0.7 — Qualidade/governança | Integrada em `develop` |
| P0.8 — Organização documental | Em execução |

---

## P0.8 — Organização documental

### Objetivo

Eliminar documentação contraditória antes da Sprint 6B e separar claramente:

```text
docs/current/  → implementação real
docs/roadmap/  → futuro planejado
docs/archive/  → histórico/superseded
docs/adr/      → decisões arquiteturais
```

### Implementado até agora

- [x] `docs/README.md` com mapa e regra de fonte da verdade.
- [x] `docs/current/ARCHITECTURE.md`.
- [x] `docs/current/DATABASE.md`.
- [x] `docs/current/API.md`.
- [x] `docs/current/DEPLOYMENT.md` reescrito sem Docker/cloud fictícios.
- [x] `docs/current/CONTRIBUTING.md` alinhado ao GitFlow/Quality atual.
- [x] `docs/roadmap/FRONTEND.md` explicitamente planejado.
- [x] `docs/roadmap/AI_PIPELINE.md` explicitamente planejado e dependente de jobs persistentes.
- [x] `docs/archive/` criado para histórico.
- [x] registros de prompts antigos e Sprints 4/5 arquivados com baseline Git preservada.
- [x] `PROJECT_CONTEXT.md` reescrito com matriz de capacidade real.
- [x] `README.md` reescrito para não anunciar transcrição/LLM/export como funcionalidades entregues.
- [x] `docs/00_PROJECT_OVERVIEW.md` reescrito.
- [x] `PROJECT_GOVERNANCE.md` atualizado para a nova taxonomia documental.

### Pendente

- [ ] atualizar `docs/06_BACKLOG.md` com fechamento P0.7/P0.8;
- [ ] registrar decisão técnica da taxonomia documental;
- [ ] remover caminhos antigos `docs/01..05`, `07..09` após atualizar referências;
- [ ] remover documentos históricos antigos da raiz/docs após catálogo em `archive/`;
- [ ] procurar links/referências quebradas para paths antigos;
- [ ] validar CI + Quality;
- [ ] PR para `develop`;
- [ ] merge + CI/Quality pós-merge.

---

## Capacidade atual do produto

### Funcional

- API CRUD de reuniões;
- upload/armazenamento de áudio;
- streaming/staging + limite;
- `ffprobe` e metadados;
- Unit of Work;
- Alembic;
- integridade de áudio concorrente;
- erros sanitizados/request ID;
- lifecycle/configuração segura;
- CI/Quality completo.

### Ainda não funcional

- jobs persistentes/worker;
- transcrição real;
- diarização;
- análise por LLM;
- UI completa;
- autenticação/autorização;
- busca/exportação;
- produção pública multiusuário.

## Próxima etapa após P0.8

**Sprint 6B — Jobs persistentes**.

Essa Sprint é o último grande pré-requisito estrutural antes da primeira transcrição real.

**Document Version:** 2.5  
**Status:** Active
