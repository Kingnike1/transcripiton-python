# API atual do AMIP

Este documento descreve somente endpoints implementados. A especificação OpenAPI do FastAPI é a referência executável.

Base local padrão: `http://localhost:8000`.

## Autenticação — Stack 13

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/status`

Cadastro/login criam uma sessão opaca persistente. O browser recebe cookie `amip_session` com `HttpOnly`, `SameSite=Lax` e `Secure` em staging/produção. Somente o hash do token é armazenado no banco.

Enquanto nenhuma conta existe, o AMIP mantém o modo local legado sem exigir login. A primeira conta criada assume reuniões legadas sem owner. Depois que existe ao menos uma conta, endpoints protegidos exigem sessão válida.

## Ownership

Reuniões pertencem a `User` por `Meeting.owner_id`. Recursos derivados são autorizados através da reunião-pai. Um usuário não pode listar, consultar ou alterar reunião de outro usuário; tentativas de acesso cruzado retornam 404 para não revelar a existência do recurso.

## Reuniões

- `GET /api/meetings`
- `GET /api/meetings/{meeting_id}`
- `POST /api/meetings`
- `PUT /api/meetings/{meeting_id}`
- `DELETE /api/meetings/{meeting_id}`

Com autenticação ativa, listagem/pesquisa/CRUD são filtrados pelo usuário atual e novas reuniões recebem seu `owner_id`.

## Áudio

- `POST /api/meetings/{meeting_id}/audio`
- `GET /api/meetings/{meeting_id}/audio`

## Jobs persistentes

- `POST /api/meetings/{meeting_id}/jobs/transcription`
- `POST /api/meetings/{meeting_id}/jobs/diarization`
- `POST /api/meetings/{meeting_id}/jobs/analysis`
- `GET /api/jobs/{job_id}`
- `GET /api/meetings/{meeting_id}/jobs`
- `DELETE /api/jobs/{job_id}`

Jobs são autorizados pela reunião associada.

## Transcrição

`GET /api/meetings/{meeting_id}/transcription`

## Diarização

`GET /api/meetings/{meeting_id}/diarization`

## Participantes

- `GET /api/meetings/{meeting_id}/participants`
- `PATCH /api/meetings/{meeting_id}/participants/{speaker_label}`

## Inteligência por LLM

`GET /api/meetings/{meeting_id}/analysis`

A análise contém resumo, action items, decisões, riscos, perguntas abertas, follow-ups, provider/modelo e evidências rastreáveis.

## Interface web

- `GET /login`
- `GET /meetings`
- `GET /meetings/{meeting_id}`

A tela `/login` permite criar a primeira conta, registrar outra conta e fazer login. O workspace mostra apenas reuniões do usuário autenticado e oferece logout.

## Health

`GET /health`

Versão da aplicação na Stack 13: `0.9.0`.

## Ainda não implementado

- infraestrutura production-ready;
- busca;
- exportação;
- gravação por microfone.

---

**Status:** Active  
**Last Updated:** 2026-08-17
