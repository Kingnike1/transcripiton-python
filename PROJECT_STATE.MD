# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack atual:** P0.5 — Tratamento seguro de erros  
**Branch:** `agent/stack-p0-5-safe-errors`  
**Branch base:** `agent/stack-p0-4-audio-concurrency`  
**Branch de integração:** `develop`  
**PR atual:** #6  
**Status:** P0.1–P0.5 implementadas em branches empilhadas; integração bloqueada por ausência de quality gate reproduzível

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
agent/stack-p0-5-safe-errors       → PR #6
```

Todos os PRs permanecem draft. Nenhum deve ser mesclado enquanto o quality gate não for executável no head atual.

---

## P0.1 — Transações e Unit of Work

- [x] `SqlAlchemyUnitOfWork`.
- [x] Service Layer proprietária de commit/rollback.
- [x] Repositories transaction-neutral.
- [x] Transições de estado persistentes.
- [x] Compensação de storage alinhada à transação.
- [x] Testes e ADR-017.
- [ ] GitHub Actions no head atual.
- [ ] Merge em `develop`.

## P0.2 — Migrations

- [x] Alembic operacional.
- [x] Baseline `0001_initial_schema`.
- [x] SQLite batch migrations.
- [x] Upgrade/downgrade e verificação de drift.
- [x] Estratégia de adoção de banco legado.
- [x] ADR-018.
- [ ] Quality gate oficial.

## P0.3 — Upload streaming

- [x] Remoção da leitura integral do upload em RAM.
- [x] Staging em chunks de 1 MiB.
- [x] Limite durante escrita.
- [x] `ffprobe` para validar e extrair metadados.
- [x] Promoção atômica e limpeza/compensação.
- [x] Migration `0002_audio_media_metadata`.
- [x] Testes e ADR-019.
- [ ] Quality gate oficial.

## P0.4 — Consistência e concorrência

- [x] Regra de no máximo um áudio ativo por reunião.
- [x] Índice único parcial `uq_audios_active_meeting`.
- [x] Migration `0003_one_active_audio_per_meeting` com preflight.
- [x] Race condition traduzida para conflito de domínio.
- [x] Outros `IntegrityError` não são mascarados.
- [x] Testes e ADR-020.
- [ ] Quality gate oficial.

## P0.5 — Tratamento seguro de erros

- [x] Envelope público `status/code/detail/request_id`.
- [x] `X-Request-ID` em respostas normais e de erro.
- [x] `str(exc)` e `exc.details` removidos de respostas 5xx.
- [x] Traceback preservado explicitamente apenas nos logs internos.
- [x] `HTTPException` e `RequestValidationError` normalizados.
- [x] `file_path` removido de `AudioResponse`.
- [x] Testes contra vazamento de SQL, paths e credenciais.
- [x] ADR-021.
- [x] `docs/03_API.md` sincronizado com endpoints realmente implementados.
- [x] Arquitetura, backlog e decisões técnicas sincronizados.
- [x] PR #6 criado.
- [ ] Quality gate oficial.

---

## Auditoria de fechamento P0.1–P0.5

### Verificado

- PRs #2, #3, #4 e #5 permanecem abertos, draft e mergeáveis no GitHub.
- PR #6 foi criado para P0.5.
- Encadeamento das branches está consistente e cada stack está à frente da anterior sem divergência conhecida.
- Cadeia Alembic validada independentemente até `0003`, incluindo zero drift contra `Base.metadata` e downgrade em banco descartável.
- P0.5 teve documentação faltante corrigida durante a auditoria.
- P0.5 teve um detalhe de observabilidade corrigido: handlers preservam o traceback recebido no logger sem depender de `sys.exc_info()` ativo.

### Bloqueio objetivo

Consultas aos heads atuais de P0.1, P0.2, P0.3, P0.4 e P0.5 retornaram **zero workflow runs** associados.

Portanto não existe evidência de GitHub Actions para afirmar:

- suíte completa verde no código empilhado atual;
- cobertura >= 80% no head atual;
- ausência de regressão entre todas as stacks combinadas.

O último CI confiável continua sendo o da `main` anterior à P0.1.

---

## Riscos e dívidas abertas

| Item | Prioridade | Estado |
|---|---|---|
| GitHub Actions não executa nos heads empilhados | Crítica | Bloqueando integração |
| `init_db()`/`create_all()` participa do import/startup | Alta | P0.6 |
| `datetime.utcnow()` restante | Média/Alta | P0.6 |
| Pydantic V1-style Config restante | Média | P0.6 |
| `get_stale_processing(minutes)` ignora `minutes` | Alta | P0.6 |
| Defaults inseguros de configuração | Alta | P0.6 |
| CI sem lint/type/security/migration gates | Alta | P0.7 |
| `main` sem proteção obrigatória | Alta | P0.7 |
| Documentação histórica ainda misturada com ativa | Média | P0.8 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |

## Próxima ação recomendada

**Não iniciar integração nem merge ainda.**

Antes de P0.6, a recomendação desta auditoria é antecipar o subconjunto bloqueador da P0.7 necessário para tornar o quality gate reproduzível. Depois de executar a suíte completa sobre o head empilhado e corrigir eventuais regressões, o projeto pode continuar para P0.6 com confiança.

Se for necessário manter desenvolvimento paralelo, P0.6 pode ser criada como branch empilhada sobre P0.5, mas continuará proibida de merge até o gate ser restaurado.

**Document Version:** 2.0  
**Status:** Active
