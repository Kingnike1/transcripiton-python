# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Stack atual:** Stack 11 — Identificação de participantes  
**Branch de integração:** `develop`  
**Último merge:** PR #14 — Stack 9 Empacotamento  
**Commit de integração:** `3e34e9ee4d958ce08af89867400b08ed23e83137`  
**Status:** Stacks 9 e 10 concluídas e integradas; Stack 11 é a próxima prioridade

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento de áudio;
- jobs duráveis e worker separado;
- transcrição local com faster-whisper;
- transcrição/segmentos persistidos;
- diarização local com pyannote quando `HUGGINGFACE_TOKEN` está configurado;
- speaker segments persistidos e reconciliados com o texto;
- APIs para transcrição e diarização;
- UI para o fluxo de transcrição;
- Dockerfile multi-target web/worker;
- Compose com migrations, web e worker;
- volumes persistentes para dados e cache de modelos;
- ffmpeg/ffprobe dentro do runtime;
- healthcheck, smoke test e documentação operacional/backup.

## Stack 10 — Diarização — CONCLUÍDA

- [x] provider `pyannote.audio` atrás de `ISpeakerIdentifier`;
- [x] modelo `speaker-diarization-community-1`;
- [x] estado `DIARIZED`;
- [x] job `DIARIZE` no worker durável;
- [x] persistência e consulta de `speaker_segments`;
- [x] alinhamento com segmentos da transcrição;
- [x] CI + Quality verdes;
- [x] PR #13 integrado em `develop`.

## Stack 9 — Empacotamento — CONCLUÍDA

- [x] Dockerfile multi-target `web` / `worker`;
- [x] imagem com `ffmpeg`/`ffprobe`;
- [x] Compose com migration one-shot, web e worker;
- [x] migration bloqueia inicialização até concluir com sucesso;
- [x] volume persistente para SQLite/storage/logs;
- [x] volume separado para cache de modelos;
- [x] healthcheck da aplicação;
- [x] entrypoint `python -m app.workers.run`;
- [x] worker mantém transcrição ativa sem token pyannote;
- [x] smoke test operacional em `scripts/smoke.py`;
- [x] documentação operacional e backup;
- [x] workflow Docker valida Compose e constrói web target;
- [x] CI + Quality + Docker verdes no PR #14;
- [x] PR #14 integrado em `develop`.

## Próximas stacks

1. Stack 11 — identificação de participantes;
2. Stack 12 — inteligência por LLM;
3. Stack 13 — autenticação/autorização;
4. Stack 14 — infraestrutura de produção;
5. Stack 15 — busca;
6. Stack 16 — exportação;
7. Stack 17 — gravação por microfone.

## Pendência operacional

O smoke test com áudio real e os modelos efetivamente baixados deve ser executado na máquina que rodará o AMIP. O CI usa providers fake para não baixar modelos pesados.

**Document Version:** 6.1  
**Status:** Active
