# Execução e deployment atual

## Estado de prontidão

O AMIP possui baseline de produção implementado, incluindo:

- autenticação e autorização por ownership;
- jobs persistentes e worker separado;
- PostgreSQL no Compose de produção;
- storage persistente em volume;
- migrations one-shot via Alembic;
- `/health` e `/ready`;
- backup automatizado e retenção;
- Dockerfile multi-stage;
- `compose.yaml` para ambiente local;
- `compose.production.yaml` para baseline de produção.

Isso não significa que qualquer host possa ser exposto publicamente sem configuração operacional adicional. Antes de produção pública ainda devem ser validados TLS/reverse proxy, monitor externo, destino off-host de backups, política de retenção/LGPD, secrets e hardening do ambiente escolhido.

## Requisitos locais sem Docker

- Python 3.11 ou 3.12;
- Git;
- `ffprobe` disponível no PATH;
- SQLite para desenvolvimento padrão;
- `requirements-worker.txt` para Whisper/Pyannote;
- Ollama quando a análise LLM local for usada.

## Setup local sem Docker

```bash
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python
python -m venv .venv
```

Ativação:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instale aplicação, ferramentas de desenvolvimento e runtime do worker:

```bash
pip install -r requirements.txt -r requirements-dev.txt -r requirements-worker.txt
```

Configure o ambiente:

```bash
cp .env.example .env
```

Aplique migrations antes de iniciar:

```bash
alembic upgrade head
```

Inicie web e worker em terminais separados:

```bash
uvicorn main:app --reload
python worker.py
```

## Docker local oficial

O repositório possui `Dockerfile` e `compose.yaml` oficiais.

Prepare o ambiente:

```bash
cp .env.example .env
docker compose config --quiet
docker compose up --build
```

O Compose local executa:

- `migrate` — aplica `alembic upgrade head`;
- `web` — FastAPI;
- `worker` — Whisper, Pyannote e LLM jobs;
- volume `amip_data` — SQLite/storage/logs;
- volume `model_cache` — cache dos modelos do worker.

Validação:

```text
GET http://127.0.0.1:8000/health
GET http://127.0.0.1:8000/ready
```

## Baseline de produção com Docker

O arquivo oficial é `compose.production.yaml`.

Crie o arquivo de configuração a partir do template:

```bash
cp .env.production.example .env.production
```

Preencha os secrets reais fora do Git, principalmente:

- `SECRET_KEY`;
- `POSTGRES_PASSWORD`;
- `HUGGINGFACE_TOKEN` quando diarização estiver habilitada.

Valide antes de subir:

```bash
docker compose -f compose.production.yaml config --quiet
docker compose -f compose.production.yaml up --build -d
```

O baseline de produção contém PostgreSQL 16, migration one-shot, web, worker e processo de backup. O endpoint `/ready` é usado para confirmar que a aplicação alcança o banco.

## `ffprobe`

Uploads reais exigem `ffprobe`, normalmente distribuído com FFmpeg.

```env
FFPROBE_BINARY=ffprobe
FFPROBE_TIMEOUT_SECONDS=15
```

Se o binário não estiver disponível, o upload real deve falhar de forma explícita em vez de aceitar mídia sem inspeção.

## Diarização com Hugging Face + Pyannote

A Stack de diarização usa:

```env
HUGGINGFACE_TOKEN=
PYANNOTE_MODEL=pyannote/speaker-diarization-community-1
PYANNOTE_DEVICE=cpu
```

Para habilitar o fluxo real:

1. possuir uma conta Hugging Face;
2. aceitar as condições de acesso do modelo Pyannote configurado, quando exigidas;
3. criar um token de leitura;
4. colocar o token somente em `.env` ou `.env.production`;
5. nunca commitar o token;
6. instalar `requirements-worker.txt` ou usar o target `worker` do Dockerfile;
7. iniciar/reiniciar o worker.

O worker lê `HUGGINGFACE_TOKEN` no startup. Quando o token não está configurado, o handler de diarização não é registrado e o worker emite um aviso explícito.

Para validar a preparação sem imprimir o token:

```bash
python scripts/check_diarization.py
```

Em Docker local:

```bash
docker compose run --rm worker python scripts/check_diarization.py
```

O primeiro carregamento real do modelo pode usar o volume `model_cache`/`HF_HOME` para evitar download repetido.

## LLM local com Ollama

Configuração padrão:

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

Quando o AMIP estiver em container e o Ollama estiver no host, `localhost` dentro do container não aponta para o host. Ajuste `OLLAMA_URL` conforme a plataforma/rede, por exemplo `http://host.docker.internal:11434` quando suportado.

## Ambientes

```text
ENVIRONMENT=development | test | staging | production
```

Staging/produção recusam combinações inseguras definidas pela configuração do projeto, como `DEBUG=true` e secrets placeholders quando aplicável.

## Testes e quality gates locais

```bash
pytest --cov=app --cov-fail-under=80 tests/
ruff check app tests main.py
mypy app main.py
pytest -q tests/test_migrations.py
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
```

Os workflows `CI`, `Quality` e `Docker` repetem os controles relevantes no GitHub.

## Atualização de schema

```bash
alembic revision --autogenerate -m "descricao"
# revisar a migration manualmente
alembic upgrade head
```

Migrations destrutivas exigem backup e plano de rollback.

## Checklist antes de exposição pública

- [ ] `CI`, `Quality` e `Docker` verdes;
- [ ] PostgreSQL persistente validado;
- [ ] migrations aplicadas;
- [ ] secrets fora do repositório;
- [ ] `HUGGINGFACE_TOKEN` validado quando diarização for necessária;
- [ ] Ollama/modelo validado quando análise local for necessária;
- [ ] smoke test com áudio e voz reais;
- [ ] gravação por microfone testada em HTTPS/localhost;
- [ ] reverse proxy + TLS;
- [ ] limite de upload no edge;
- [ ] backup e restore testados;
- [ ] cópia off-host de backups;
- [ ] monitor externo de `/ready`;
- [ ] políticas de retenção e LGPD definidas;
- [ ] plano de rollback documentado.

---

**Status:** Active — Docker/local/production baseline documented  
**Last Updated:** 2026-08-18
