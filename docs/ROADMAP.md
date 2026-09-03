# ROADMAP — Continuidade do AMIP

> Roadmap derivado da auditoria de 2026-09-03.  
> Este arquivo descreve **o que fazer depois**; a auditoria não iniciou nenhuma Sprint.

## Princípios

- cada Sprint deve ser pequena, testável e reversível;
- não misturar feature nova com correção de baseline;
- preservar o monólito modular e a separação web/worker;
- evitar Redis/Celery, microserviços, SPA, vector DB ou Kubernetes sem necessidade medida;
- toda alteração deve terminar com testes e documentação compatíveis;
- antes de começar qualquer Sprint, ler `CLAUDE.md`, `docs/PROJECT_STATUS.md`, `docs/ROADMAP.md` e `docs/ARCHITECTURE.md`.

## Sprint 1 — Baseline reproduzível da branch atual

**Prioridade:** P1  
**Objetivo:** provar em ambiente limpo que `fix/runtime-dependencies` instala, passa nos gates e inicia sem depender de estado oculto de uma máquina.

### Motivo

A branch está 35 commits à frente de `develop`, mas não possui workflow run registrado. Sem esse baseline, qualquer feature seguinte pode confundir erro novo com problema preexistente.

### Tarefas

- confirmar `git status` limpo no ambiente de trabalho;
- testar Python 3.11 e 3.12;
- instalar `requirements.txt`, `requirements-worker.txt` e `requirements-dev.txt` em venv limpa;
- validar se `httpx2==2.9.0` é realmente intencional/necessário;
- executar Ruff, mypy, pytest/coverage, migrations, Bandit e pip-audit;
- validar `docker compose config` local e produção;
- buildar targets `web` e `worker`;
- executar `python run.py` e confirmar `/health` + `/ready`;
- registrar erros sem corrigi-los de forma oportunista; correções necessárias devem virar commits pequenos na própria Sprint.

### Dependências

- Python 3.11/3.12;
- FFmpeg para caminhos que o exigirem;
- Docker para validação de imagem/Compose.

### Áreas prováveis

`.github/workflows/`, `requirements*.txt`, `pyproject.toml`, `Dockerfile`, `compose*.yaml`, `run.py`, `tests/`.

### Testes necessários

```bash
ruff check app tests main.py
mypy app main.py
pytest --cov=app --cov-fail-under=80 tests/
pytest -q tests/test_migrations.py
bandit -q -r app -ll
bandit -q main.py -ll
pip-audit -r requirements.txt
docker compose config --quiet
docker compose build
```

### Critérios de aceite

- instalação limpa reproduzível;
- gates verdes ou falhas documentadas e corrigidas dentro de escopo;
- backend e worker iniciam juntos;
- `/health` responde 2xx;
- `/ready` responde 2xx com banco disponível;
- nenhum segredo incluído em logs/documentação;
- resultado registrado em `docs/PROJECT_STATUS.md`.

### Riscos

Dependências ML podem variar por SO; não mascarar falha instalando versões ad hoc fora dos arquivos do projeto.

---

## Sprint 2 — Bootstrap seguro de autenticação em produção

**Prioridade:** P0 para exposição pública  
**Objetivo:** impedir que uma instância em `production` fique aberta apenas porque ainda não existe usuário cadastrado.

### Motivo

Hoje o modo local é habilitado implicitamente quando a tabela de usuários está vazia. Isso é útil localmente, mas perigoso em uma implantação pública recém-subida.

### Tarefas

- definir comportamento explícito por ambiente;
- manter compatibilidade do modo local em desenvolvimento, se essa continuar sendo a decisão;
- em produção, bloquear acesso protegido antes do bootstrap seguro;
- definir fluxo de criação da primeira conta/admin sem token hardcoded;
- adicionar testes de produção e regressão do modo local;
- atualizar `SECURITY`/setup operacional.

### Dependências

Sprint 1 verde.

### Áreas prováveis

`app/services/auth_service.py`, `app/api/dependencies.py`, `app/api/auth.py`, `app/config/security.py`, `.env*.example`, `tests/test_auth.py`, `tests/test_production_readiness.py`.

### Testes necessários

- production + zero usuários => recursos protegidos não ficam públicos;
- development/local + zero usuários => comportamento definido continua funcionando;
- primeiro usuário => ownership legado continua correto;
- login/logout/session continuam funcionando;
- acesso cruzado continua 404.

### Critérios de aceite

Nenhuma implantação `production` fica utilizável anonimamente por ausência de conta.

### Riscos

Quebrar o fluxo pessoal/local existente. A mudança deve ser condicionada por ambiente/configuração e coberta por testes.

---

## Sprint 3 — Hardening do runtime de mídia e diarização

**Prioridade:** P1  
**Objetivo:** fechar a portabilidade Windows/Linux/Docker do runtime FFmpeg/Torch/TorchCodec/Pyannote.

### Motivo

Parte da descoberta de FFmpeg Shared já foi implementada, mas o preflight funcional completo e a matriz homologada ainda não estão fechados.

### Tarefas

- mapear a implementação atual contra `docs/FUTURE_SPRINT_MEDIA_RUNTIME_HARDENING.md`;
- implementar/fechar somente os itens faltantes do preflight;
- diferenciar falha de FFmpeg, Torch, TorchCodec, Pyannote, modelo/token e decode;
- documentar matriz de versões homologada;
- confirmar comportamento CPU;
- validar Windows, Linux e Docker;
- garantir que o worker não anuncie diarização disponível quando runtime estiver incompleto.

### Dependências

Sprint 1 verde.

### Áreas prováveis

`app/infrastructure/media_runtime.py`, `app/providers/speaker_identifier/pyannote.py`, `app/config/audio.py`, `app/workers/`, `requirements-worker.txt`, `Dockerfile`, `scripts/check_diarization.py`, `tests/`.

### Testes necessários

- FFmpeg ausente;
- Windows com build static;
- Windows com Shared;
- Linux com FFmpeg válido/ausente;
- TorchCodec incompatível;
- token/modelo Pyannote ausente;
- CPU funcional;
- Docker worker preflight.

### Critérios de aceite

Preflight determinístico, mensagens de erro específicas e diarização real validada em pelo menos Linux/Docker e Windows homologado.

### Riscos

Dependências nativas grandes e sensíveis a versão. Não pinçar versões aleatórias por máquina.

---

## Sprint 4 — Hardening HTTP de autenticação

**Prioridade:** P2  
**Objetivo:** preparar a superfície de sessão para uso público com controles explícitos contra abuso e requisições indevidas.

### Motivo

Cookie `HttpOnly`, `SameSite=Lax` e `Secure` em produção já existem, mas não foi identificado mecanismo dedicado de CSRF nem rate limiting/anti-bruteforce.

### Tarefas

- definir threat model mínimo;
- introduzir proteção CSRF adequada aos endpoints mutáveis baseados em cookie;
- limitar tentativas de login/cadastro sem criar dependência distribuída desnecessária;
- validar headers/cookies em produção;
- documentar política.

### Dependências

Sprint 2.

### Áreas prováveis

`app/api/auth.py`, demais routers mutáveis, middleware/dependencies, templates/JS, testes de segurança.

### Testes necessários

- request mutável sem token/origem válida é rejeitado;
- login legítimo continua funcionando;
- rate limit tem comportamento previsível;
- cookies preservam flags de produção.

### Critérios de aceite

Controles automatizados e documentados sem prejudicar o modo local homologado.

### Riscos

CSRF mal integrado pode quebrar formulários/fetches existentes.

---

## Sprint 5 — Smoke E2E do pipeline principal

**Prioridade:** P1/P2  
**Objetivo:** provar a vertical real com menos mocks.

### Motivo

A suíte Python é ampla, mas o valor do AMIP depende da integração entre upload, worker e providers locais.

### Tarefas

- criar roteiro reproduzível com áudio pequeno de fixture legalmente incluível;
- reunião → upload → job → transcrição;
- validar diarização quando ambiente ML estiver disponível;
- validar análise via Ollama quando serviço/modelo estiver disponível;
- validar busca e exportação após processamento;
- separar testes obrigatórios de CI dos testes pesados opcionais.

### Dependências

Sprints 1 e 3.

### Áreas prováveis

`scripts/`, `tests/`, `app/workers/`, providers, documentação de setup.

### Testes necessários

Smoke local e Docker; paths de falha de provider devem ser explícitos.

### Critérios de aceite

Uma IA ou desenvolvedor novo consegue executar o pipeline documentado e reconhecer claramente o que foi aprovado ou pulado.

### Riscos

Model downloads e LLM local tornam CI pesado; manter gates pesados opt-in quando adequado.

---

## Sprint 6 — Operação de produção: backup e restore

**Prioridade:** P2  
**Objetivo:** provar recuperação, não apenas criação de backup.

### Motivo

Existe serviço de backup, mas continuidade operacional exige teste de restauração.

### Tarefas

- documentar artefatos gerados;
- executar backup de banco + storage de teste;
- restaurar em ambiente limpo;
- validar migrations/ownership/arquivos após restore;
- definir retenção e falhas observáveis.

### Dependências

Sprint 1.

### Áreas prováveis

`ops/backup/`, `compose.production.yaml`, `docs/PRODUCTION.md`, scripts/testes operacionais.

### Critérios de aceite

Restore reproduzível documentado e testado sem dados reais.

### Riscos

Backup sem storage e banco consistentes pode produzir restore parcial.

---

## Sprint 7 — Limpeza documental e compatibilidade de entrypoints

**Prioridade:** P2  
**Objetivo:** reduzir ambiguidade para humanos e agentes sem refatorar comportamento.

### Motivo

Há roadmaps históricos que contradizem o código e dois entrypoints de worker.

### Tarefas

- classificar `docs/roadmap/AI_PIPELINE.md` e `docs/roadmap/FRONTEND.md` como histórico ou reescrevê-los;
- revisar `docs/current/*` contra os documentos canônicos novos;
- decidir se `worker.py` é alias suportado ou legado removível;
- manter redirect/documentação de compatibilidade se necessário;
- evitar apagar ADRs históricos.

### Dependências

Sprint 1.

### Áreas prováveis

`docs/`, `worker.py`, `app/workers/run.py`, README.

### Testes necessários

`tests/test_documentation_structure.py`, `tests/test_launcher.py` e qualquer teste de packaging/entrypoint relevante.

### Critérios de aceite

Existe uma única fonte clara de estado/roadmap/arquitetura/setup, sem quebrar comandos suportados.

### Riscos

Remover arquivo aparentemente redundante que algum ambiente externo ainda usa.

---

## Futuro somente com evidência

Itens abaixo permanecem P3 e não devem virar Sprint por entusiasmo arquitetural:

- Redis/Celery/RQ/Dramatiq;
- WebSockets;
- PostgreSQL FTS avançado;
- embeddings/vector DB/RAG;
- SPA;
- microserviços;
- GPU orchestration/Kubernetes;
- colaboração em tempo real.

## Ordem recomendada

```text
Sprint 1 — baseline reproduzível
   ↓
Sprint 2 — bootstrap seguro de produção (P0)
   ↓
Sprint 3 — runtime de mídia/diarização
   ↓
Sprint 5 — smoke E2E
   ↓
Sprint 4 / 6 / 7 — hardening e manutenção
```

A próxima Sprint é **Sprint 1**, porque ela reduz incerteza antes de qualquer mudança de comportamento.
