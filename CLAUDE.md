# CLAUDE.md — Entrada para agentes no AMIP

## Leia isto antes de alterar qualquer código

Todo agente ou desenvolvedor deve ler, nesta ordem:

1. `CLAUDE.md`;
2. `docs/PROJECT_STATUS.md`;
3. `docs/ROADMAP.md`;
4. `docs/ARCHITECTURE.md`.

Depois consulte ADRs e documentos específicos somente conforme a tarefa.

**Não use roadmaps/documentos históricos como fonte de verdade sem comparar com o código.** Alguns arquivos antigos em `docs/current/` e `docs/roadmap/` descrevem estados anteriores às Stacks já implementadas.

## O que é o projeto

AMIP (AI Meeting Intelligence Platform) é um monólito modular Python/FastAPI que recebe/grava áudio de reuniões e executa um pipeline com jobs persistentes:

```text
Meeting
  ↓
Audio upload / browser recording
  ↓
TRANSCRIBE → faster-whisper
  ↓
DIARIZE → pyannote
  ↓
Participants
  ↓
LLM analysis → Ollama
  ↓
Search / Export
```

## Arquitetura curta

- web: FastAPI/Uvicorn + Jinja2;
- frontend: HTML/CSS/JS vanilla, sem `package.json`;
- banco: SQLAlchemy; SQLite local/testes; PostgreSQL em produção;
- migrations: Alembic;
- jobs: fila durável no banco;
- worker: processo separado;
- STT: faster-whisper;
- diarização: pyannote.audio;
- LLM: Ollama adapter;
- storage: filesystem persistente configurável;
- deploy baseline: Docker/Compose.

Detalhes: `docs/ARCHITECTURE.md`.

## Branch auditada

A auditoria de continuidade de 2026-09-03 partiu de:

```text
branch: fix/runtime-dependencies
commit-base: 28493b4b7fd4cfdec565145d88d5ac97eb38c0b8
```

A documentação adicionada depois desse commit não muda comportamento funcional.

Sempre confirme o estado real antes de trabalhar:

```bash
git branch --show-current
git status --short --branch
git log -5 --oneline
```

## Comandos importantes

### Ambiente

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-worker.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
```

No Windows, use o equivalente do `venv`/PowerShell descrito em `docs/SETUP.md`.

### Executar aplicação completa

```bash
python run.py
```

### Executar separadamente

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
python -m app.workers.run
```

### Diagnóstico

```bash
python run.py --diagnostics
```

### Quality gates

```bash
ruff check app tests main.py
mypy app main.py
pytest --cov=app --cov-fail-under=80 tests/
pytest -q tests/test_migrations.py
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
```

### Docker

```bash
docker compose config --quiet
docker compose build
```

Produção:

```bash
docker compose -f compose.production.yaml config --quiet
docker compose -f compose.production.yaml build
```

## Convenções que devem ser preservadas

1. **Não transforme o projeto em microserviços por antecipação.**
2. Trabalho pesado de IA fica no worker, não em request HTTP.
3. Use services para regras/orquestração; routers devem permanecer finos.
4. Respeite repositories/Unit of Work e ownership de transações existente.
5. Evolua schema com Alembic; não substitua migrations por criação automática em produção.
6. Providers externos/pesados devem permanecer atrás das interfaces/adapters existentes.
7. `Meeting.owner_id` é a raiz de autorização dos recursos da reunião.
8. Nunca commite `.env`, tokens, API keys, senhas, cookies ou bundles não sanitizados.
9. Não reduza testes/cobertura/linters para fazer uma Sprint passar.
10. Não introduza Redis/Celery, SPA, vector DB, Kubernetes ou novo provider sem necessidade definida na Sprint.
11. Mudanças devem ser pequenas, testáveis e reversíveis.
12. Antes de remover arquivo aparentemente duplicado, procure consumidores e preserve compatibilidade quando necessário.

## Coisas que não devem ser quebradas

- launcher `python run.py` inicia backend + worker;
- entrypoint canônico do worker `python -m app.workers.run`;
- `/health` como liveness;
- `/ready` como readiness com banco;
- modo SQLite de desenvolvimento/testes;
- PostgreSQL/Compose de produção;
- migrations existentes `0001`–`0009`;
- upload seguro e storage;
- pipeline de jobs persistentes;
- autenticação/sessões/ownership;
- exportações existentes;
- logging com redaction de credenciais;
- separação das dependências web e worker.

## Alertas atuais

### P0 para implantação pública

O código atual permite modo local sem autenticação quando não existe nenhum usuário. Isso é compatibilidade intencional para uso local, mas **não é um bootstrap seguro para produção pública**. Consulte `docs/PROJECT_STATUS.md` e a Sprint 2 em `docs/ROADMAP.md`.

### Branch sem CI próprio

`fix/runtime-dependencies` não possui workflow run automático registrado. A **próxima Sprint recomendada é a Sprint 1 — Baseline reproduzível**, antes de qualquer feature nova.

### Runtime ML

A diarização possui hardening parcial de FFmpeg Shared, mas ainda precisa fechar preflight e compatibilidade Torch/TorchCodec/Pyannote. Não marque diarização como portátil apenas porque `ffmpeg -version` funciona.

### Documentação histórica

`docs/roadmap/AI_PIPELINE.md`, `docs/roadmap/FRONTEND.md` e partes de `docs/current/` estão atrasados em relação ao código. Para estado atual, use os quatro documentos canônicos listados no topo.

## Como começar uma implementação

1. leia os quatro documentos canônicos;
2. identifique a Sprint exata em `docs/ROADMAP.md`;
3. confirme branch/status/commit;
4. rode baseline relevante antes de alterar código;
5. não misture pendências de outra prioridade na mesma Sprint;
6. faça a menor alteração que satisfaça os critérios de aceite;
7. adicione/ajuste testes antes de considerar concluído;
8. rode gates relevantes;
9. revise `git diff`;
10. atualize `docs/PROJECT_STATUS.md` apenas com fatos comprovados.

## Como validar qualquer alteração

No mínimo:

```bash
git diff --check
ruff check app tests main.py
mypy app main.py
pytest --cov=app --cov-fail-under=80 tests/
```

Quando tocar banco:

```bash
pytest -q tests/test_migrations.py
alembic heads
```

Quando tocar segurança/dependências:

```bash
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
```

Quando tocar container/runtime:

```bash
docker compose config --quiet
docker compose build
```

Quando tocar pipeline ML, registre separadamente testes unitários/fakes e testes reais dependentes de modelo/runtime.

## Regra de encerramento de Sprint

Uma Sprint só está concluída quando:

- critérios de aceite foram verificados;
- testes relevantes passam;
- falhas/skips estão explicitamente registrados;
- não existem segredos no diff;
- documentação canônica permanece coerente;
- branch/commit final são informados.

Não iniciar automaticamente a Sprint seguinte.
