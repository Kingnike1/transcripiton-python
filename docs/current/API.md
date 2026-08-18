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

Reuniões pertencem a `User` por `Meeting.owner_id`. Recursos derivados são autorizados através da reunião-pai. Um usuário não pode listar, consultar, exportar ou alterar reunião de outro usuário; tentativas de acesso cruzado retornam 404 para não revelar a existência do recurso.

## Reuniões

- `GET /api/meetings`
- `GET /api/meetings/{meeting_id}`
- `POST /api/meetings`
- `PUT /api/meetings/{meeting_id}`
- `DELETE /api/meetings/{meeting_id}`

## Busca — Stack 15

`GET /api/search?q={texto}&skip=0&limit=20`

Pesquisa textual entre reuniões do usuário atual. O baseline consulta título, descrição e texto integral da transcrição, devolvendo reunião, campos que produziram o match e um snippet contextual.

## Exportação — Stack 16

`GET /api/meetings/{meeting_id}/export?format={formato}`

Formatos aceitos: `txt`, `md`, `json`, `docx` e `pdf`.

O arquivo é gerado sob demanda e reúne metadados, participantes, transcrição segmentada quando disponível e inteligência estruturada. A ausência de transcrição ou análise não impede a exportação. O endpoint usa `Content-Disposition: attachment` e preserva o isolamento por owner.

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

## Health

- `GET /health`
- `GET /ready`

Versão da aplicação na Stack 16: `0.12.0`.

## Ainda não implementado

- gravação por microfone.

---

**Status:** Active  
**Last Updated:** 2026-08-18
