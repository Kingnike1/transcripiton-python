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

Campos principais:

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
- `created_at`
- `updated_at`
- `deleted_at`

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

A tabela existe como preparação para diarização; ainda não há provider operacional.

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

A tabela existe como preparação para análise por IA; ainda não há pipeline persistente que a preencha.

---

## Unit of Work

Desde a Stack P0.1, repositories são transaction-neutral:

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

Repositories não devem executar `commit()` ou `rollback()`.

---

# Migrations com Alembic

A Stack P0.2 torna Alembic a fonte oficial de evolução do schema.

Estrutura:

```text
alembic.ini
migrations/
├── env.py
├── script.py.mako
└── versions/
    └── 0001_initial_schema.py
```

A revision `0001_initial_schema` representa exatamente o schema ORM existente na adoção do Alembic.

## Banco novo

Para criar um banco do zero:

```bash
alembic upgrade head
```

O Alembic cria todas as tabelas e registra a revision na tabela `alembic_version`.

## Banco criado antes do Alembic

Não executar `upgrade head` diretamente sobre um banco que já contém as tabelas da aplicação, pois a migration inicial tentaria criá-las novamente.

Procedimento seguro:

1. realizar backup do banco;
2. confirmar que o schema existente corresponde aos models atuais;
3. registrar a baseline sem executar DDL:

```bash
alembic stamp head
```

Depois do `stamp`, migrations futuras podem ser aplicadas normalmente:

```bash
alembic upgrade head
```

`stamp` não corrige schema divergente. Se houver drift, ele deve ser resolvido antes da marcação.

## Criar uma nova migration

Depois de alterar models:

```bash
alembic revision --autogenerate -m "descricao da alteracao"
```

A migration gerada **deve ser revisada manualmente** antes de commit.

Depois:

```bash
alembic upgrade head
```

## Rollback

Para reverter uma revision em ambiente controlado:

```bash
alembic downgrade -1
```

Migrations destrutivas em produção exigirão backup e plano de recuperação antes da execução.

---

## SQLite

O ambiente Alembic usa `render_as_batch=True` para URLs SQLite. Isso permite migrations futuras que precisem recriar tabelas para alterar constraints ou colunas.

SQLite continua válido para desenvolvimento e testes. PostgreSQL continua planejado para staging/produção com maior concorrência.

## Configuração

A URL efetiva vem de:

```text
settings.DATABASE_URL
```

Exemplo:

```bash
DATABASE_URL=sqlite:///./app.db alembic upgrade head
```

No futuro:

```bash
DATABASE_URL=postgresql+psycopg://... alembic upgrade head
```

---

## Testes de migration

`tests/test_migrations.py` valida:

- banco vazio → `upgrade head`;
- schema migrado sem diferenças contra `Base.metadata`;
- banco legado compatível → `stamp head`;
- banco descartável → `downgrade base`.

Esses testes impedem que models e migrations evoluam silenciosamente em direções diferentes.

---

## Itens ainda pendentes

- remover `Base.metadata.create_all()` do startup normal na Stack P0.6;
- corrigir timestamps legados em models;
- definir constraint de áudio na P0.4;
- adicionar `processing_jobs` na Sprint 6B;
- migrar para PostgreSQL antes de uso multiusuário relevante;
- definir estratégia de backup e restore para produção.

---

**Document Version:** 1.1  
**Last Updated:** 2026-08-16  
**Status:** Active
