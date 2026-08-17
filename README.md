# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para receber áudio de reuniões e transformá-lo progressivamente em transcrição e inteligência estruturada.

> **Estado atual:** reuniões, upload, jobs persistentes e a primeira transcrição real local com `faster-whisper` estão implementados. A próxima prioridade é fechar uma interface utilizável ponta a ponta.

## O que funciona hoje

- CRUD de reuniões via API;
- upload de áudio por reunião;
- streaming/chunks com staging temporário;
- validação de arquivo e inspeção por `ffprobe`;
- persistência de metadados técnicos do áudio;
- Unit of Work e transações no Service Layer;
- migrations Alembic;
- proteção contra dois áudios ativos na mesma reunião;
- erros públicos sanitizados + `X-Request-ID`;
- jobs persistentes com progresso, tentativas, resultado e erro;
- worker separado do processo HTTP;
- claim, lease, heartbeat, retry e stale recovery;
- transcrição local com `faster-whisper`;
- defaults de STT: modelo `base`, CPU, `int8` e VAD;
- persistência de texto, idioma e segmentos com timestamps/confiança;
- estado de reunião `TRANSCRIBING → TRANSCRIBED`;
- API para consultar a transcrição e seus segmentos;
- CI/Quality em Python 3.11 e 3.12;
- Ruff, mypy, migration checks, Bandit e `pip-audit` bloqueantes.

## Ainda não implementado

- interface completa de reuniões/processamento/transcrição;
- empacotamento simples para uso interno;
- diarização;
- identificação de participantes;
- LLM/resumos/action items;
- autenticação/autorização;
- busca/exportação;
- deployment público production-ready.

## Arquitetura

```text
FastAPI
  ↓
Application Services
  ↓
SqlAlchemyUnitOfWork
  ↓
Repositories
  ↓
SQLAlchemy / SQLite

Upload/API
  ↓
ProcessingJob (DB)
  ↓
JobWorker
  ↓
ITranscriber
  ↓
faster-whisper
  ↓
Transcription + TranscriptionSegment
```

O projeto permanece um **monólito modular**. O STT pesado roda no worker, não no processo web.

## Setup local

### Pré-requisitos

- Python 3.11 ou 3.12;
- Git;
- `ffprobe` disponível para upload real de áudio.

### Instalação da aplicação web

```bash
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python
python -m venv .venv
```

Ative o ambiente virtual e instale:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Para executar o worker com transcrição real, instale também:

```bash
pip install -r requirements-worker.txt
```

Configure:

```bash
cp .env.example .env
```

Crie/atualize o banco:

```bash
alembic upgrade head
```

Execute a API:

```bash
uvicorn main:app --reload
```

Aplicação:

```text
http://127.0.0.1:8000
```

OpenAPI:

```text
http://127.0.0.1:8000/docs
```

O worker é executado separadamente conforme a configuração atual do projeto. Na primeira transcrição real, o `faster-whisper` poderá baixar o modelo configurado e manter cache local.

## Testes e quality

```bash
pytest --cov=app --cov-fail-under=80 tests/
ruff check app tests main.py
mypy app main.py
pytest -q tests/test_migrations.py
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
```

Os testes de CI usam providers fake e não exigem download do modelo Whisper.

Os workflows `CI` e `Quality` executam esses gates automaticamente.

## Fluxo Git

```text
main      → release estável
develop   → integração
agent/*   → trabalho por Sprint/Stack
```

Commits seguem Conventional Commits. As regras completas estão em [`PROJECT_GOVERNANCE.md`](PROJECT_GOVERNANCE.md).

## Documentação

Comece por [`docs/README.md`](docs/README.md).

### Estado atual

- [Arquitetura](docs/current/ARCHITECTURE.md)
- [Banco](docs/current/DATABASE.md)
- [API](docs/current/API.md)
- [Execução/deployment atual](docs/current/DEPLOYMENT.md)
- [Contribuição](docs/current/CONTRIBUTING.md)

### Planejamento

- [Backlog](docs/06_BACKLOG.md)
- [Roadmap de frontend](docs/roadmap/FRONTEND.md)
- [Roadmap de IA](docs/roadmap/AI_PIPELINE.md)

### Governança e estado

- [Contexto](PROJECT_CONTEXT.md)
- [Governança](PROJECT_GOVERNANCE.md)
- [Estado atual](PROJECT_STATE.MD)
- [Decisões técnicas](TECH_DECISIONS.md)
- [ADRs](docs/adr/)

## Próxima etapa

Depois do merge da Sprint 7, a prioridade é **Sprint 8 — Interface utilizável**, conectando criação da reunião, upload, início da transcrição, acompanhamento do job e visualização do resultado.

## Licença

MIT — consulte [`LICENSE`](LICENSE).
