# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-17  
**Stack atual:** Stack 12 — Inteligência por LLM  
**Branch de integração:** `develop`  
**Último merge:** PR #15 — Stack 11 Identificação de participantes  
**Commit de integração:** `4be1554995c6ba02223d2c4ea44c71797795b5ec`  
**Status:** Stacks 7–11 concluídas e integradas; Stack 12 é a próxima prioridade

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- transcrição e segmentos persistidos;
- diarização local com `pyannote.audio` quando configurado;
- speaker segments persistidos e reconciliados com texto;
- identificação de participantes por reunião;
- edição e confirmação manual de `SPEAKER_XX` → nome humano;
- API enriquecida com identidade do participante;
- UI para transcrição, diarização e confirmação de participantes;
- Docker/Compose com migrations, web e worker;
- healthcheck, smoke test e documentação operacional.

## Stack 11 — Identificação de participantes — CONCLUÍDA

- [x] entidade `Participant` por reunião;
- [x] constraint única `(meeting_id, speaker_label)`;
- [x] migration `0007_participant_identities`;
- [x] backfill de rótulos já diarizados;
- [x] criação automática de placeholders em novas diarizações;
- [x] API para listar participantes;
- [x] API para editar/confirmar identidade;
- [x] confirmação exige nome não vazio;
- [x] diarização retorna nome/estado de confirmação por segmento;
- [x] UI para iniciar diarização e editar participantes;
- [x] testes específicos da Stack 11;
- [x] ADR-026 e documentação current sincronizados;
- [x] CI + Quality + Docker verdes no PR #15;
- [x] PR #15 integrado em `develop`.

## Próximas stacks

1. Stack 12 — inteligência por LLM;
2. Stack 13 — autenticação/autorização;
3. Stack 14 — infraestrutura de produção;
4. Stack 15 — busca;
5. Stack 16 — exportação;
6. Stack 17 — gravação por microfone.

## Pendências operacionais independentes

- smoke test com áudio real/modelos baixados na máquina de uso;
- branch protection administrativa da `main` quando permissões permitirem.

## Próxima Stack

**Stack 12 — Inteligência por LLM** deve consumir transcrição, speaker segments e participantes confirmados para produzir resumo estruturado, action items, decisões, riscos e follow-ups com rastreabilidade.

**Document Version:** 7.1  
**Status:** Active
