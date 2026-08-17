# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para receber áudio de reuniões, transcrever, separar falas, identificar participantes e gerar inteligência estruturada localmente.

> **Estado atual:** o fluxo cobre reunião → áudio → transcrição → diarização → participantes → inteligência por LLM, agora com contas, login e isolamento por usuário. A próxima prioridade é a Stack 14, infraestrutura de produção.

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
- senha com scrypt + salt;
- sessão opaca persistente/revogável;
- ownership de reuniões e isolamento de todos os recursos derivados;
- modo local legado preservado enquanto não houver contas;
- Docker/Compose, migrations e quality gates.

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
```

## Autenticação

Acesse:

```text
http://127.0.0.1:8000/login
```

Enquanto nenhuma conta existe, o AMIP mantém o modo local anterior. Ao criar a primeira conta, reuniões legadas sem proprietário são associadas a ela. Depois disso, o workspace e APIs protegidas exigem sessão válida e cada usuário acessa apenas suas próprias reuniões.

A sessão usa cookie `HttpOnly`/`SameSite=Lax`; em staging/produção o cookie também é `Secure`. O banco guarda somente o hash do token de sessão.

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
- [Deployment](docs/current/DEPLOYMENT.md)
- [Backlog](docs/06_BACKLOG.md)
- [Estado atual](PROJECT_STATE.MD)
- [Decisões técnicas](TECH_DECISIONS.md)
- [ADRs](docs/adr/)

## Próxima etapa

**Stack 14 — Infraestrutura de produção:** banco/storage/backups/observabilidade/hardening e deployment production-ready, preservando o monólito modular até existir evidência para outra arquitetura.

## Licença

MIT — consulte [`LICENSE`](LICENSE).
