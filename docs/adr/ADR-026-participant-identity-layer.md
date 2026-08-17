# ADR-026 — Identidade de participantes separada da diarização

**Status:** Accepted  
**Date:** 2026-08-17

## Contexto

A diarização identifica vozes com rótulos técnicos como `SPEAKER_00`, mas esses rótulos não são nomes de pessoas e não devem ser gravados como identidade humana definitiva. A Stack 12 também precisa de uma forma estável de consultar quem é cada participante sem duplicar nomes em todos os segmentos.

## Decisão

Criar `Participant` como entidade pertencente à reunião, com:

- `meeting_id`;
- `speaker_label`;
- `display_name` opcional;
- `confirmed` explícito;
- timestamps.

A combinação `(meeting_id, speaker_label)` é única. `SpeakerSegment` continua sendo o resultado temporal da diarização e não recebe nome humano persistido. A API de diarização apenas enriquece a resposta com a identidade atual do participante.

Novas diarizações criam placeholders de participantes automaticamente. A migration `0007_participant_identities` faz backfill dos rótulos já persistidos. A confirmação manual exige nome não vazio.

## Consequências

### Positivas

- evita repetir nome em cada segmento;
- mantém dado bruto de diarização separado de edição humana;
- permite correção de identidade sem reprocessar áudio;
- prepara a Stack 12 para atribuir falas, decisões e action items a pessoas confirmadas;
- preserva rastreabilidade entre rótulo técnico e identidade humana.

### Limitações

O rótulo produzido pelo provider é local à diarização daquela reunião; ele não representa identidade biométrica global. A Stack 11 não implementa reconhecimento de voz entre reuniões.
