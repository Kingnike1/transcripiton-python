# PROJECT_GOVERNANCE.md

## Objetivo

Este documento define as regras obrigatórias de engenharia, Git, qualidade e documentação do AMIP. Antes de qualquer Stack, a equipe deve ler este arquivo, `PROJECT_CONTEXT.md`, `PROJECT_STATE.MD`, `TECH_DECISIONS.md`, os documentos relevantes em `docs/current/`, o backlog e os ADRs aplicáveis.

A regra central é: **nenhuma implementação começa diretamente pelo código**. Primeiro vêm auditoria, análise crítica, plano técnico, riscos, branch e critérios de aceite.

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

Python 3.11 é a baseline mínima atual. Não declarar versões posteriores como suportadas sem CI verde nessa versão.

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
3. ler `docs/README.md` e os documentos `docs/current/` afetados;
4. comparar documentação com código real;
5. definir objetivo, escopo e fora de escopo;
6. analisar banco, API, services, storage, segurança, performance, concorrência, rollback e compatibilidade;
7. registrar alternativas e trade-offs;
8. definir critérios de aceite e testes;
9. criar branch exclusiva a partir da base correta;
10. somente então implementar.

Quando documentação e código divergirem, a divergência deve ser explicitada e corrigida; `docs/roadmap/` e `docs/archive/` nunca substituem a documentação atual.

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

Padrão:

```text
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

Exemplos:

```text
feat: add persistent job model
fix: persist stale-processing threshold
refactor: centralize transaction ownership
test: cover concurrent uploads
docs: update current API contract
chore: pin quality tooling
ci: add migration quality gate
```

Tipos preferidos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`.

Commits devem ser pequenos, coerentes e reversíveis. Não usar mensagens genéricas como `update`, `changes` ou `fix stuff`.

---

## 6. Quality gates

Uma Stack não é concluída apenas porque o código foi escrito.

### Testes

```bash
pytest --cov=app --cov-fail-under=80 tests/
```

Cobertura global mínima: **80%**.

### Ruff

Ruff é o linter oficial. A adoção inicial bloqueia erros semânticos/sintáticos (`F`/`E9`).

### mypy

mypy é o type checker oficial inicial. Erros devem ser corrigidos nos contratos ou justificados tecnicamente; não desativar checks amplos para obter CI verde.

### Migrations

Toda alteração de schema deve passar os testes de migration e comparação com `Base.metadata`.

### Segurança estática

Bandit bloqueia achados de severidade média/alta aplicáveis ao projeto.

### Dependências

`pip-audit -r requirements.txt` é bloqueante. Vulnerabilidades precisam ser classificadas e corrigidas com análise de compatibilidade; não fazer upgrades amplos/cegos.

### Compatibilidade Python

Python 3.11 e 3.12 devem permanecer verdes.

---

## 7. Pull Requests e integração

Cada Stack deve ter PR próprio, salvo dependência técnica inseparável documentada.

O PR deve informar objetivo, dependências, escopo, fora de escopo, testes/gates, migrations, riscos residuais e documentação alterada.

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
CI + Quality pós-merge
```

Promoção para `main` ocorre em release controlada.

---

## 8. Banco de dados

- SQLAlchemy é o ORM;
- Alembic é a fonte oficial de schema;
- Service Layer possui a transação;
- repositories usam query/add/flush;
- constraints importantes devem existir no banco;
- migrations destrutivas exigem backup e rollback;
- não apagar dados automaticamente para resolver conflito de migration;
- `reset_db()` é restrito a desenvolvimento/testes.

---

## 9. Segurança

- nunca commitar `.env`, API keys, tokens ou credenciais;
- staging/produção devem falhar com `DEBUG=true` ou secret inseguro;
- erros públicos devem ser sanitizados;
- logs não devem expor secrets/transcrições sensíveis sem necessidade;
- uploads precisam de limite, validação e storage controlado;
- autenticação/autorização, rate limit, retenção e LGPD são obrigatórios antes de exposição pública multiusuário.

---

## 10. Organização da documentação

A partir da P0.8:

- `docs/current/` — **somente implementação atual**;
- `docs/roadmap/` — direções futuras, explicitamente não implementadas;
- `docs/archive/` — histórico e documentos superseded;
- `docs/adr/` — decisões arquiteturais;
- `docs/06_BACKLOG.md` — backlog operacional;
- `docs/00_PROJECT_OVERVIEW.md` e `docs/README.md` — visão/mapa.

Atualizar conforme o impacto:

- `PROJECT_STATE.MD` — estado real, branch, PR, CI, riscos e próximo passo;
- `PROJECT_CONTEXT.md` — visão e capacidade atual;
- `TECH_DECISIONS.md` — decisão técnica ativa;
- `docs/06_BACKLOG.md` — concluído/em andamento/pendente;
- `docs/current/ARCHITECTURE.md` — arquitetura;
- `docs/current/DATABASE.md` — schema/migrations;
- `docs/current/API.md` — contrato HTTP real;
- `docs/current/DEPLOYMENT.md` — execução/deployment real;
- `docs/current/CONTRIBUTING.md` — fluxo de contribuição;
- ADR — decisão arquitetural relevante.

`docs/roadmap/` nunca deve ser citado como prova de que algo existe. `docs/archive/` não deve orientar implementação nova sem uma nova análise.

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
- PR mergeado na branch correta;
- CI/Quality pós-merge verdes;
- riscos residuais explicitados.

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

**Document Version:** 2.1  
**Last Updated:** 2026-08-16  
**Status:** Active
