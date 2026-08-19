# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-18  
**Fase atual:** Validação operacional pós-Stack 17  
**Branch de integração:** `develop`  
**Branch de correções:** `agent/post-manus-fixes`  
**Último merge funcional:** PR #21 — Stack 17 Gravação por microfone  
**Status:** Stacks 7–17 concluídas; correções pós-Manus em validação

## Resultado da primeira validação Manus

- 30 casos consolidados;
- 23 PASS;
- 1 FAIL: gate mypy;
- 6 BLOCKED por limitações/dependências do ambiente;
- sem bug CRITICAL ou HIGH confirmado nos fluxos efetivamente executados.

## Correções pós-Manus nesta branch

### 1. Gate mypy

- [x] stubs internos de NumPy/Torch/Pyannote deixam de fazer parte do contrato de type-check do AMIP;
- [x] adapters do próprio projeto continuam sendo verificados;
- [x] nulabilidade real do adapter Pyannote corrigida;
- [x] retorno nulo de pipeline/annotation gera erro operacional explícito;
- [ ] confirmar gate mypy verde no GitHub Actions.

### 2. Documentação Docker

- [x] `docs/current/DEPLOYMENT.md` sincronizado com a infraestrutura real;
- [x] Dockerfile oficial documentado;
- [x] `compose.yaml` local documentado;
- [x] `compose.production.yaml` documentado;
- [x] `.env.production.example` criado;
- [x] README sincronizado;
- [ ] confirmar gate documental/CI verde.

### 4. Hugging Face + Pyannote

- [x] configuração existente de `HUGGINGFACE_TOKEN`, `PYANNOTE_MODEL` e `PYANNOTE_DEVICE` documentada;
- [x] `scripts/check_diarization.py` criado para preflight sem imprimir secrets;
- [x] adapter Pyannote endurecido contra pipeline/resultado nulo;
- [x] testes adicionais do adapter;
- [ ] inserir token real de leitura no `.env`/`.env.production` da máquina de uso;
- [ ] aceitar condições do modelo configurado na conta Hugging Face quando exigido;
- [ ] executar `python scripts/check_diarization.py` na máquina real;
- [ ] executar primeira diarização real e confirmar download/cache do modelo.

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- gravação de reunião pelo microfone do navegador;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando token/modelo estão configurados;
- identificação/confirmação de participantes;
- inteligência estruturada local via Ollama + Qwen3;
- autenticação, sessões revogáveis e ownership;
- baseline de produção com PostgreSQL, migrations, Docker, web, worker e backups;
- busca textual ownership-aware;
- exportação TXT, Markdown, JSON, DOCX e PDF.

## Pendências operacionais após estas correções

- fornecer/configurar o `HUGGINGFACE_TOKEN` real na máquina de uso;
- instalar Ollama e baixar `qwen3:4b` para smoke test real;
- repetir diarização, participantes e LLM com dependências reais;
- smoke test da gravação em navegador com microfone real via HTTPS/localhost;
- validar Docker/Compose em host com Docker disponível;
- configurar destino off-host para backups;
- configurar proxy/TLS e monitor externo;
- branch protection administrativa da `main` quando permissões permitirem.

## Próximo gate

Abrir PR das correções contra `develop` e integrar somente com CI, Quality e Docker verdes.

**Document Version:** 13.2  
**Status:** Active
