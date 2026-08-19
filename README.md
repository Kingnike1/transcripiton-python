# AMIP — AI Meeting Intelligence Platform

O AMIP é um monólito modular em Python/FastAPI para gravar ou receber áudio de reuniões, transcrever, separar falas, identificar participantes, gerar inteligência estruturada, buscar conhecimento e exportar resultados.

> **Estado atual:** o fluxo cobre reunião → gravação/upload → transcrição → diarização → participantes → inteligência por LLM → busca → exportação, com contas, isolamento por usuário e baseline de produção. Com a Stack 17, o ciclo funcional planejado de Stacks 7–17 está completo.

## O que funciona hoje

- CRUD e interface de reuniões;
- upload seguro de áudio e inspeção por `ffprobe`;
- gravação pelo microfone do navegador com preview antes do envio;
- jobs persistentes + worker separado;
- transcrição local com `faster-whisper`;
- diarização com `pyannote.audio` quando configurado;
- identificação humana de `SPEAKER_XX`;
- inteligência estruturada via Ollama + `qwen3:4b` configurável;
- resumo, action items, decisões, riscos e follow-ups rastreáveis;
- usuários, cadastro, login e logout;
- sessão opaca persistente/revogável e ownership;
- busca em título, descrição e texto transcrito, isolada por usuário;
- exportação TXT, Markdown, JSON, DOCX e PDF;
- PostgreSQL/Compose de produção, readiness e backups;
- SQLite preservado para desenvolvimento/testes;
- migrations e quality gates.

## Pipeline atual

```text
User
  ↓ owns
Meeting
  ↓
Microphone recording / Audio upload
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
Search / Export
```

## Gravação por microfone

Abra uma reunião em `/meetings/{id}` e use **Gravar pelo microfone**. O navegador solicita permissão, grava localmente, oferece preview e só envia o arquivo quando o usuário confirma **Usar gravação**.

A captura usa `MediaRecorder` e tenta WebM/Opus, WebM, Ogg/Opus e MP4 conforme suporte do navegador. Depois do envio, o áudio entra no mesmo pipeline seguro do upload convencional: validação, limite de tamanho, assinatura do arquivo, `ffprobe`, storage e transcrição.

O recurso exige HTTPS ou localhost, conforme as regras de segurança dos navegadores para acesso ao microfone.

## Busca

```text
GET /api/search?q=termo&skip=0&limit=20
```

A busca considera título, descrição e transcrição, devolve contexto do match e respeita o owner da reunião.

## Exportação

```text
GET /api/meetings/{meeting_id}/export?format=md
```

Formatos: `txt`, `md`, `json`, `docx` e `pdf`. Os arquivos são gerados sob demanda e podem incluir metadados, participantes, transcrição segmentada e análise estruturada. Reuniões ainda sem transcrição ou análise continuam exportáveis.

## Autenticação

Acesse `http://127.0.0.1:8000/login`. Enquanto nenhuma conta existe, o AMIP mantém o modo local anterior. Depois da primeira conta, APIs protegidas e workspace usam sessão e ownership.

## LLM local

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

A análise não exige API paga. O domínio não depende diretamente de Ollama e pode receber adapters futuros.

## Diarização real

O worker usa `pyannote.audio`. Configure em `.env`:

```env
HUGGINGFACE_TOKEN=seu-token-de-leitura
PYANNOTE_MODEL=pyannote/speaker-diarization-community-1
PYANNOTE_DEVICE=cpu
```

O token deve permanecer fora do Git. Antes do smoke test real, valide os pré-requisitos sem imprimir o segredo:

```bash
python scripts/check_diarization.py
```

## Execução local com Docker

Configure `.env` e execute:

```bash
docker compose config --quiet
docker compose up --build
```

Para o baseline de produção:

```bash
cp .env.production.example .env.production
docker compose -f compose.production.yaml config --quiet
docker compose -f compose.production.yaml up --build -d
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
