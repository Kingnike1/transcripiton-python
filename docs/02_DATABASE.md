# Banco de Dados

## Estratégia atual

- **ORM:** SQLAlchemy 2.x
- **Desenvolvimento/testes:** SQLite
- **Produção futura:** PostgreSQL
- **Migrations:** Alembic
- **Soft delete:** aplicado em reuniões, áudios e transcrições
- **Ownership transacional:** Service Layer via `SqlAlchemyUnitOfWork`

## Schema atual

```text
meetings
  ├── audios
  │     └── transcriptions
  │            └── speaker_segments
  └── meeting_analysis (1:1)
```

### `meetings`

- `id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`
- `deleted_at`

### `audios`

- `id`
- `meeting_id` → `meetings.id`
- `filename`
- `file_path`
- `duration`
- `file_size`
- `mime_type`
- `codec_name`
- `channels`
- `sample_rate`
- `created_at`
- `updated_at`
- `deleted_at`

`codec_name`, `channels` e `sample_rate` foram adicionados pela revision `0002_audio_media_metadata` e são extraídos com `ffprobe` durante o upload.

A regra de um áudio por reunião ainda está somente no Service Layer. A constraint de banco será decidida na Stack P0.4.

### `transcriptions`

- `id`
- `audio_id` → `audios.id`
- `text`
- `language`
- `created_at`
- `updated_at`
- `deleted_at`

O modelo existe, mas o fluxo de transcrição real ainda não foi implementado.

### `speaker_segments`

- `id`
- `transcription_id` → `transcriptions.id`
- `speaker_label`
- `start_time`
- `end_time`
- `text`
- `confidence`
- `created_at`

### `meeting_analysis`

- `id`
- `meeting_id` → `meetings.id` com unicidade
- `summary`
- `action_items`
- `decisions`
- `risks`
- `open_questions`
- `follow_up_tasks`
- `created_at`
- `updated_at`

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

Estrutura atual:

```text
alembic.ini
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 0001_initial_schema.py
    └── 0002_audio_media_metadata.py
```

## Banco novo

```bash
alembic upgrade head
```

O Alembic aplica toda a cadeia até a revision atual.

## Banco criado antes da adoção do Alembic

O banco legado original corresponde à revision `0001_initial_schema`. Como já existem revisions posteriores, **não usar `stamp head` nesse banco**.

Procedimento:

1. realizar backup;
2. confirmar que o schema legado corresponde à baseline `0001`;
3. registrar somente a baseline:

```bash
alembic stamp 0001_initial_schema
```

4. aplicar as alterações posteriores:

```bash
alembic upgrade head
```

Assim a `0002_audio_media_metadata` e futuras revisions são realmente executadas.

### Banco sem histórico mas já com schema totalmente atual

Somente quando o schema já corresponder exatamente ao `head` atual é aceitável:

```bash
alembic stamp head
```

`stamp` nunca deve ser usado para esconder drift.

## Nova migration

```bash
alembic revision --autogenerate -m "descricao da alteracao"
```

Toda migration autogerada deve ser revisada manualmente antes do commit.

Depois:

```bash
alembic upgrade head
```

## Rollback

```bash
alembic downgrade -1
```

Migrations destrutivas em produção exigem backup e plano de recuperação.

---

## SQLite

O ambiente Alembic usa `render_as_batch=True`, permitindo alterações futuras de colunas e constraints em SQLite.

SQLite continua válido para desenvolvimento e testes. PostgreSQL permanece planejado para staging/produção com maior concorrência.

## Configuração

A URL efetiva vem de `settings.DATABASE_URL`.

```bash
DATABASE_URL=sqlite:///./app.db alembic upgrade head
```

---

## Testes de migration

`tests/test_migrations.py` valida:

- banco vazio → `upgrade head`;
- schema migrado sem diferenças contra `Base.metadata`;
- schema legado `0001` sem histórico → `stamp 0001_initial_schema` + `upgrade head`;
- schema já totalmente atual sem histórico → `stamp head`;
- cadeia completa → `downgrade base` em banco descartável.

---

## Itens ainda pendentes

- remover `Base.metadata.create_all()` do startup normal na P0.6;
- corrigir timestamps legados em models;
- definir constraint de áudio na P0.4;
- adicionar `processing_jobs` na Sprint 6B;
- migrar para PostgreSQL antes de uso multiusuário relevante;
- definir backup e restore de produção.

---

**Document Version:** 1.2  
**Last Updated:** 2026-08-16  
**Status:** Active
