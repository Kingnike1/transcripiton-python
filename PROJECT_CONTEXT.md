# PROJECT_CONTEXT.md

## Projeto

**AMIP — AI Meeting Intelligence Platform**

O AMIP transforma áudio de reuniões em transcrição, separação de falas e, progressivamente, inteligência estruturada.

## Capacidade implementada

- FastAPI + SQLAlchemy + Pydantic + Jinja2;
- CRUD e interface de reuniões;
- upload seguro de áudio com streaming/staging e `ffprobe`;
- Alembic e migrations versionadas;
- jobs persistentes + worker separado;
- claim, lease, heartbeat, retry e recovery;
- transcrição local com `faster-whisper`;
- persistência de transcrição e segmentos;
- diarização local com `pyannote.audio` quando configurado;
- `speaker_segments` reconciliados com texto;
- Stack 11: identidade de participantes por reunião, edição e confirmação manual de `SPEAKER_XX` → nome;
- Docker/Compose para uso local com migrations, web e worker;
- CI/Quality com Python 3.11/3.12, Ruff, mypy, migrations, Bandit e `pip-audit`.

## Pipeline atual

```text
Reunião
  ↓
Áudio
  ↓
ProcessingJob: TRANSCRIBE
  ↓
Transcrição + segmentos
  ↓
ProcessingJob: DIARIZE
  ↓
Speaker segments
  ↓
Participantes confirmados
  ↓
Stack 12 — inteligência por LLM
```

## Arquitetura vigente

Monólito modular em camadas, com processo web separado do worker pesado. SQLite e storage local continuam adequados ao estágio de uso pessoal/local. Redis, Celery, microservices e Kubernetes continuam adiados até necessidade comprovada.

A identidade humana não é gravada dentro de cada `SpeakerSegment`: `Participant` pertence à reunião e mapeia `speaker_label` para `display_name` + `confirmed`.

## Próxima prioridade

**Stack 12 — Inteligência por LLM**: resumo estruturado, action items, decisões, riscos e follow-ups, mantendo rastreabilidade para transcrição e participantes.

Depois dela:

1. Stack 13 — autenticação/autorização;
2. Stack 14 — infraestrutura de produção;
3. Stack 15 — busca;
4. Stack 16 — exportação;
5. Stack 17 — gravação por microfone.

## Restrições e decisões importantes

- não usar microservices por antecipação;
- não colocar processamento pesado no processo HTTP;
- migrations são externas ao startup;
- não expor detalhes internos em erros HTTP;
- não declarar roadmap como funcionalidade entregue;
- identidade de participante é local à reunião, não reconhecimento biométrico global;
- `main` é release estável; `develop` é integração.

## Onde buscar a verdade

1. código/migrations/testes/CI;
2. `PROJECT_GOVERNANCE.md`;
3. `PROJECT_STATE.MD`;
4. `TECH_DECISIONS.md` + ADRs;
5. `docs/current/`;
6. `docs/06_BACKLOG.md`;
7. `docs/roadmap/` apenas para futuro;
8. `docs/archive/` apenas para histórico.

**Document Version:** 3.0  
**Last Updated:** 2026-08-17  
**Status:** Active
