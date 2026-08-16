# PROJECT_GOVERNANCE.md

## Objetivo

Este documento define as regras obrigatórias de engenharia, Git, qualidade e documentação do AMIP. Antes de qualquer Stack, a equipe deve ler este arquivo, `PROJECT_CONTEXT.md`, `PROJECT_STATE.MD`, `TECH_DECISIONS.md`, arquitetura, banco, API, backlog e ADRs relevantes.

A regra central é: **nenhuma implementação começa diretamente pelo código**. Primeiro vem auditoria, análise crítica, plano técnico, riscos, branch e critérios de aceite.

---

## 1. Princípios de engenharia

- manter o AMIP como monólito modular enquanto não houver necessidade comprovada de microservices;
- aplicar KISS/YAGNI e evitar infraestrutura prematura;
- Service Layer concentra casos de uso e transações;
- repositories não fazem `commit()`/`rollback()`;
- routes não contêm SQL nem regras de negócio;
- toda alteração de schema usa Alembic;
- migrations nunca rodam automaticamente no processo web;
- processamento pesado não roda dentro do request HTTP;
- arquivos grandes não devem ser materializados integralmente em memória;
- detalhes internos, secrets, SQL e paths não podem aparecer em respostas públicas;
- decisões arquiteturais relevantes exigem ADR;
- documentação ativa deve representar o código real, não roadmap como se estivesse implementado.

---

## 2. Stack oficialmente suportada

### Backend

- Python **3.11 e 3.12** — ambas precisam permanecer testadas no CI;
- FastAPI;
- SQLAlchemy 2.x;
- Pydantic 2 / pydantic-settings;
- Alembic;
- pytest.

Python 3.11 é a baseline mínima atual. Não declarar `3.12+`, `3.13` ou versões posteriores como suportadas sem CI verde nessa versão.

### Frontend

- Jinja2;
- Bootstrap 5;
- HTMX quando necessário;
- JavaScript mínimo/vanilla.

SPA framework só entra quando a complexidade real justificar.

### Banco e storage

- SQLite: desenvolvimento/testes;
- PostgreSQL: evolução planejada para staging/produção multiusuário;
- filesystem local: MVP/single-server;
- object storage compatível com S3: somente quando múltiplas instâncias justificarem.

### IA

Whisper, pyannote, LLMs e outros providers são direções de produto, não dependências obrigatórias do núcleo. Cada funcionalidade deve começar com um provider concreto atrás de uma interface estável.

---

## 3. Protocolo obrigatório antes de cada Stack

Antes de alterar código:

1. verificar `main`, `develop`, branch atual, PRs e CI;
2. ler governança e estado técnico;
3. comparar documentação com código real;
4. definir objetivo, escopo e fora de escopo;
5. analisar banco, API, services, storage, segurança, performance, concorrência, rollback e compatibilidade;
6. registrar alternativas e trade-offs;
7. definir critérios de aceite e testes;
8. criar branch exclusiva a partir da base correta;
9. somente então implementar.

Quando documentação e código divergirem, a divergência deve ser explicitada e corrigida; documentos antigos não devem ser seguidos cegamente.

---

## 4. Estratégia Git — GitFlow adaptado

### `main`

Representa release estável.

- sem desenvolvimento direto;
- mudanças entram por PR/release;
- CI/Quality precisam estar verdes;
- force push e exclusão devem ser bloqueados quando a proteção de branch estiver configurada.

### `develop`

Branch de integração das Sprints.

- recebe Stacks concluídas por PR;
- deve permanecer verde;
- é a base normal para novas Stacks após integração da dependência anterior.

### Branches de Stack

Padrão atual:

```text
agent/stack-p0-7-quality-governance
agent/stack-p0-8-documentation
agent/sprint-6b-persistent-jobs
```

Branches adicionais permitidas:

```text
fix/<descricao>
hotfix/<descricao>
release/<versao>
```

Hotfix nasce da `main` e deve retornar também para `develop` quando aplicável.

---

## 5. Conventional Commits

Formato padrão:

```text
feat: add persistent job model
fix: persist stale-processing threshold
refactor: centralize transaction ownership
test: cover concurrent uploads
docs: update current API contract
chore: pin quality tooling
ci: add migration quality gate
```

Tipos preferidos:

- `feat`
- `fix`
- `refactor`
- `test`
- `docs`
- `chore`
- `ci`
- `perf`

Commits devem ser pequenos, coerentes e reversíveis. Não usar mensagens genéricas como `update`, `changes` ou `fix stuff`.

---

## 6. Quality gates

Uma Stack não é concluída apenas porque o código foi escrito.

Antes de merge em `develop`, devem passar os gates aplicáveis:

### Testes

```bash
pytest --cov=app --cov-fail-under=80 tests/
```

Cobertura global mínima: **80%**. Cobertura global não substitui testes dos componentes críticos modificados.

### Ruff

Ruff é o linter oficial. A adoção inicial bloqueia erros semânticos/sintáticos (`F`/`E9`). Formatação/import sorting podem ser ampliados de forma incremental para evitar churn cosmético sem valor funcional.

### mypy

mypy é o type checker oficial inicial. Erros encontrados devem ser corrigidos nos contratos ou justificados tecnicamente; não desativar checks amplos apenas para obter CI verde.

### Migrations

Toda alteração de schema deve passar os testes de migration e comparação com `Base.metadata`.

### Segurança estática

Bandit bloqueia achados de severidade média/alta que sejam aplicáveis ao projeto.

### Dependências

`pip-audit` deve executar no CI. Vulnerabilidades encontradas precisam ser classificadas. Não fazer upgrade amplo/cego de frameworks apenas para zerar scanner; correções devem considerar compatibilidade, exploitabilidade e testes.

### Compatibilidade Python

Python 3.11 e 3.12 devem permanecer verdes. Nova versão só vira oficialmente suportada depois de adicionada ao gate.

---

## 7. Pull Requests e integração

Cada Stack deve ter PR próprio, salvo dependência técnica inseparável devidamente documentada.

PR deve conter:

- objetivo;
- dependências;
- escopo entregue;
- fora de escopo;
- testes/gates;
- migrations, quando houver;
- riscos residuais;
- documentação/ADR alterados.

Fluxo padrão:

```text
develop
  ↓
agent/stack-...
  ↓
PR para develop
  ↓
CI + Quality
  ↓
merge em develop
  ↓
CI pós-merge
```

Promoção para `main` ocorre em release controlada, não automaticamente após cada Stack.

---

## 8. Banco de dados

- SQLAlchemy é o ORM;
- Alembic é a fonte oficial de schema;
- Service Layer possui a transação;
- repositories usam query/add/flush;
- constraints importantes devem existir no banco, não apenas no Python;
- migrations destrutivas exigem backup e plano de rollback;
- não apagar dados automaticamente para resolver conflito de migration;
- `reset_db()` é restrito a desenvolvimento/testes.

---

## 9. Segurança

- nunca commitar `.env`, API keys, tokens ou credenciais;
- staging/produção devem falhar com `DEBUG=true` ou secret inseguro;
- erros públicos devem ser sanitizados;
- logs podem conter contexto técnico, mas não secrets/transcrições sensíveis sem necessidade;
- uploads precisam de limite, validação e storage controlado;
- autenticação/autorização, rate limit, retenção e LGPD são obrigatórios antes de exposição pública multiusuário.

---

## 10. Documentação obrigatória

Atualizar conforme o impacto:

- `PROJECT_STATE.MD` — estado real, branch, PR, CI, riscos e próximo passo;
- `TECH_DECISIONS.md` — decisão técnica ativa;
- `docs/06_BACKLOG.md` — concluído/em andamento/pendente;
- `docs/01_ARCHITECTURE.md` — arquitetura;
- `docs/02_DATABASE.md` — schema/migrations;
- `docs/03_API.md` — contrato HTTP real;
- ADR — decisão arquitetural relevante;
- demais documentos específicos da área.

Decisões superseded/deprecated não devem desaparecer sem histórico; marcar o status e preservar a rastreabilidade.

---

## 11. Definition of Done

Uma Stack só está concluída quando:

- escopo implementado;
- testes relevantes aprovados;
- CI/Quality verdes;
- migrations válidas, quando aplicável;
- segurança revisada;
- documentação sincronizada;
- estado/backlog/decisões atualizados;
- PR revisável e mergeado na branch correta;
- CI pós-merge verde;
- riscos residuais explicitados.

Se algum gate não puder ser executado, a Stack deve permanecer bloqueada ou registrar claramente a exceção e o responsável pela resolução.

---

## 12. Release

Versionamento segue SemVer (`MAJOR.MINOR.PATCH`).

Antes de promover `develop` para `main`:

- CI e Quality verdes;
- migrations testadas;
- documentação/release notes atualizadas;
- secrets/configuração de ambiente validados;
- backup/rollback definidos quando houver mudança de dados;
- smoke test realizado no ambiente alvo.

---

**Document Version:** 2.0  
**Last Updated:** 2026-08-16  
**Status:** Active
