# SETUP — AMIP / Transcripition

> Guia canônico para um novo desenvolvedor ou agente reproduzir o projeto sem depender de configuração escondida de outra máquina.

## 1. Pré-requisitos

### Recomendado

- Git;
- Python **3.11 ou 3.12**;
- FFmpeg/ffprobe;
- Docker + Docker Compose para validação/container;
- Ollama apenas para análise LLM real;
- acesso ao modelo Pyannote/Hugging Face apenas para diarização real.

A configuração de CI e `pyproject.toml` tem Python 3.11/3.12 como baseline. Não assumir compatibilidade de Python 3.13/3.14 sem executar os gates.

## 2. Clonar e escolher a branch

```bash
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python
git fetch --all --prune
git checkout fix/runtime-dependencies
```

Antes de alterar qualquer coisa:

```bash
git branch --show-current
git status --short --branch
git log -5 --oneline
```

Leia obrigatoriamente:

```text
CLAUDE.md
docs/PROJECT_STATUS.md
docs/ROADMAP.md
docs/ARCHITECTURE.md
```

## 3. Criar ambiente Python

### Linux/macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Se a máquina tiver Python 3.11 como baseline homologado:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 4. Instalar dependências

### Apenas backend web

```bash
pip install -r requirements.txt
```

### Aplicação completa com worker ML

```bash
pip install -r requirements-worker.txt
```

`requirements-worker.txt` inclui `requirements.txt` e adiciona faster-whisper/pyannote.audio.

### Desenvolvimento e quality gates

```bash
pip install -r requirements-dev.txt
```

Para uma máquina de desenvolvimento que executará tudo:

```bash
pip install -r requirements-worker.txt -r requirements-dev.txt
```

**Não altere versões apenas para “fazer instalar” sem registrar o erro.** A próxima Sprint deve primeiro provar uma instalação limpa.

## 5. Configurar ambiente

Crie o arquivo local a partir do template:

### Linux/macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Nunca commite `.env`, tokens, chaves ou senhas reais.

### Grupos de variáveis

O template define nomes para:

- aplicação: `ENVIRONMENT`, `DEBUG`, `SECRET_KEY`, `HOST`, `PORT`;
- banco: `DATABASE_URL`, pool/connect timeout e variáveis PostgreSQL;
- backup;
- FFmpeg/ffprobe;
- Ollama/LLM;
- Hugging Face/Pyannote;
- Whisper;
- storage;
- logging.

Use os templates como referência de nomes. Em produção, gere segredos fortes fora do Git.

## 6. Preparar banco

Execute migrations:

```bash
alembic upgrade head
```

Verifique o head quando necessário:

```bash
alembic current
alembic heads
```

No modo local padrão, o projeto suporta SQLite. Produção usa PostgreSQL via Compose.

## 7. Verificar runtime de mídia

Confirme FFmpeg:

```bash
ffmpeg -version
ffprobe -version
```

Para diarização:

```bash
python scripts/check_diarization.py
```

No Windows, se a descoberta automática não encontrar uma build Shared válida, configure `FFMPEG_BIN_DIR` no `.env` para o diretório `bin` correto. Não coloque caminho específico de uma máquina no código ou documentação compartilhada.

## 8. Executar

### Opção recomendada — launcher unificado

```bash
python run.py
```

Esse comando inicia o backend e o worker e monitora ambos.

Por padrão, a aplicação fica no host/porta configurados. O ambiente de desenvolvimento do template usa loopback.

### Executar separadamente

Terminal 1:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
python -m app.workers.run
```

### Diagnóstico sem iniciar a aplicação

```bash
python run.py --diagnostics
```

O bundle de diagnóstico deve ser sanitizado e não deve incluir `.env`.

## 9. Verificar saúde

Com a aplicação ativa:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

- `/health` prova que o processo HTTP responde;
- `/ready` também verifica conectividade com o banco.

## 10. Ollama / análise LLM

O código possui adapter Ollama. Para teste real:

1. instalar/iniciar Ollama na máquina que hospedará o serviço;
2. disponibilizar o modelo configurado em `OLLAMA_MODEL`;
3. garantir que o worker alcance `OLLAMA_URL`;
4. não tratar `OPENAI_API_KEY` como integração ativa — nenhum adapter OpenAI foi identificado na branch auditada.

## 11. Pyannote / diarização

Para teste real:

1. aceitar os termos do modelo aplicável no Hugging Face, quando exigido;
2. configurar `HUGGINGFACE_TOKEN` localmente;
3. garantir FFmpeg/Torch/TorchCodec/Pyannote compatíveis;
4. executar o check de diarização antes de processar reunião real.

Nunca imprimir o token em diagnóstico, teste ou log.

## 12. Executar testes e quality gates

Execute na raiz:

```bash
ruff check app tests main.py
mypy app main.py
pytest --cov=app --cov-fail-under=80 tests/
pytest -q tests/test_migrations.py
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
```

Se algo falhar, **registre a falha antes de corrigir**. Não reduza cobertura, ignore type errors ou desabilite scanner apenas para deixar o gate verde.

## 13. Build Docker local

Primeiro valide a configuração:

```bash
docker compose config --quiet
```

Build:

```bash
docker compose build
```

Executar:

```bash
docker compose up --build
```

Encerrar:

```bash
docker compose down
```

O Compose local usa SQLite em volume e serviços separados de migration, web e worker.

## 14. Build/validação de produção

Crie um arquivo local a partir do template sem commitá-lo:

```bash
cp .env.production.example .env.production
```

Preencha valores de produção fora do Git, incluindo senha PostgreSQL e `SECRET_KEY` forte.

Valide:

```bash
docker compose -f compose.production.yaml config --quiet
```

Build:

```bash
docker compose -f compose.production.yaml build
```

Subida de laboratório:

```bash
docker compose -f compose.production.yaml up -d
```

### Alerta P0

**Não exponha a instância à internet antes de resolver/mitigar o bootstrap de autenticação.** No código atual, se nenhuma conta existe, o modo local permite acesso aos recursos protegidos. `ENVIRONMENT=production` não desativa automaticamente esse fallback.

## 15. Smoke mínimo recomendado

Depois que os gates básicos passarem:

1. migrations aplicadas;
2. `python run.py` inicia backend + worker;
3. `/health` retorna sucesso;
4. `/ready` retorna sucesso;
5. abrir UI;
6. criar reunião;
7. enviar áudio pequeno válido;
8. confirmar criação/processamento do job;
9. confirmar transcrição quando provider estiver disponível;
10. confirmar diarização quando runtime/token estiverem disponíveis;
11. confirmar análise quando Ollama estiver disponível;
12. testar busca/exportação.

Diferencie **SKIPPED por dependência externa não configurada** de **FAILED por bug**.

## 16. Comandos Git antes de uma mudança

```bash
git fetch --all --prune
git status --short --branch
git log --oneline --decorate -10
git diff
git diff --staged
```

Não desenvolver diretamente em `main`. Respeite o fluxo e a política atual do projeto/branch definida para a Sprint.

## 17. Checklist para outra IA

Antes de implementar:

```text
[ ] Li CLAUDE.md
[ ] Li docs/PROJECT_STATUS.md
[ ] Li docs/ROADMAP.md
[ ] Li docs/ARCHITECTURE.md
[ ] Confirmei branch e git status
[ ] Confirmei commit-base da tarefa
[ ] Rodei ou registrei baseline dos testes
[ ] Não expus segredos
[ ] Entendi web x worker x providers
[ ] Sei os critérios de aceite da Sprint
```

Depois de implementar:

```text
[ ] Mudança pequena e reversível
[ ] Testes específicos verdes
[ ] Quality gates relevantes verdes
[ ] Build/startup relevante validado
[ ] Nenhum segredo/log sensível
[ ] Documentação de estado atualizada se necessário
[ ] Git diff revisado antes do commit
```
