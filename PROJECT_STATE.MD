# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-16  
**Sprint atual:** Sprint 6A — Estabilização do Núcleo  
**Stack em execução:** P0.3 — Upload seguro em streaming  
**Branch:** `agent/stack-p0-3-streaming-upload`  
**Branch base:** `agent/stack-p0-2-alembic`  
**Branch de integração:** `develop`  
**Status:** P0.3 implementada em branch empilhada; integração continua bloqueada pelo quality gate da P0.1

## Baseline e cadeia de branches

```text
main
  ↓
develop

agent/stack-p0-1-transaction-uow   → PR #2
  ↓
agent/stack-p0-2-alembic           → PR #3
  ↓
agent/stack-p0-3-streaming-upload
```

O desenvolvimento permanece empilhado para permitir avanço sem integrar código não validado em `develop` ou `main`.

## P0.1 — Transações e Unit of Work

- [x] `SqlAlchemyUnitOfWork`.
- [x] Service Layer proprietária de commit/rollback.
- [x] Repositories transaction-neutral.
- [x] Persistência de transições de estado.
- [x] `AudioService` alinhado à UoW.
- [x] Testes transacionais e ADR-017.
- [ ] GitHub Actions no head atual.
- [ ] Merge em `develop`.

## P0.2 — Migrations com Alembic

- [x] `alembic.ini` e ambiente de migrations.
- [x] `0001_initial_schema`.
- [x] SQLite batch migrations.
- [x] Testes de upgrade, drift, stamp e downgrade.
- [x] ADR-018.
- [x] Validação independente com zero diferenças entre migration e metadata.
- [ ] Quality gate oficial após desbloqueio do CI.

## P0.3 — Upload seguro em streaming

### Implementado

- [x] Remoção de `await file.read()` do endpoint.
- [x] Execução do pipeline síncrono de filesystem em threadpool.
- [x] `AudioUploadStager` com leitura em chunks de 1 MiB.
- [x] Limite aplicado durante a escrita, antes de materializar o arquivo completo.
- [x] Staging em `storage/temp`.
- [x] Preservação da extensão no arquivo temporário.
- [x] Validação de nome, MIME, tamanho e assinatura sem carregar arquivo inteiro.
- [x] Rejeição explícita de path traversal com `/` e `\\`.
- [x] Inspeção com `ffprobe`.
- [x] Validação de existência de stream de áudio.
- [x] Extração de duração, codec, canais e sample rate.
- [x] Promotion atômica com `os.replace`.
- [x] Limpeza de temporários em falha.
- [x] Compensação do arquivo final se o commit do banco falhar.
- [x] Migration `0002_audio_media_metadata`.
- [x] Persistência dos metadados técnicos.
- [x] HTTP 503 quando `ffprobe` não estiver disponível.
- [x] Testes com inspector fake e leitura em chunks.
- [x] Testes do parser de `ffprobe`.
- [x] ADR-019.
- [x] Validação independente da migration `0001 → 0002` com zero drift.

### Dependência operacional nova

O ambiente que recebe uploads deve possuir `ffprobe` (distribuído normalmente com FFmpeg). O caminho pode ser configurado por `FFPROBE_BINARY` e o timeout por `FFPROBE_TIMEOUT_SECONDS`.

## Regra atual de adoção do Alembic

Como já existe `0002`, bancos legados correspondentes ao schema original devem seguir:

```text
backup
  ↓
verificar schema equivalente a 0001
  ↓
alembic stamp 0001_initial_schema
  ↓
alembic upgrade head
```

Usar `stamp head` em um banco ainda no schema `0001` pularia migrations posteriores e não é permitido.

## Riscos e Dívidas Abertas

| Item | Prioridade | Estado |
|---|---|---|
| CI não dispara para commits feitos pela integração | Crítica para integração | Bloqueando merges |
| Regra de um áudio não possui constraint de banco | Emergencial | P0.4 |
| Upload simultâneo ainda pode disputar a regra de duplicidade | Emergencial | P0.4 |
| Limite HTTP ainda não é duplicado no reverse proxy | Alta antes de produção | Deployment/P3 |
| Handler genérico expõe detalhes internos | Alta | P0.5 |
| `file_path` ainda aparece em resposta pública | Alta | P0.5 |
| `init_db()`/`create_all()` ainda participa do startup | Alta | P0.6 |
| `datetime.utcnow()` restante | Média/Alta | P0.6 |
| `get_stale_processing(minutes)` ignora `minutes` | Alta | P0.6 |
| `main` sem proteção obrigatória | Alta | P0.7 |
| Fila de jobs em memória | Crítica antes do Whisper | Sprint 6B |

## Próxima Stack Técnica

**P0.4 — Consistência e concorrência**

Objetivo: definir formalmente a cardinalidade de áudio por reunião, garanti-la no banco via Alembic, impedir race condition de uploads simultâneos e introduzir a base de idempotência.

## Regra de Integração

Nenhuma stack dependente será mesclada em `develop` ou `main` enquanto a P0.1 não tiver quality gate reproduzível.

**Document Version:** 1.7  
**Status:** Active
