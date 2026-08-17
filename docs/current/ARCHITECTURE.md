# Arquitetura atual do AMIP

## Visão

O AMIP é um **monólito modular em camadas** com processos web e worker. Ambos compartilham banco/storage; processamento pesado não roda dentro do request HTTP.

```text
Browser
  ↓ session cookie
FastAPI / Jinja2 UI
  ↓ auth + ownership
Application Services
  ↓
SQLAlchemy / Repositories
  ↓
Database

FastAPI ── cria/consulta ──> ProcessingJob
                              ↓
                         database queue
                              ↓
                         Worker separado
                              ↓
             STT / diarization / LLM providers
```

## Estado real

| Área | Estado |
|---|---|
| CRUD de reuniões | Implementado |
| Upload/inspeção de áudio | Implementado |
| Jobs persistentes/worker | Implementado |
| Transcrição real | Implementada com `faster-whisper` |
| Diarização | Implementada com `pyannote.audio` quando configurado |
| Identificação de participantes | Implementada |
| Inteligência por LLM | Implementada via Ollama/Qwen3 |
| Autenticação | Implementada — Stack 13 |
| Ownership/autorização | Implementados — Stack 13 |
| Empacotamento Docker local | Implementado |
| Infra pública production-ready | Ainda não implementada |

## Pipeline

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
Structured intelligence
```

## Boundary de segurança

`User` é a identidade de conta. `AuthSession` implementa sessão revogável por token opaco. `Meeting.owner_id` é a raiz da autorização: áudio, transcrição, diarização, participantes, análise e jobs são liberados somente se a reunião-pai pertence ao usuário atual.

Workers não recebem cookie nem identidade HTTP; eles processam jobs internos já persistidos. A autorização acontece na fronteira web/API antes da criação/consulta dos recursos.

O modo local sem contas continua disponível para compatibilidade. Quando a primeira conta é criada, reuniões legadas sem owner são associadas a ela. Depois disso, a aplicação passa a exigir sessão para o workspace e APIs protegidas.

## Segurança de credenciais

- senha: scrypt + salt aleatório;
- comparação: tempo constante;
- sessão: token aleatório opaco;
- banco: somente SHA-256 do token;
- cookie: HttpOnly, SameSite=Lax e Secure em staging/produção;
- acesso cruzado: 404 para reduzir enumeração de recursos.

## Quality gates

- Python 3.11 e 3.12;
- pytest + cobertura >=80%;
- Ruff;
- mypy;
- migration integrity;
- Bandit;
- `pip-audit`;
- validação Docker/Compose.

## Próxima fronteira arquitetural

**Stack 14 — Infraestrutura de produção**: preparar banco, storage, backups, observabilidade, hardening e deployment sem introduzir microserviços sem necessidade comprovada.

## ADRs relacionados

ADRs 017–027 cobrem fundação, jobs, STT, participantes e LLM. A Stack 13 adiciona **ADR-028 — authentication and resource ownership**.

---

**Status:** Active  
**Last Updated:** 2026-08-17
