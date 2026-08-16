# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack atual:** P0.7 — Qualidade e governança  
**Branch:** `agent/stack-p0-7-quality-governance`  
**Branch base / integração:** `develop`  
**Head base:** `d2966cbc02125876df86f6cc358c6fe55fc48bff`  
**Status:** P0.7 implementada; aguardando quality gate do head documental final, PR e merge em `develop`

## Baseline

P0.1–P0.6 estão integradas em `develop` pelos PRs #2–#7. O CI pós-merge da P0.6 concluiu com sucesso.

`main` permanece como release estável anterior à Sprint 6A e não receberá mudanças automaticamente por Stack.

## Estado das stacks P0

| Stack | Estado |
|---|---|
| P0.1 — Unit of Work | Integrada em `develop` |
| P0.2 — Alembic | Integrada em `develop` |
| P0.3 — Upload streaming | Integrada em `develop` |
| P0.4 — Concorrência de áudio | Integrada em `develop` |
| P0.5 — Erros seguros/request ID | Integrada em `develop` |
| P0.6 — Lifecycle/configuração | Integrada em `develop` |
| P0.7 — Qualidade/governança | Implementada, fechamento pendente |
| P0.8 — Organização documental | Planejada |

---

## P0.7 — Qualidade e governança

### Implementado

- [x] `actions/checkout@v6` e `actions/setup-python@v6` em CI/Quality.
- [x] CI principal em Python 3.11 com cobertura mínima de 80%.
- [x] workflow `Quality` independente.
- [x] Python 3.12 como compatibilidade obrigatória.
- [x] Ruff bloqueante para `F`/`E9`.
- [x] mypy bloqueante para `app` e `main.py`.
- [x] migration integrity explícito.
- [x] Bandit bloqueante para severidade média/alta.
- [x] `pip-audit -r requirements.txt` bloqueante.
- [x] `requirements.txt` reduzido ao runtime realmente utilizado.
- [x] `requirements-dev.txt` separado para testes e quality tooling.
- [x] dependências de exportação ainda não implementada removidas do runtime.
- [x] runtime HTTP/configuração atualizado de forma direcionada e validado.
- [x] TestClient migrado de `httpx` para `httpx2`.
- [x] bind padrão alterado de `0.0.0.0` para `127.0.0.1`.
- [x] contratos/typing corrigidos até o mypy retornar zero issues em 61 source files.
- [x] Ruff e Bandit sem achados bloqueantes.
- [x] migrations: 6 testes dedicados aprovados.
- [x] auditoria de dependências: `No known vulnerabilities found`.
- [x] GitFlow adaptado formalizado.
- [x] Conventional Commits formalizado.
- [x] suporte oficial alinhado a Python 3.11/3.12 testados.
- [x] `PROJECT_GOVERNANCE.md` atualizado.
- [x] ADR-023, arquitetura, decisões e backlog atualizados.

### Auditoria de dependências

A primeira execução de `pip-audit` encontrou **27 advisories em 7 pacotes**. A remediação não foi um upgrade cego:

1. dependências de teste foram separadas do runtime;
2. bibliotecas de exportação ainda inexistentes foram removidas;
3. o núcleo HTTP/configuração afetado foi atualizado;
4. toda regressão foi validada em Python 3.11 e 3.12;
5. o audit final do runtime retornou **No known vulnerabilities found**.

### Quality já comprovado antes do head documental final

- Ruff: verde;
- mypy: `Success: no issues found in 61 source files`;
- migrations: 6/6 aprovadas;
- Bandit: verde;
- pip-audit: sem vulnerabilidades conhecidas;
- Python 3.12: suíte completa verde;
- Python 3.11: 122 testes verdes e cobertura >87%.

A última depreciação conhecida de status HTTP 422 foi corrigida para `HTTP_422_UNPROCESSABLE_CONTENT`.

### Limitação administrativa — branch protection

A consulta ao endpoint de proteção da `main` retornou **403** com a permissão disponível à integração e não existe ferramenta autorizada de ruleset/branch-protection neste ambiente.

Portanto:

- a proteção da `main` continua recomendada;
- **não é correto afirmar que ela esteja protegida**;
- o item fica registrado como controle administrativo externo pendente;
- isso não justifica desativar ou ignorar os quality gates automatizados.

### Pendente para fechamento

- [ ] CI + Quality do head final após documentação, 422 atual e `pip-audit` bloqueante.
- [ ] criar PR P0.7 → `develop`.
- [ ] marcar PR pronto após gates verdes.
- [ ] merge em `develop`.
- [ ] CI + Quality pós-merge em `develop`.

---

## Próxima etapa

**P0.8 — Organização documental**

Depois da P0.8, a próxima fase crítica é **Sprint 6B — Jobs persistentes**.

**Document Version:** 2.4  
**Status:** Active
