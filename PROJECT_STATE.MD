# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack atual:** P0.6 — Lifecycle e configuração  
**Branch:** `agent/stack-p0-6-lifecycle-config`  
**Branch base / integração:** `develop`  
**Head verde de `develop` antes da P0.6:** `5eb893c4014d089902eb507c3055253c65cc4e65`  
**Status:** P0.1–P0.5 integradas em `develop`; P0.6 em execução

## Baseline validada

As stacks P0.1–P0.5 foram integradas sequencialmente em `develop` pelos PRs #2–#6.

O GitHub Actions executou diretamente no head integrado de `develop` (run #80) com:

- 114 testes aprovados;
- 0 falhas;
- cobertura total de 87,04%;
- gate mínimo de 80% aprovado.

O workflow também foi ampliado para `develop`, PRs direcionados a `develop`, `workflow_dispatch`, permissões mínimas e cancelamento de runs redundantes.

`main` permanece fora desta integração até uma futura etapa de release.

---

## P0.1 — Transações e Unit of Work

**Status:** Integrada em `develop`.

- [x] `SqlAlchemyUnitOfWork`.
- [x] Service Layer proprietária de commit/rollback.
- [x] Repositories transaction-neutral.
- [x] Transições de estado persistentes.
- [x] Compensação de storage alinhada à transação.
- [x] Testes e ADR-017.
- [x] Quality gate.
- [x] Merge em `develop`.

## P0.2 — Migrations

**Status:** Integrada em `develop`.

- [x] Alembic operacional.
- [x] Baseline `0001_initial_schema`.
- [x] SQLite batch migrations.
- [x] Upgrade/downgrade e verificação de drift.
- [x] Estratégia de adoção de banco legado.
- [x] ADR-018.
- [x] Quality gate e merge.

## P0.3 — Upload streaming

**Status:** Integrada em `develop`.

- [x] Upload em chunks de 1 MiB.
- [x] Staging temporário e promoção atômica.
- [x] Limite durante escrita.
- [x] `ffprobe` para validação e metadados.
- [x] Migration `0002_audio_media_metadata`.
- [x] Testes e ADR-019.
- [x] Quality gate e merge.

## P0.4 — Consistência e concorrência

**Status:** Integrada em `develop`.

- [x] No máximo um áudio ativo por reunião.
- [x] Índice único parcial `uq_audios_active_meeting`.
- [x] Migration `0003_one_active_audio_per_meeting` com preflight.
- [x] Race condition convertida para conflito de domínio.
- [x] Testes e ADR-020.
- [x] Quality gate e merge.

## P0.5 — Tratamento seguro de erros

**Status:** Integrada em `develop`.

- [x] Envelope público `status/code/detail/request_id`.
- [x] `X-Request-ID` em respostas normais e de erro.
- [x] Detalhes internos removidos de respostas 5xx.
- [x] Traceback preservado somente nos logs.
- [x] `HTTPException` e `RequestValidationError` normalizados.
- [x] `file_path` removido de `AudioResponse`.
- [x] API/documentação sincronizadas.
- [x] ADR-021.
- [x] Quality gate e merge.

---

## P0.6 — Lifecycle e configuração

### Objetivo

Eliminar efeitos colaterais de startup/import, padronizar configuração Pydantic V2 e semântica UTC, corrigir a detecção de processamento obsoleto e impedir configuração insegura em staging/produção.

### Escopo planejado

- [ ] Remover `init_db()`/`Base.metadata.create_all()` do startup normal.
- [ ] Usar lifespan do FastAPI apenas para lifecycle de recursos; migrations continuam externas via Alembic.
- [ ] Corrigir assinatura depreciada de `TemplateResponse`.
- [ ] Substituir `datetime.utcnow()` restante por helper UTC comum.
- [ ] Corrigir `get_stale_processing(minutes)` e usar os estados do enum.
- [ ] Migrar settings e schemas restantes para Pydantic V2/`ConfigDict`.
- [ ] Adicionar `ENVIRONMENT` e validação de `DEBUG`/`SECRET_KEY` para staging/produção.
- [ ] Atualizar `.env.example`.
- [ ] Adicionar testes de lifecycle, settings, stale processing e regressão.
- [ ] Registrar decisão em ADR e atualizar arquitetura/backlog/decisões.
- [ ] Passar no CI e integrar em `develop`.

### Decisão de lifecycle

A aplicação web **não executará migrations automaticamente ao iniciar**. O schema é responsabilidade do processo de deployment por `alembic upgrade head`. O lifespan será usado apenas para lifecycle de recursos, como startup/shutdown e descarte do engine.

---

## Dívidas abertas após P0.6

| Item | Prioridade | Stack |
|---|---|---|
| CI ainda sem lint/type/security/migration gates explícitos | Alta | P0.7 |
| `main` sem proteção obrigatória | Alta | P0.7 |
| Governança ainda cita Python 3.12+ e formato antigo de commits | Média/Alta | P0.7 |
| Documentação histórica misturada com ativa | Média | P0.8 |
| `PROJECT_CONTEXT.md` possui status de features antigos | Média | P0.8 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |
| `processing_service.py` sem cobertura | Crítica antes de jobs | Sprint 6B |

## Próxima stack após P0.6

**P0.7 — Qualidade e governança**, seguida por P0.8 documental e então Sprint 6B — Jobs persistentes.

**Document Version:** 2.1  
**Status:** Active
