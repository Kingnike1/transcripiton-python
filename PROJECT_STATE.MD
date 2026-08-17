# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 7 — Transcrição real  
**Branch:** `agent/sprint-7-transcription`  
**Branch base / integração:** `develop`  
**Status:** implementação funcional concluída na branch; fechamento por PR/CI em andamento

## Baseline

A Sprint 6B está integrada em `develop` e fornece a base durável de processamento: `ProcessingJob`, worker separado, claim, lease, heartbeat, retry, recovery, progresso e API de acompanhamento.

A Sprint 7 está 23 commits à frente de `develop` e adiciona o primeiro vertical slice de transcrição real do projeto.

## Sprint 7 — entregue na branch

- [x] provider local `faster-whisper` isolado atrás de `ITranscriber`.
- [x] configuração inicial: modelo `base`, CPU, `int8`, beam size e VAD configuráveis.
- [x] detecção automática de idioma ou idioma fixo configurável.
- [x] consumo completo do generator do faster-whisper.
- [x] normalização de texto, timestamps e confiança por segmento.
- [x] `Transcription` persistida por áudio.
- [x] `TranscriptionSegment` persistido com sequência, início, fim, texto e confiança.
- [x] migration `0005_transcription_segments`.
- [x] estado de reunião `TRANSCRIBING` → `TRANSCRIBED`.
- [x] handler durável `TRANSCRIBE` integrado ao `JobWorker`.
- [x] heartbeat permanece ativo enquanto o provider executa transcrições longas.
- [x] retry recuperável não marca a reunião como `FAILED`; apenas falha terminal faz isso.
- [x] idempotência: resultado já persistido é reutilizado.
- [x] proteção contra path traversal ao resolver o arquivo de áudio.
- [x] API `GET /api/meetings/{meeting_id}/transcription` com segmentos.
- [x] dependências pesadas do STT isoladas em `requirements-worker.txt`.
- [x] testes com provider fake e adapter fake, sem download de modelo no CI.

## Validação de fechamento

O código da Sprint 7 inclui testes para:

- mapeamento do adapter faster-whisper;
- persistência ordenada dos segmentos;
- transição para `TRANSCRIBED`;
- execução do worker + persistência ponta a ponta com provider fake;
- falha terminal segura;
- rejeição de path fora do storage;
- retorno da transcrição/segmentos pela API.

O head atual da branch é `28311d44f29ee8174360414f7372d372879825c7`.

## Gate final da Sprint 7

1. abrir PR `agent/sprint-7-transcription` → `develop`;
2. executar CI + Quality no PR;
3. corrigir qualquer gate vermelho;
4. merge somente com os gates verdes;
5. confirmar CI/Quality pós-merge.

A validação com áudio real usando o modelo Whisper permanece um smoke test operacional local, pois baixar/carregar o modelo não deve fazer parte do CI automatizado.

## Capacidade após a Sprint 7

### Funcional

- CRUD de reuniões;
- upload/armazenamento de áudio;
- jobs duráveis e worker separado;
- retry/heartbeat/recovery;
- transcrição real local com faster-whisper;
- transcrição e segmentos persistidos;
- consulta da transcrição pela API.

### Próxima prioridade

**Sprint 8 — Interface utilizável:** criar o primeiro fluxo humano ponta a ponta para criar reunião, enviar áudio, iniciar processamento, acompanhar o job e visualizar a transcrição.

### Ainda não funcional

- interface completa de uso ponta a ponta;
- empacotamento simplificado para uso interno;
- diarização de speakers;
- identificação de participantes;
- análise por LLM, resumos e action items;
- autenticação/autorização;
- deploy público production-ready.

**Document Version:** 4.0  
**Status:** Active
