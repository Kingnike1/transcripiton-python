# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack em execução:** P0.5 — Tratamento seguro de erros  
**Branch:** `agent/stack-p0-5-safe-errors`  
**Branch base:** `agent/stack-p0-4-audio-concurrency`  
**Branch de integração:** `develop`  
**Status:** P0.5 implementada em branch empilhada; integração continua bloqueada pelo quality gate da P0.1

## Cadeia atual

```text
main
  ↓
develop

agent/stack-p0-1-transaction-uow   → PR #2
  ↓
agent/stack-p0-2-alembic           → PR #3
  ↓
agent/stack-p0-3-streaming-upload  → PR #4
  ↓
agent/stack-p0-4-audio-concurrency → PR #5
  ↓
agent/stack-p0-5-safe-errors
```

## P0.1 — Transações e Unit of Work

- [x] Unit of Work, repositories transaction-neutral e transições persistentes.
- [x] Testes e ADR-017.
- [ ] Quality gate oficial e merge em `develop`.

## P0.2 — Migrations

- [x] Alembic, baseline e testes de drift/upgrade/downgrade.
- [x] ADR-018.
- [ ] Quality gate oficial.

## P0.3 — Upload streaming

- [x] Upload em chunks, staging, ffprobe, metadados e migration `0002`.
- [x] Testes e ADR-019.
- [ ] Quality gate oficial.

## P0.4 — Consistência e concorrência

- [x] Um áudio ativo por reunião.
- [x] Índice único parcial e migration `0003`.
- [x] Race traduzida para conflito de domínio e storage compensado.
- [x] Testes, estratégia de idempotência e ADR-020.
- [ ] Quality gate oficial.

## P0.5 — Tratamento seguro de erros

### Contrato público

Erros passam a usar:

```json
{
  "status": "error",
  "code": "INTERNAL_ERROR",
  "detail": "An unexpected error occurred",
  "request_id": "<uuid>"
}
```

### Implementado

- [x] Remover `exc.details` das respostas públicas.
- [x] Remover `str(exc)` do 500 genérico.
- [x] Manter detalhes internos exclusivamente nos logs.
- [x] Gerar `request_id` confiável no servidor para cada request.
- [x] Adicionar `X-Request-ID` nas respostas normais.
- [x] Adicionar `X-Request-ID` diretamente nos envelopes de erro para cobrir 500 genérico.
- [x] Normalizar `HTTPException` com códigos estáveis (`NOT_FOUND`, `CONFLICT`, etc.).
- [x] Normalizar `RequestValidationError` sem ecoar payload/estrutura do Pydantic.
- [x] Separar mensagens públicas de falhas de banco, storage, pipeline e erro interno.
- [x] Manter feedback de validação de upload quando seguro.
- [x] Remover `file_path` de `AudioResponse`.
- [x] Adicionar testes de request ID, 404, 422, 500 genérico e erro de banco.
- [x] Adicionar teste de ausência de `file_path` na API de áudio.
- [x] Registrar ADR-021.

## Riscos e dívidas abertas

| Item | Prioridade | Estado |
|---|---|---|
| CI não dispara para commits feitos pela integração | Crítica para integração | Bloqueando merges |
| `init_db()`/`create_all()` participa do startup | Alta | P0.6 |
| `datetime.utcnow()` restante | Média/Alta | P0.6 |
| Pydantic V1-style Config restante | Média | P0.6 |
| `get_stale_processing(minutes)` ignora `minutes` | Alta | P0.6 |
| Defaults inseguros de configuração | Alta antes de produção | P0.6 |
| `main` sem proteção obrigatória | Alta | P0.7 |
| CI sem lint/type/security/migration gates | Alta | P0.7 |
| Documentação histórica ainda misturada com ativa | Média | P0.8 |
| Limite HTTP não existe no reverse proxy | Alta antes de produção | Deployment/P3 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |

## Próxima Stack Técnica

**P0.6 — Lifecycle e configuração**

Objetivo: retirar side effects do import/startup, consolidar timezone/Pydantic V2, corrigir `get_stale_processing(minutes)` e tornar configurações inseguras impossíveis fora de desenvolvimento.

## Regra de integração

Nenhuma stack empilhada será mesclada em `develop` ou `main` enquanto a P0.1 não possuir quality gate reproduzível.

**Document Version:** 1.9  
**Status:** Active
