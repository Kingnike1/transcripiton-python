# Banco de Dados

## Estratégia atual

- **ORM:** SQLAlchemy 2.x
- **Desenvolvimento/testes:** SQLite
- **Produção futura:** PostgreSQL
- **Migrations:** Alembic
- **Soft delete:** reuniões, áudios e transcrições
- **Transações:** Service Layer via `SqlAlchemyUnitOfWork`
- **Semântica temporal:** UTC

## Schema atual

```text
meetings
  ├── audios
  │     └── transcriptions
  │            └── speaker_segments
  └── meeting_analysis (1:1)
```

### `audios`

Além dos campos de arquivo, a revision `0002_audio_media_metadata` adicionou:

- `codec_name`;
- `channels`;
- `sample_rate`.

A revision `0003_one_active_audio_per_meeting` criou o índice único parcial:

```text
uq_audios_active_meeting
WHERE deleted_at IS NULL
```

Assim, uma reunião pode manter histórico soft-deletado, mas possui no máximo um áudio ativo.

---

## Unit of Work

```text
Application Service
  ↓
SqlAlchemyUnitOfWork
  ├── commit no sucesso
  └── rollback na exceção
  ↓
Repositories
  └── query / add / flush
```

Repositories não executam `commit()` ou `rollback()`.

---

# Migrations com Alembic

Cadeia atual:

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
```

## Banco novo

```bash
alembic upgrade head
```

## Banco legado correspondente à baseline original

1. realizar backup;
2. verificar que o schema corresponde à `0001`;
3. registrar a baseline:

```bash
alembic stamp 0001_initial_schema
```

4. aplicar revisions posteriores:

```bash
alembic upgrade head
```

`stamp head` só é aceitável quando o schema já corresponde exatamente ao head atual. `stamp` nunca deve esconder drift.

## Nova migration

```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```

Toda migration autogerada precisa de revisão manual.

---

# P0.6 — Lifecycle do banco

A aplicação web não cria ou migra tabelas automaticamente.

```text
Deployment
  ↓
alembic upgrade head
  ↓
Start FastAPI
```

`main.py` não chama `init_db()` e `Base.metadata.create_all()` não faz parte do startup normal.

O FastAPI lifespan apenas administra recursos do processo e chama `engine.dispose()` no shutdown.

`reset_db()` continua como ferramenta explícita de desenvolvimento/testes e falha em staging/produção.

Testes descartáveis podem continuar usando `Base.metadata.create_all()` diretamente, pois esse uso é isolado e não representa o fluxo de deployment.

---

# Política temporal

`app.core.time.utc_now()` é o relógio comum da aplicação e substitui o uso legado de `datetime.utcnow()`.

Todos os novos timestamps são produzidos semanticamente em UTC. A P0.6 não altera as colunas para `DateTime(timezone=True)`, porque SQLite pode remover `tzinfo` no round-trip e uma migration agora não resolveria a fidelidade de timezone de ponta a ponta.

A necessidade de tipos timezone-aware no banco será revisitada na migração para PostgreSQL.

## Stale processing

`MeetingRepository.get_stale_processing(minutes)` agora usa:

```text
cutoff = utc_now() - timedelta(minutes=minutes)
```

E considera apenas os estados de processamento definidos em `ProcessingStatus`.

---

## Testes de migration

`tests/test_migrations.py` continua validando:

- banco vazio → `upgrade head`;
- zero drift contra `Base.metadata`;
- adoção de baseline legada;
- schema atual sem histórico → `stamp head`;
- downgrade completo em banco descartável;
- integridade da regra de um áudio ativo.

## Itens futuros

- `processing_jobs` na Sprint 6B;
- PostgreSQL antes de concorrência multiusuário relevante em produção;
- backup/restore de produção;
- revisão da persistência timezone-aware durante a adoção do PostgreSQL.

---

**Document Version:** 1.3  
**Last Updated:** 2026-08-16  
**Status:** Active
