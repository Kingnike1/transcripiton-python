# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para receber áudio de reuniões, transcrever, separar falas, identificar participantes e gerar inteligência estruturada localmente.

> **Estado atual:** o fluxo local cobre reunião → áudio → transcrição → diarização → identificação de participantes → inteligência por LLM. A próxima prioridade é a Stack 13, autenticação/autorização.

## O que funciona hoje

- CRUD e interface de reuniões;
- upload de áudio com streaming/staging e inspeção por `ffprobe`;
- Alembic e migrations;
- jobs persistentes + worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando configurado;
- identificação de participantes `SPEAKER_XX` → nome humano confirmável;
- inteligência estruturada local via Ollama;
- baseline `qwen3:4b` configurável por `.env`;
- resumo, action items, decisões, riscos, perguntas abertas e follow-ups;
- saída do LLM validada por JSON Schema/Pydantic;
- evidências com speaker/timestamps/citações para rastreabilidade;
- provider/modelo persistidos junto à análise;
- Docker/Compose com migrations, web e worker;
- CI/Quality com Python 3.11/3.12, Ruff, mypy, migrations, Bandit e `pip-audit`.

## Pipeline atual

```text
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
```

## LLM local

O provider inicial da Stack 12 é Ollama. Por padrão:

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

A análise não exige API paga. O modelo é configurável e o domínio não depende diretamente de Ollama, permitindo adapters futuros sem reescrever o contrato da análise.

## Execução local com Docker

Configure `.env` e execute:

```bash
docker compose up --build
```

Para diarização real, configure `HUGGINGFACE_TOKEN`. Para análise real, instale/inicie Ollama na máquina de uso e garanta que o worker consiga alcançar `OLLAMA_URL`, depois baixe o modelo configurado.

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
- [Deployment](docs/current/DEPLOYMENT.md)
- [Backlog](docs/06_BACKLOG.md)
- [Estado atual](PROJECT_STATE.MD)
- [Decisões técnicas](TECH_DECISIONS.md)
- [ADRs](docs/adr/)

## Próxima etapa

**Stack 13 — Autenticação e autorização:** usuários/login, ownership e autorização por recurso, preparando o AMIP para uso multiusuário.

## Licença

MIT — consulte [`LICENSE`](LICENSE).
