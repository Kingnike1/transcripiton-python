# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para receber áudio de reuniões, transcrever, separar falas, identificar participantes, gerar inteligência estruturada e recuperar esse conhecimento por busca textual.

> **Estado atual:** o fluxo cobre reunião → áudio → transcrição → diarização → participantes → inteligência por LLM → busca, com contas, isolamento por usuário e baseline de produção. A próxima prioridade após a Stack 15 é exportação.

## O que funciona hoje

- CRUD e interface de reuniões;
- upload seguro de áudio e inspeção por `ffprobe`;
- jobs persistentes + worker separado;
- transcrição local com `faster-whisper`;
- diarização com `pyannote.audio` quando configurado;
- identificação humana de `SPEAKER_XX`;
- inteligência estruturada via Ollama + `qwen3:4b` configurável;
- resumo, action items, decisões, riscos e follow-ups rastreáveis;
- usuários, cadastro, login e logout;
- sessão opaca persistente/revogável e ownership;
- busca em título, descrição e texto transcrito, isolada por usuário;
- PostgreSQL/Compose de produção, readiness e backups;
- SQLite preservado para desenvolvimento/testes;
- migrations e quality gates.

## Pipeline atual

```text
User
  ↓ owns
Meeting
  ↓
Audio
  ↓ TRANSCRIBE
Transcription
  ↓ DIARIZE
Speaker segments
  ↓ confirmação humana
Participants
  ↓ SUMMARIZE
Ollama / Qwen3
  ↓
Structured meeting intelligence
  ↓
Text search
```

## Busca

Na interface, acesse `/meetings` e use o campo de busca. Pela API:

```text
GET /api/search?q=termo&skip=0&limit=20
```

A busca considera título, descrição e transcrição, devolve contexto do match e respeita o owner da reunião. O baseline é SQL portável; PostgreSQL FTS fica reservado para quando volume e métricas justificarem. Vector database não é requisito desta etapa.

## Autenticação

Acesse `http://127.0.0.1:8000/login`. Enquanto nenhuma conta existe, o AMIP mantém o modo local anterior. Depois da primeira conta, APIs protegidas e workspace usam sessão e ownership.

## LLM local

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

A análise não exige API paga. O domínio não depende diretamente de Ollama e pode receber adapters futuros.

## Execução local com Docker

Configure `.env` e execute:

```bash
docker compose up --build
```

Para diarização real, configure `HUGGINGFACE_TOKEN`. Para análise real, instale/inicie Ollama na máquina de uso e garanta que o worker alcance `OLLAMA_URL`.

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

## Fluxo Git

```text
main      → release estável
develop   → integração
agent/*   → trabalho por Stack
```

## Documentação

- [Mapa documental](docs/README.md)
- [Arquitetura atual](docs/current/ARCHITECTURE.md)
- [Banco atual](docs/current/DATABASE.md)
- [API atual](docs/current/API.md)
- [Deploy](docs/current/DEPLOYMENT.md)
