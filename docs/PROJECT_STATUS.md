# PROJECT STATUS — AMIP / Transcripition

> Fonte de verdade operacional para continuidade de desenvolvimento.
>
> **Data da auditoria:** 2026-09-03  
> **Branch auditada:** `fix/runtime-dependencies`  
> **Commit-base auditado:** `28493b4b7fd4cfdec565145d88d5ac97eb38c0b8` (`test(runtime): protect unified launcher behavior`)  
> **Relação com `develop`:** 35 commits à frente, 0 atrás no momento da auditoria.

## Objetivo do projeto

AMIP (AI Meeting Intelligence Platform) é um monólito modular em Python/FastAPI para receber ou gravar áudio de reuniões, persistir e processar esse áudio em background, transcrever, diarizar falantes, associar participantes, gerar inteligência estruturada com LLM, pesquisar conteúdo e exportar resultados.

## Escopo desta auditoria

A auditoria validou a árvore real da branch, código de aplicação, modelos, migrations, providers, frontend server-rendered, workers, dependências, configuração, workflows, documentação e histórico Git disponível no repositório remoto.

### Limitação importante

O `git status` do checkout local de um desenvolvedor/VM não pode ser observado pelo repositório remoto. Portanto esta auditoria **não afirma** que a cópia local de Pablo esteja sem arquivos modificados ou não rastreados. No remoto, a referência auditada aponta para o commit acima. Antes de qualquer implementação, executar localmente:

```bash
git branch --show-current
git status --short --branch
git log -5 --oneline
```

Também não foi possível executar os comandos locais de instalação/lint/typecheck/test/build/start dentro do ambiente desta auditoria. Não foram inventados resultados. O último `develop` observado possuía CI e Docker concluídos com sucesso, mas a branch atual não possui workflow run automático porque os workflows de push não incluem `fix/**`.

## Estado geral

**Classificação global: 🟡 PARCIAL / funcionalmente avançado, porém sem baseline atual completamente validado.**

O produto possui uma vertical funcional ampla no código: reuniões, upload/gravação, fila persistente, worker, transcrição, diarização, participantes, LLM, busca, exportação, autenticação/ownership, migrations e infraestrutura Docker. O principal problema de continuidade não é ausência de código-base, e sim a combinação de:

1. branch atual sem CI reproduzido;
2. documentação histórica divergente do código;
3. runtime ML/FFmpeg ainda parcialmente endurecido entre Windows/Linux/Docker;
4. risco de segurança do modo local sem autenticação em implantação pública sem conta inicial;
5. algumas duplicidades/artefatos históricos que aumentam a chance de futuros agentes seguirem instruções erradas.

## Tecnologias reais

| Área | Tecnologia | Estado |
|---|---|---|
| Backend HTTP | FastAPI + Starlette + Uvicorn | ✅ CONCLUÍDO |
| Templates/UI | Jinja2 + HTML/CSS + JavaScript vanilla | ✅ CONCLUÍDO |
| Persistência | SQLAlchemy 2 | ✅ CONCLUÍDO |
| Desenvolvimento/testes | SQLite | ✅ CONCLUÍDO |
| Produção | PostgreSQL 16 via Compose | ✅ CONCLUÍDO como baseline |
| Migrations | Alembic | ✅ CONCLUÍDO |
| Jobs | fila durável no banco + worker separado | ✅ CONCLUÍDO |
| STT | faster-whisper | ✅ CONCLUÍDO no código / 🟡 dependente de runtime/modelo |
| Diarização | pyannote.audio | 🟡 PARCIAL quanto à portabilidade do runtime |
| LLM | Ollama, modelo configurável (ex.: Qwen) | ✅ CONCLUÍDO no adapter / 🟡 dependente do serviço externo local |
| Exportação | TXT/Markdown/JSON/DOCX/PDF | ✅ CONCLUÍDO |
| Qualidade | pytest, coverage, Ruff, mypy, Bandit, pip-audit | 🟡 configurado, branch atual sem run |
| Container | Docker multi-stage + Compose local/produção | ✅ baseline existente |

Não existe `package.json`; o frontend não possui toolchain Node, bundler ou framework SPA.

## Arquitetura resumida

```text
Browser / Jinja2 UI
        │
        ▼
FastAPI routers
        │ auth + ownership
        ▼
Application services
        │
        ├── SQLAlchemy repositories / Unit of Work ──> SQLite/PostgreSQL
        ├── storage de áudio/arquivos
        └── ProcessingJob persistido
                         │
                         ▼
                  Worker separado
                         │
              ┌──────────┼───────────┐
              ▼          ▼           ▼
       faster-whisper  pyannote    Ollama/LLM
```

Detalhes completos: `docs/ARCHITECTURE.md`.

## Funcionalidades concluídas

### ✅ Reuniões e UI

- CRUD de reuniões via API/service/repository;
- páginas Jinja2 para autenticação, lista e detalhe de reunião;
- arquivos estáticos CSS/JS;
- gravação pelo navegador usando `MediaRecorder`;
- upload/uso da gravação no mesmo fluxo de áudio.

### ✅ Áudio

- staging de upload;
- validação de tamanho/formato;
- inspeção por `ffprobe`;
- persistência de metadados;
- storage configurável;
- regra de um áudio ativo por reunião via migration/contrato.

### ✅ Processamento assíncrono

- `ProcessingJob` persistido;
- worker durável separado do request HTTP;
- handlers para transcrição, diarização e análise;
- launcher unificado `run.py` para backend + worker;
- health e readiness endpoints.

### ✅ Transcrição

- provider `faster-whisper`;
- serviço e handler de transcrição;
- segmentos persistidos;
- testes de contrato/unitários existentes.

### ✅ Participantes e diarização de domínio

- modelos de speaker/participant;
- speaker segments;
- identificação/associação humana de participantes;
- provider Pyannote implementado.

### ✅ Inteligência por LLM

- adapter Ollama;
- análise estruturada persistida;
- metadados do provider;
- resumo e campos estruturados tratados na camada de serviço.

### ✅ Busca e exportação

- busca em conteúdo de reunião/transcrição com ownership;
- exportação TXT, Markdown, JSON, DOCX e PDF.

### ✅ Autenticação e autorização

- cadastro/login/logout;
- senha com scrypt + salt;
- sessão opaca com hash SHA-256 persistido;
- cookie HttpOnly, SameSite=Lax e Secure em staging/production;
- ownership por `Meeting.owner_id`;
- recursos de outro usuário retornam 404 para reduzir enumeração.

### ✅ Banco e infraestrutura baseline

- migrations `0001` a `0009`;
- SQLite para uso local/testes;
- PostgreSQL 16 em Compose de produção;
- migration container antes de web/worker;
- volumes persistentes;
- backup loop;
- `/health` e `/ready`.

## Funcionalidades parciais

### 🟡 Runtime de diarização multiplataforma

A branch atual já possui `app/infrastructure/media_runtime.py` com discovery de FFmpeg Shared no Windows e registro de DLLs, além de validação básica de FFmpeg no Linux. Porém a própria documentação de hardening define itens ainda não fechados e eles não aparecem integralmente no código:

- preflight funcional completo de Torch/TorchCodec/Pyannote;
- exceções específicas por causa de falha;
- matriz de versões homologadas;
- teste funcional real Windows + Linux/Docker;
- normalização central opcional de áudio;
- garantia de que diarização só seja anunciada como disponível quando todo runtime estiver operacional.

### 🟡 Validação da branch atual

Os quality gates existem, mas `fix/runtime-dependencies` não é branch de push contemplada nos workflows atuais e não há PR dela aberto. Assim, o head auditado não possui evidência de CI equivalente à de `develop`.

### 🟡 Deploy de produção

Existe baseline Docker/PostgreSQL/backup/readiness, mas não há evidência nesta auditoria de uma implantação pública homologada com TLS, proxy/rede, secrets manager, observabilidade externa e procedimento de restore validado.

## Não implementado / futuro

### 🔴 Provider OpenAI

`OPENAI_API_KEY` existe na configuração de ambiente, porém a árvore atual possui provider LLM operacional para Ollama e não mostra adapter OpenAI. Tratar a variável como reserva/legado até decisão explícita.

### 🔴 Recursos deliberadamente adiados

Não existem e não devem ser introduzidos sem necessidade comprovada:

- microserviços;
- Redis/Celery como requisito;
- Kubernetes;
- vector DB/RAG;
- SPA React/Vue/Angular;
- WebSocket como padrão;
- colaboração em tempo real.

## Bugs e inconsistências conhecidos

### 🐛 / ⚠️ Documentação antiga contradiz o código

- `docs/current/ARCHITECTURE.md` ainda trata Stack 14 como próxima etapa, apesar de código de produção existir;
- `docs/roadmap/AI_PIPELINE.md` afirma que providers de STT/diarização/LLM não existem, mas eles existem;
- `docs/roadmap/FRONTEND.md` afirma que UI de reuniões ainda não existe, mas templates e JavaScript correspondentes existem;
- README é mais novo que esses documentos, mas também deve ser lido como visão resumida, não como prova de testes atuais.

### 🐛 Runtime Pyannote/TorchCodec historicamente frágil

Há registro de falha `Could not load libtorchcodec` em Windows. Parte do remediation já entrou na branch, porém falta fechar o preflight completo.

### ⚠️ Dois entrypoints de worker

Existem `worker.py` e `app/workers/run.py` com responsabilidade praticamente equivalente. O launcher/Docker usam `python -m app.workers.run`. `worker.py` parece ser compatibilidade/legado e deve ser decidido antes de remoção; não remover sem teste de consumidores externos.

### ❓ Dependência `httpx2`

`requirements-dev.txt` fixa `httpx2==2.9.0`, enquanto os testes usam `fastapi.testclient.TestClient`. Confirmar em ambiente limpo se este pacote é intencional e necessário antes de alterar dependências.

## Segurança

### P0 — modo local sem autenticação em produção pública

Quando não existe nenhum usuário, `AuthService.authentication_enabled()` retorna falso e os guards permitem acesso em modo local. Isso é compatibilidade intencional para uso pessoal, porém uma instância pública recém-subida pode ficar acessível sem login até a criação da primeira conta.

**Recomendação:** antes de qualquer exposição pública, exigir um mecanismo explícito de bootstrap/flag que não permita fallback local em `production`, com testes de regressão. Não foi alterado nesta auditoria.

### P1 — proteção web de produção ainda precisa de hardening explícito

Não foi identificado nesta auditoria um mecanismo dedicado de CSRF nem rate limiting/anti-bruteforce para login/cadastro. `SameSite=Lax` ajuda, mas não substitui uma política completa para uma implantação pública.

### ✅ Segredos

Templates `.env.example`/`.env.production.example` existem. Segredos reais não devem ser commitados. A documentação criada nesta auditoria lista apenas nomes de variáveis e nunca valores privados.

## Performance e dívida técnica

- ⚠️ SQLite é adequado ao modo local, mas web + worker concorrentes podem sofrer contenção de escrita; produção já possui caminho PostgreSQL;
- ⚠️ jobs usam banco como fila — decisão simples e coerente para o porte atual, mas throughput/latência devem ser medidos antes de introduzir broker externo;
- ⚠️ workloads de Whisper/Pyannote são pesados em CPU e modelo; separar worker do web é correto, mas a capacidade ainda precisa ser homologada por máquina;
- ⚠️ frontend não possui testes automatizados de navegador/E2E; os testes atuais cobrem contratos Python e alguns artefatos de gravação, mas não substituem teste real de permissão/mídia por browser;
- ⚠️ documentação histórica deve ser claramente arquivada ou marcada para evitar regressões de contexto por agentes futuros.

## Variáveis de ambiente necessárias

Consulte `.env.example` e `.env.production.example`. Nomes relevantes, sem valores secretos:

- aplicação: `ENVIRONMENT`, `DEBUG`, `SECRET_KEY`, `HOST`, `PORT`;
- banco: `DATABASE_URL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE_SECONDS`, `DB_CONNECT_TIMEOUT_SECONDS`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `AMIP_PORT`;
- backup: `BACKUP_INTERVAL_SECONDS`, `BACKUP_RETENTION_DAYS`;
- mídia: `FFPROBE_BINARY`, `FFMPEG_BIN_DIR`, `FFPROBE_TIMEOUT_SECONDS`;
- IA: `LLM_PROVIDER`, `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, `OLLAMA_AUTO_START_LOCAL`, `OPENAI_API_KEY`, `HUGGINGFACE_TOKEN`;
- transcrição/diarização: `WHISPER_MODEL`, `WHISPER_LANGUAGE`, `PYANNOTE_MODEL`, `PYANNOTE_DEVICE`;
- storage: `STORAGE_PATH`, `MAX_UPLOAD_SIZE`;
- logs: `LOG_LEVEL`, `LOG_FILE`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`.

## Testes existentes

Há cobertura dedicada para API, áudio, autenticação, diagnostics, diarização, enums, erros, exportação, launcher, lifecycle config, meetings, migrations, packaging, participants, jobs persistentes, pipeline, processing, production readiness, recording, search, storage, transcription, Unit of Work e web.

### Resultado desta auditoria

| Validação | Resultado |
|---|---|
| Inspeção estática da árvore Git | ✅ concluída |
| Comparação `develop...fix/runtime-dependencies` | ✅ 35 ahead / 0 behind |
| CI no head atual | ⚠️ não existe run registrado |
| CI mais recente de `develop` | ✅ observado como sucesso no commit `600f7dbe...` |
| Docker workflow mais recente de `develop` | ✅ observado como sucesso no mesmo commit |
| `pip install` em ambiente limpo | ❓ não executado neste ambiente |
| Ruff | ❓ não executado no head atual |
| mypy | ❓ não executado no head atual |
| pytest + coverage | ❓ não executado no head atual |
| migrations test | ❓ não executado no head atual |
| Bandit | ❓ não executado no head atual |
| pip-audit | ❓ não executado no head atual |
| Docker build/Compose | ❓ não executado no head atual |
| startup real | ❓ não executado no head atual |

Não interpretar `❓` como falha; significa **sem evidência produzida nesta auditoria**.

## Prioridades

### P0 — bloqueia exposição segura

1. **Produção não pode depender do fallback “sem usuários = sem autenticação”.** Definir e testar bootstrap seguro para ambiente `production` antes de publicar externamente.

### P1 — necessário para próxima versão/merge

1. Reproduzir quality gates completos na branch atual em Python 3.11 e 3.12.
2. Validar instalação limpa das dependências web/worker/dev.
3. Fechar hardening do runtime FFmpeg/Torch/TorchCodec/Pyannote em Linux/Docker e Windows.
4. Validar build de `Dockerfile`, `compose.yaml` e `compose.production.yaml`.
5. Executar smoke real: migrations → backend → worker → `/health` → `/ready` → upload → transcrição; diarização/LLM quando credenciais/modelos locais estiverem disponíveis.

### P2 — melhoria importante

1. CSRF e rate limiting/anti-bruteforce para superfície pública.
2. Teste de restore de backup e documentação operacional.
3. Decidir destino de `worker.py` duplicado.
4. Confirmar intenção de `httpx2` no ambiente de desenvolvimento.
5. Criar testes E2E mínimos de UI/gravação em browser.
6. Marcar/arquivar roadmaps históricos obsoletos.

### P3 — futuro

1. observabilidade externa/metrics conforme necessidade;
2. otimização de busca (FTS) apenas se escala exigir;
3. broker externo, embeddings, SPA ou microserviços apenas mediante caso de uso medido.

## Próxima ação recomendada

Executar a **Sprint 1 do novo roadmap: Baseline reproduzível e gates da branch atual**. Ela deve validar — sem misturar novas features — instalação limpa, lint, typecheck, testes, segurança estática, migrations, Docker e startup. Só depois é seguro mexer em comportamento de produção ou concluir o hardening ML.

Ver `docs/ROADMAP.md`.
