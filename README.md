# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para receber áudio de reuniões, transcrever, separar falas e evoluir até inteligência estruturada.

> **Estado atual:** o fluxo local já cobre reunião → áudio → transcrição → diarização → identificação manual dos participantes. A próxima prioridade é a Stack 12, inteligência por LLM.

## O que funciona hoje

- CRUD e interface de reuniões;
- upload de áudio com streaming/staging e inspeção por `ffprobe`;
- Alembic e migrations;
- jobs persistentes + worker separado;
- claim, lease, heartbeat, retry e recovery;
- transcrição local com `faster-whisper`;
- segmentos/timestamps persistidos;
- diarização local com `pyannote.audio` quando `HUGGINGFACE_TOKEN` está configurado;
- `speaker_segments` reconciliados com o texto;
- identificação de participantes: `SPEAKER_XX` → nome humano editável/confirmável;
- UI para iniciar transcrição/diarização e confirmar participantes;
- Dockerfile/Compose com migrations, web e worker;
- volumes persistentes e cache de modelos;
- CI/Quality com Python 3.11/3.12, Ruff, mypy, migrations, Bandit e `pip-audit`.

## Ainda não implementado

- inteligência por LLM;
- autenticação/autorização;
- infraestrutura pública production-ready;
- busca;
- exportação;
- gravação por microfone.

## Pipeline atual

```text
Meeting
  ↓
Audio
  ↓ TRANSCRIBE
Transcription + segments
  ↓ DIARIZE
Speaker segments
  ↓ confirmação humana
Participants
  ↓
Stack 12 — LLM intelligence
```

## Execução local com Docker

Configure `.env` e execute:

```bash
docker compose up --build
```

O Compose executa migrations antes de web/worker. Para diarização real, configure `HUGGINGFACE_TOKEN`; a transcrição continua disponível sem esse token.

Também é possível executar via ambiente Python conforme `docs/current/DEPLOYMENT.md`.

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

Commits seguem Conventional Commits. Consulte [`PROJECT_GOVERNANCE.md`](PROJECT_GOVERNANCE.md).

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

**Stack 12 — Inteligência por LLM:** resumo estruturado, action items, decisões, riscos e follow-ups com rastreabilidade para transcrição e participantes.

## Licença

MIT — consulte [`LICENSE`](LICENSE).
