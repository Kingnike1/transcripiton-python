# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack em execução:** P0.4 — Consistência e concorrência de áudio  
**Branch:** `agent/stack-p0-4-audio-concurrency`  
**Branch base:** `agent/stack-p0-3-streaming-upload`  
**Branch de integração:** `develop`  
**Status:** P0.4 implementada em branch empilhada; integração continua bloqueada pelo quality gate da P0.1

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
agent/stack-p0-4-audio-concurrency
```

## P0.1 — Transações e Unit of Work

- [x] Unit of Work e ownership transacional no Service Layer.
- [x] Repositories transaction-neutral.
- [x] Transições de estado persistentes.
- [x] Testes e ADR-017.
- [ ] Quality gate GitHub Actions no head atual.
- [ ] Merge em `develop`.

## P0.2 — Migrations

- [x] Alembic operacional.
- [x] Baseline `0001_initial_schema`.
- [x] Testes de upgrade/drift/stamp/downgrade.
- [x] ADR-018.
- [ ] Quality gate oficial.

## P0.3 — Upload streaming

- [x] Upload em chunks de 1 MiB.
- [x] Staging temporário e promoção atômica.
- [x] Limite aplicado durante escrita.
- [x] Validação sem carregar arquivo inteiro.
- [x] `ffprobe` para duração/codec/canais/sample rate.
- [x] Migration `0002_audio_media_metadata`.
- [x] Testes e ADR-019.
- [ ] Quality gate oficial.

## P0.4 — Consistência e concorrência

### Decisão de domínio

Uma reunião possui no máximo **um áudio ativo** (`deleted_at IS NULL`). Áudios soft-deletados permanecem como histórico e não bloqueiam uma substituição futura.

### Implementado

- [x] Índice único parcial `uq_audios_active_meeting` no model.
- [x] Compatibilidade declarada para SQLite e PostgreSQL.
- [x] Migration `0003_one_active_audio_per_meeting`.
- [x] Preflight da migration para detectar duplicidades ativas existentes.
- [x] Migration falha explicitamente em vez de escolher/apagar dados conflitantes.
- [x] Pre-check rápido no `AudioService` mantido.
- [x] Banco atua como última linha de defesa contra race condition.
- [x] `IntegrityError` específico da constraint é traduzido para `AudioAlreadyExistsError`.
- [x] Outros erros de integridade não são mascarados.
- [x] Arquivo promovido é compensado quando a race é perdida antes do commit.
- [x] Teste do índice: dois ativos rejeitados; histórico soft-deletado permite substituição.
- [x] Teste da migration com duplicidade preexistente.
- [x] Testes de tradução de race no Service Layer.
- [x] ADR-020.
- [x] Validação independente: `0001 → 0002 → 0003`, zero drift e downgrade completo.

### Estratégia de idempotência

Nesta fase, repetir um upload já concluído continua retornando conflito. Não será criado `Idempotency-Key` global antes de existir identidade/tenant. A integridade da P0.4 torna retries seguros contra duplicação; idempotência de jobs será tratada na Sprint 6B e idempotência HTTP completa será revisitada após autenticação/organizações.

## Regra de adoção do Alembic

Bancos legados equivalentes à baseline original:

```text
backup
  ↓
verificar schema 0001
  ↓
alembic stamp 0001_initial_schema
  ↓
alembic upgrade head
```

A migration `0003` recusará avanço se encontrar mais de um áudio ativo para a mesma reunião.

## Riscos e dívidas abertas

| Item | Prioridade | Estado |
|---|---|---|
| CI não dispara para commits feitos pela integração | Crítica para integração | Bloqueando merges |
| Handler genérico expõe detalhes internos | Alta | P0.5 |
| `file_path` aparece em resposta pública | Alta | P0.5 |
| Falta request ID e códigos estáveis de erro | Alta | P0.5 |
| `init_db()`/`create_all()` participa do startup | Alta | P0.6 |
| `datetime.utcnow()` restante | Média/Alta | P0.6 |
| `get_stale_processing(minutes)` ignora `minutes` | Alta | P0.6 |
| `main` sem proteção obrigatória | Alta | P0.7 |
| Limite HTTP ainda não existe no reverse proxy | Alta antes de produção | Deployment/P3 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |

## Próxima Stack Técnica

**P0.5 — Tratamento seguro de erros**

Objetivo: impedir vazamento de informações internas, padronizar códigos de erro/request ID e remover caminhos internos dos contratos públicos.

## Regra de integração

Nenhuma stack empilhada será mesclada em `develop` ou `main` enquanto a P0.1 não possuir quality gate reproduzível.

**Document Version:** 1.8  
**Status:** Active
