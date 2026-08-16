# Documentação do AMIP

A documentação é separada por finalidade para impedir que roadmap ou histórico sejam confundidos com o produto implementado.

## Estado atual

Documentos que descrevem **somente o que existe no código atual**:

- [`current/ARCHITECTURE.md`](current/ARCHITECTURE.md) — arquitetura e limites atuais;
- [`current/DATABASE.md`](current/DATABASE.md) — schema, migrations e política transacional;
- [`current/API.md`](current/API.md) — endpoints HTTP realmente implementados;
- [`current/DEPLOYMENT.md`](current/DEPLOYMENT.md) — execução local e estado real de deploy;
- [`current/CONTRIBUTING.md`](current/CONTRIBUTING.md) — fluxo Git, setup e quality gates atuais.

## Planejamento

Documentos que descrevem **direções futuras**, e não funcionalidades disponíveis:

- [`roadmap/FRONTEND.md`](roadmap/FRONTEND.md) — experiência de usuário planejada;
- [`roadmap/AI_PIPELINE.md`](roadmap/AI_PIPELINE.md) — jobs, transcrição, diarização e LLM planejados;
- [`06_BACKLOG.md`](06_BACKLOG.md) — backlog operacional e ordem de execução.

## Decisões arquiteturais

- [`adr/`](adr/) — ADRs aceitos e histórico de decisões.
- [`../TECH_DECISIONS.md`](../TECH_DECISIONS.md) — registro resumido das decisões vigentes.

## Histórico

- [`archive/README.md`](archive/README.md) — documentos de Sprints antigas, prompts históricos e materiais superseded.

Itens em `archive/` não devem ser usados como especificação atual.

## Documentos raiz de governança

- [`../PROJECT_CONTEXT.md`](../PROJECT_CONTEXT.md) — visão, escopo e capacidade atual;
- [`../PROJECT_GOVERNANCE.md`](../PROJECT_GOVERNANCE.md) — regras obrigatórias de engenharia;
- [`../PROJECT_STATE.MD`](../PROJECT_STATE.MD) — estado operacional mais recente;
- [`../README.md`](../README.md) — entrada principal do repositório.

---

**Regra:** quando houver dúvida sobre o que está implementado, prevalecem o código, OpenAPI, migrations, testes/CI e os documentos em `docs/current/`.
