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

## Busca — Stack 15

`GET /api/search?q={texto}&skip=0&limit=20`

Pesquisa textual entre reuniões do usuário atual. O baseline consulta título, descrição e texto integral da transcrição, devolvendo reunião, campos que produziram o match e um snippet contextual. A query aceita 2–200 caracteres. O contrato é ownership-aware e não retorna reuniões de outro usuário.

A implementação inicial é SQL portável para SQLite/PostgreSQL. PostgreSQL FTS fica como evolução de performance quando métricas justificarem; vector database não faz parte desta Stack.

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

## Transcrição

`GET /api/meetings/{meeting_id}/transcription`

## Diarização

`GET /api/meetings/{meeting_id}/diarization`

## Participantes

- `GET /api/meetings/{meeting_id}/participants`
- `PATCH /api/meetings/{meeting_id}/participants/{speaker_label}`

## Inteligência por LLM

`GET /api/meetings/{meeting_id}/analysis`

## Interface web

- `GET /login`
- `GET /meetings`
- `GET /meetings?q={texto}`
- `GET /meetings/{meeting_id}`

A listagem possui busca por reuniões e transcrições, preservando o isolamento por usuário.

## Health

- `GET /health`
- `GET /ready`

Versão da aplicação na Stack 15: `0.11.0`.

## Ainda não implementado

- exportação;
- gravação por microfone.

---

**Status:** Active  
**Last Updated:** 2026-08-17
