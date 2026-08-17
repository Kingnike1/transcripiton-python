# AMIP — execução interna com Docker

## Pré-requisitos

- Docker Desktop ou Docker Engine com Compose v2;
- pelo menos alguns GB livres para imagens e modelos de IA;
- token do Hugging Face para diarização, após aceitar as condições do modelo pyannote.

## 1. Configurar

Na raiz do projeto:

```bash
cp .env.example .env
```

Defina `HUGGINGFACE_TOKEN` no `.env` se for usar diarização. Para transcrição apenas, o worker ainda funciona com faster-whisper, mas o worker completo inicializa também o provider pyannote e portanto o token/modelo deve estar disponível para o fluxo completo.

## 2. Construir e iniciar

```bash
docker compose build
docker compose up -d
```

O Compose executa `alembic upgrade head` antes de iniciar web e worker.

Abra:

```text
http://127.0.0.1:8000/meetings
```

## 3. Verificar saúde

```bash
python scripts/smoke.py
```

ou:

```bash
docker compose ps
```

O serviço `web` deve aparecer como `healthy`.

## 4. Logs

```bash
docker compose logs -f web
docker compose logs -f worker
```

## 5. Parar e iniciar novamente

```bash
docker compose stop
docker compose start
```

Para remover containers sem apagar dados:

```bash
docker compose down
```

Não use `docker compose down -v` se quiser preservar banco, áudios e cache dos modelos.

## 6. Atualizar o projeto

```bash
git pull
docker compose build
docker compose up -d
```

A migration roda antes dos serviços subirem.

## Persistência

O Compose usa dois volumes:

- `amip_data`: SQLite, storage de áudio e logs;
- `model_cache`: cache de modelos Hugging Face/IA.

Os containers podem ser recriados sem perder esses volumes.

## Backup

Descubra o nome exato do volume:

```bash
docker volume ls
```

Faça backup do volume `amip_data` para a pasta atual:

```bash
docker run --rm -v transcripiton-python_amip_data:/data -v "$PWD:/backup" alpine sh -c "tar czf /backup/amip-data-backup.tar.gz -C /data ."
```

Em instalações cujo projeto/volume tenha outro prefixo, substitua `transcripiton-python_amip_data` pelo nome mostrado em `docker volume ls`.

Para restaurar, pare a aplicação e extraia o arquivo no mesmo volume antes de subir novamente.

## Arquitetura do Compose

```text
migrate (one-shot)
   ↓
web (FastAPI/Jinja2) ─┐
                      ├─ amip_data (SQLite + áudio + logs)
worker (Whisper +     ┘
        pyannote)
   ↓
model_cache
```

O processo HTTP não executa os modelos pesados. `web` cria jobs persistentes e `worker` consome esses jobs de forma separada.
