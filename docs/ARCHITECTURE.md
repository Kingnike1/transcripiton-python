# ARCHITECTURE — AMIP / Transcripition

> Arquitetura canônica baseada no código real da branch `fix/runtime-dependencies`, auditada em 2026-09-03.

## Visão geral

O AMIP é um **monólito modular em Python** com dois processos de aplicação principais:

1. **Web** — FastAPI/Uvicorn, API HTTP e páginas Jinja2;
2. **Worker** — processo separado que consome jobs persistidos no banco e executa trabalho pesado.

Eles compartilham banco de dados e storage. O projeto evita executar transcrição, diarização ou LLM dentro do request HTTP.

```text
┌──────────────── Browser ────────────────┐
│ HTML/Jinja2 + CSS + JavaScript vanilla │
│ MediaRecorder para gravação            │
└──────────────────┬──────────────────────┘
                   │ HTTP + cookie de sessão
                   ▼
          ┌──── FastAPI / Uvicorn ────┐
          │ routers + web routes      │
          │ auth + ownership          │
          └──────────┬─────────────────┘
                     ▼
              Application Services
              │       │       │
              │       │       └── storage
              │       └────────── repositories/UoW
              │                       │
              ▼                       ▼
        ProcessingJob            SQLite/PostgreSQL
              │                       ▲
              └──── banco/fila ───────┘
                     │
                     ▼
                  Worker
          ┌──────────┼───────────┐
          ▼          ▼           ▼
   faster-whisper  pyannote   Ollama/LLM
```

## Entry points

### Aplicação FastAPI

`main.py` cria `FastAPI`, registra middleware/handlers, monta `/static`, registra templates e inclui todos os routers.

Endpoints de infraestrutura:

- `GET /health`: liveness do processo;
- `GET /ready`: testa acesso ao banco com `SELECT 1`.

### Launcher local recomendado

`run.py` inicia backend e worker usando o interpretador Python atual, espera `/health`, monitora os processos e tenta encerrar ambos corretamente com Ctrl+C.

```bash
python run.py
```

Modo diagnóstico:

```bash
python run.py --diagnostics
```

### Worker

Entry point canônico usado pelo launcher e Docker:

```bash
python -m app.workers.run
```

Existe também `worker.py`, praticamente equivalente. Ele deve ser tratado como compatibilidade/legado até uma Sprint decidir seu destino.

## Camadas e diretórios

### `app/api/`

Fronteira HTTP da aplicação:

- `auth.py` — cadastro/login/logout/status;
- `meetings.py` — operações de reunião;
- `audio.py` — áudio/upload;
- `jobs.py` — jobs persistentes;
- `transcriptions.py` — transcrição;
- `diarization.py` — diarização;
- `participants.py` — participantes;
- `analysis.py` — inteligência/análise;
- `search.py` — pesquisa;
- `exports.py` — exportação;
- `dependencies.py` — DI e guards de autorização.

Routers devem permanecer finos; regras de negócio pertencem aos services.

### `app/services/`

Camada de aplicação/orquestração. Contém serviços para reunião, áudio, upload staging, validação/inspeção, jobs, pipeline, transcrição, diarização, participantes, análise, busca, exportação, autenticação e storage.

O desenho atual usa interfaces/adapters para dependências externas relevantes.

### `app/database/`

Acesso a dados:

- session/engine;
- repositories especializados;
- repository base;
- Unit of Work.

A propriedade de transações foi formalizada em ADRs anteriores; alterações futuras não devem introduzir commits arbitrários em repositories sem revisar o contrato de UoW/service layer.

### `app/models/`

Modelos SQLAlchemy principais:

- `User`;
- `AuthSession`;
- `Meeting`;
- `Audio`;
- `ProcessingJob`;
- `Transcription`;
- `TranscriptionSegment`;
- `Speaker`/speaker segments;
- `Participant`;
- `Analysis`.

### `app/schemas/`

Schemas Pydantic da fronteira de entrada/saída.

### `app/providers/`

Adapters externos/pesados:

- `transcriber/faster_whisper.py`;
- `speaker_identifier/pyannote.py`;
- `llm/ollama.py`;
- contratos/exporter/summarizer auxiliares.

O domínio/aplicação não deve passar a depender diretamente das bibliotecas pesadas se uma interface já existe.

### `app/workers/`

- `job_worker.py` — loop de trabalho durável;
- `registry.py` — composição de handlers/providers;
- `transcription_handler.py`;
- `diarization_handler.py`;
- `analysis_handler.py`;
- `run.py` — entrypoint.

### `app/infrastructure/`

`media_runtime.py` cuida de descoberta/preparação de FFmpeg, especialmente DLLs Shared no Windows antes do uso de TorchCodec/Pyannote. A implementação atual é parcial em relação ao hardening planejado.

### `app/core/`

Infraestrutura transversal:

- enums/estados;
- códigos de erro;
- handlers de exceção;
- logging e redaction;
- request ID/context;
- diagnostics;
- utilitário de tempo.

### `app/config/`

Configuração modular via ambiente:

- application;
- database;
- logging;
- storage;
- audio;
- AI;
- security.

`app/config/__init__.py` agrega esses módulos em `settings` para compatibilidade.

## Frontend atual

O frontend é **server-side rendered**, sem Node/package.json.

```text
templates/
├── auth.html
├── index.html
├── meetings.html
└── meeting_detail.html

static/
├── css/main.css
└── js/
    ├── main.js
    └── meeting_recording.js
```

A gravação usa APIs nativas do browser (`MediaRecorder`). O backend recebe o arquivo resultante e o trata pelo fluxo de upload.

O roadmap antigo de frontend que afirma haver apenas landing page está desatualizado.

## Fluxo de dados principal

```text
User
  │ owns
  ▼
Meeting
  │
  ├── upload de arquivo
  └── gravação MediaRecorder
          │
          ▼
        Audio
          │
          ▼
   ProcessingJob: TRANSCRIBE
          │
          ▼
   faster-whisper
          │
          ▼
   Transcription + segments
          │
          ▼
   ProcessingJob: DIARIZE
          │
          ▼
       pyannote
          │
          ▼
   speaker segments
          │
          ▼
   Participants / identificação humana
          │
          ▼
   ProcessingJob: análise
          │
          ▼
      Ollama LLM
          │
          ▼
 Structured intelligence
      │            │
      ▼            ▼
    Search        Export
```

## Jobs e processamento

O AMIP usa o **banco como fila durável**. Isso evita infraestrutura extra enquanto a escala atual não exige broker dedicado.

Princípios a preservar:

- trabalho pesado fora da thread/request web;
- estado do job persistido;
- worker separado;
- retry/lease/recuperação de job conforme implementação vigente;
- autorização acontece na fronteira HTTP; worker processa recursos internos já persistidos.

Redis/Celery/RQ/Dramatiq não devem ser adicionados sem problema medido.

## Banco de dados

### Local/testes

SQLite é o caminho simples de desenvolvimento e fixtures de testes.

### Produção

`compose.production.yaml` provisiona PostgreSQL 16, migrations, web, worker e backup.

Migrations Alembic existentes:

```text
0001_initial_schema
0002_audio_media_metadata
0003_one_active_audio_per_meeting
0004_processing_jobs
0005_transcription_segments
0006_speaker_segments
0007_participant_identities
0008_analysis_provider_metadata
0009_auth_and_meeting_ownership
```

Nunca substituir migrations por `Base.metadata.create_all()` em produção. Testes podem usar criação direta de metadata quando explicitamente isolados.

## Storage

Arquivos de áudio e artefatos usam caminho configurável (`STORAGE_PATH`). Em Compose, banco e storage usam volumes persistentes. Produção mantém storage separado do filesystem efêmero do container.

## Autenticação e autorização

### Conta

`AuthService` implementa:

- normalização de e-mail;
- senha mínima atual de 10 caracteres;
- hash scrypt com salt aleatório;
- login de usuário ativo;
- sessão expiráveis de 7 dias;
- logout por remoção da sessão.

### Sessão

O token entregue ao navegador é opaco. O banco guarda hash SHA-256 do token. Cookie:

- `HttpOnly=true`;
- `SameSite=Lax`;
- `Secure=true` em staging/production;
- path `/`.

### Ownership

`Meeting.owner_id` é a raiz da autorização. Guards também protegem jobs via reunião-pai. Acesso cruzado usa 404 para não revelar existência de recurso.

### Modo local sem contas

Enquanto não existe nenhum `User`, os guards permitem o modo local legado. Na criação do primeiro usuário, reuniões legadas sem owner são atribuídas a ele.

**Importante:** esse fallback é risco P0 para exposição pública antes do bootstrap da primeira conta. Não assumir que o fato de `ENVIRONMENT=production` desativa o fallback — no código auditado, não desativa.

## Integrações externas

### FFmpeg / ffprobe

Usados para inspeção/runtime de mídia. Windows tem lógica para localizar build Shared; Linux depende de FFmpeg disponível no sistema/PATH na implementação atual.

### faster-whisper

Provider local de speech-to-text, instalado pelo conjunto de dependências do worker.

### pyannote.audio

Provider de diarização. Pode depender de token Hugging Face/modelo gated e runtime Torch/TorchCodec/FFmpeg compatível.

### Ollama

Adapter HTTP/local para inteligência por LLM. O modelo e endpoint são configuráveis por ambiente.

### OpenAI

Existe nome de variável `OPENAI_API_KEY`, mas não há adapter OpenAI operacional identificado na árvore auditada. Não documentar como integração implementada.

## Infraestrutura Docker

`Dockerfile` possui targets:

- `web`: dependências HTTP/app, Uvicorn;
- `worker`: inclui `requirements-worker.txt` e executa worker.

A imagem base é Python 3.11 slim e instala FFmpeg via apt.

### Compose local

`compose.yaml` usa SQLite em volume e possui serviços `migrate`, `web` e `worker`.

### Compose produção

`compose.production.yaml` usa:

- PostgreSQL 16;
- migration job;
- web com readiness healthcheck;
- worker;
- backup loop;
- volumes de banco, storage, cache de modelos e backups.

## Observabilidade e diagnósticos

- logging estruturado/códigos de erro;
- redaction de credenciais Bearer adicionada nos commits recentes;
- request IDs/context;
- `diagnose.py` e `python run.py --diagnostics` para gerar bundle sanitizado;
- `/health` e `/ready`.

Ainda não há evidência de stack externa de métricas/tracing/alertas. Não inventar essa camada.

## Testes e gates

A configuração atual define:

- Python 3.11/3.12;
- Ruff (erros de sintaxe/undefined/import issues selecionados);
- mypy;
- pytest + coverage >= 80%;
- migration integrity;
- Bandit;
- pip-audit;
- workflows CI/Docker/Quality.

A branch `fix/runtime-dependencies` não possui execução automática registrada desses workflows; validar localmente/PR antes de merge.

## Decisões arquiteturais que não devem ser quebradas sem ADR

1. monólito modular;
2. web e worker separados;
3. jobs duráveis no banco enquanto escala não exigir broker;
4. providers pesados atrás de interfaces;
5. migrations Alembic como evolução de schema;
6. ownership derivado da reunião;
7. storage persistente fora do container efêmero;
8. segredos apenas por ambiente/secret store, nunca Git;
9. mudanças transacionais respeitam service/UoW;
10. nenhuma dependência arquitetural grande por antecipação.

## Dívidas arquiteturais atuais

- runtime de mídia ainda precisa de preflight completo;
- fallback local sem autenticação não é seguro para produção pública sem bootstrap;
- frontend carece de E2E real em navegador;
- `worker.py` duplica entrypoint canônico;
- documentos históricos precisam ser claramente classificados;
- restore de backup precisa de prova operacional;
- ausência de rate limiting/CSRF dedicado deve ser tratada antes de exposição mais ampla.

## Documentos relacionados

- estado atual: `docs/PROJECT_STATUS.md`;
- roadmap: `docs/ROADMAP.md`;
- setup: `docs/SETUP.md`;
- decisões históricas: `docs/adr/`;
- produção antiga/detalhada: `docs/PRODUCTION.md` e `docs/current/DEPLOYMENT.md` — consultar com cautela e validar contra o código.
