# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Stack atual:** Stack 9 — Empacotamento para uso interno  
**Branch:** `agent/sprint-9-packaging`  
**Branch de integração:** `develop`  
**Último merge:** PR #13 — Stack 10 Diarização  
**Commit de integração:** `8d0734e30526ff7fa0b282053e96ad25ea65ce1b`  
**Status:** Stack 10 concluída fora de ordem; Stack 9 implementada e em fechamento por PR/CI

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento de áudio;
- jobs duráveis e worker separado;
- transcrição local com faster-whisper;
- transcrição/segmentos persistidos;
- diarização local com pyannote quando `HUGGINGFACE_TOKEN` está configurado;
- speaker segments persistidos e reconciliados com o texto;
- APIs para transcrição e diarização;
- UI para o fluxo de transcrição.

## Stack 10 — Diarização — CONCLUÍDA

- [x] provider `pyannote.audio` atrás de `ISpeakerIdentifier`;
- [x] modelo `speaker-diarization-community-1`;
- [x] estado `DIARIZED`;
- [x] job `DIARIZE` no worker durável;
- [x] persistência e consulta de `speaker_segments`;
- [x] alinhamento com segmentos da transcrição;
- [x] CI + Quality verdes;
- [x] PR #13 integrado em `develop`.

## Stack 9 — Empacotamento — IMPLEMENTADA NA BRANCH

- [x] Dockerfile multi-target `web` / `worker`;
- [x] imagem com `ffmpeg`/`ffprobe`;
- [x] Compose com migration one-shot, web e worker;
- [x] migration bloqueia inicialização até concluir com sucesso;
- [x] volume persistente para SQLite/storage/logs;
- [x] volume separado para cache de modelos;
- [x] healthcheck da aplicação;
- [x] entrypoint `python -m app.workers.run`;
- [x] worker mantém transcrição ativa mesmo sem token pyannote;
- [x] smoke test operacional em `scripts/smoke.py`;
- [x] documentação operacional e backup;
- [x] workflow Docker valida Compose e constrói web target;
- [x] testes estáticos do contrato de empacotamento.

## Gate final da Stack 9

1. abrir PR para `develop`;
2. CI + Quality + Docker verdes;
3. corrigir regressões se houver;
4. merge na `develop`;
5. registrar fechamento oficial.

## Próximas stacks

- Stack 11 — identificação de participantes;
- Stack 12 — inteligência por LLM;
- Stack 13 — autenticação/autorização;
- Stack 14 — infraestrutura de produção;
- Stack 15 — busca;
- Stack 16 — exportação;
- Stack 17 — gravação por microfone.

**Document Version:** 6.0  
**Status:** Active
