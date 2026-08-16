# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack atual:** P0.7 — Qualidade e governança  
**Branch:** `agent/stack-p0-7-quality-governance`  
**Branch base / integração:** `develop`  
**Head base:** `d2966cbc02125876df86f6cc358c6fe55fc48bff`  
**Status:** P0.1–P0.6 integradas em `develop`; P0.7 em execução

## Baseline validada

P0.1–P0.6 estão integradas em `develop` pelos PRs #2–#7.

A P0.6 passou no quality gate do PR com 122 testes, 87,29% de cobertura e zero warnings do pytest. O CI pós-merge em `develop` também concluiu com sucesso.

`main` permanece sem receber a Sprint 6A; a promoção para `main` será tratada como release controlada após o fechamento da estabilização.

## Estado das stacks P0

| Stack | Estado |
|---|---|
| P0.1 — Unit of Work | Integrada em `develop` |
| P0.2 — Alembic | Integrada em `develop` |
| P0.3 — Upload streaming | Integrada em `develop` |
| P0.4 — Concorrência de áudio | Integrada em `develop` |
| P0.5 — Erros seguros/request ID | Integrada em `develop` |
| P0.6 — Lifecycle/configuração | Integrada em `develop` |
| P0.7 — Qualidade/governança | Em execução |
| P0.8 — Organização documental | Planejada |

---

## P0.7 — Qualidade e governança

### Objetivo

Transformar o CI em um quality gate reproduzível para código, tipos, migrations e segurança antes da Sprint 6B, e formalizar o fluxo Git já adotado pelo projeto.

### Decisões iniciais

- Python 3.11 continua como baseline mínima atualmente comprovada.
- Python 3.12 será testado no CI antes de ser declarado oficialmente suportado.
- `actions/checkout` e `actions/setup-python` serão atualizados para v6, que usam Node 24 e são compatíveis com o runner hospedado atual.
- Ruff será o linter principal.
- mypy será o type checker inicial por ser nativo do ecossistema Python e não exigir Node.
- Bandit será gate bloqueante para achados de severidade média/alta.
- `pip-audit` entrará inicialmente como auditoria visível; vulnerabilidades existentes em pins legados serão analisadas antes de qualquer upgrade amplo de framework.
- migrations terão um gate explícito além da suíte geral.

### Em execução

- [ ] Criar configuração de Ruff e mypy.
- [ ] Criar dependências de desenvolvimento reproduzíveis.
- [ ] Atualizar Actions para runtime Node 24.
- [ ] Testar Python 3.11 e 3.12.
- [ ] Adicionar lint bloqueante.
- [ ] Adicionar type checking bloqueante.
- [ ] Adicionar migration check explícito.
- [ ] Adicionar Bandit bloqueante para medium/high.
- [ ] Executar `pip-audit` e classificar o passivo real de dependências.
- [ ] Corrigir violações descobertas pelos novos gates.
- [ ] Atualizar `PROJECT_GOVERNANCE.md` para GitFlow adaptado e Conventional Commits.
- [ ] Alinhar a versão Python documentada à matriz realmente validada.
- [ ] Verificar/proteger `main` se a API disponível permitir a alteração segura.
- [ ] Registrar ADR/decisão técnica e atualizar backlog/arquitetura.
- [ ] PR + CI verde + merge em `develop`.

## Limites da P0.7

Não serão feitos upgrades amplos de FastAPI/SQLAlchemy/Pydantic apenas para satisfazer scanner sem análise de compatibilidade. Vulnerabilidades reais serão classificadas e, quando exigirem upgrade estrutural, receberão plano explícito e testes próprios.

P0.8 continuará responsável por reorganizar documentos históricos e atualizar documentos de contexto ainda antigos.

## Próxima etapa após P0.7

**P0.8 — Organização documental**, seguida pela **Sprint 6B — Jobs persistentes**.

**Document Version:** 2.3  
**Status:** Active
