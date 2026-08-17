# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 8 — Interface utilizável  
**Branch de integração:** `develop`  
**Último merge:** PR #11 — Sprint 7  
**Commit de integração:** `99e9b79b0202591faab4cd5e9f313bde66b5f6d3`  
**Status:** Sprint 7 concluída e integrada; próxima prioridade é a interface ponta a ponta

## Baseline

A Sprint 6B fornece a base durável de processamento: `ProcessingJob`, worker separado, claim, lease, heartbeat, retry, recovery, progresso e API de acompanhamento.

A Sprint 7 foi integrada em `develop` pelo PR #11 e entrega o primeiro vertical slice real de transcrição do AMIP.

## Sprint 7 — concluída

- [x] provider local `faster-whisper` isolado atrás de `ITranscriber`.
- [x] configuração inicial: modelo `base`, CPU, `int8`, beam size e VAD configuráveis.
- [x] detecção automática de idioma ou idioma fixo configurável.
- [x] consumo completo do generator do faster-whisper.
- [x] normalização de texto, timestamps e confiança por segmento.
- [x] `Transcription` persistida por áudio.
- [x] `TranscriptionSegment` persistido com sequência, início, fim, texto e confiança.
- [x] migration `0005_transcription_segments`.
- [x] estado de reunião `TRANSCRIBING` → `TRANSCRIBED`.
- [x] compatibilidade preservada para `TRANSCRIBING` → `DIARIZING` no pipeline futuro.
- [x] handler durável `TRANSCRIBE` integrado ao `JobWorker`.
- [x] heartbeat permanece ativo enquanto o provider executa transcrições longas.
- [x] retry recuperável não marca a reunião como `FAILED`; apenas falha terminal faz isso.
- [x] idempotência: resultado já persistido é reutilizado.
- [x] proteção contra path traversal ao resolver o arquivo de áudio.
- [x] API `GET /api/meetings/{meeting_id}/transcription` com segmentos.
- [x] dependências pesadas do STT isoladas em `requirements-worker.txt`.
- [x] testes com provider fake e adapter fake, sem download de modelo no CI.
- [x] PR #11 com CI verde.
- [x] PR #11 com Quality verde.
- [x] merge na `develop` concluído.

## Validação de fechamento

Na execução final do PR:

- suíte principal: **128 testes coletados e aprovados após a correção de compatibilidade**;
- cobertura permaneceu acima do gate de 80%; na execução anterior à correção, a cobertura medida foi **88,25%**;
- Python 3.12: verde;
- Ruff: verde;
- mypy: verde;
- migration integrity: verde;
- Bandit: verde;
- `pip-audit`: verde.

A validação com áudio real usando o modelo Whisper permanece um smoke test operacional local, pois baixar/carregar o modelo não faz parte do CI automatizado.

## Capacidade atual

### Funcional

- CRUD de reuniões;
- upload/armazenamento de áudio;
- jobs duráveis e worker separado;
- retry/heartbeat/recovery;
- transcrição real local com faster-whisper;
- transcrição e segmentos persistidos;
- consulta da transcrição pela API.

### Próxima prioridade — Sprint 8

Criar o primeiro fluxo humano ponta a ponta:

1. criar/listar reunião;
2. enviar áudio;
3. iniciar transcrição;
4. acompanhar job/progresso;
5. visualizar texto e segmentos;
6. apresentar estados de erro/retry/conclusão com clareza.

### Ainda não funcional

- interface completa de uso ponta a ponta;
- empacotamento simplificado para uso interno;
- diarização de speakers;
- identificação de participantes;
- análise por LLM, resumos e action items;
- autenticação/autorização;
- deploy público production-ready.

**Document Version:** 4.1  
**Status:** Active
