# Banco de dados atual

## Estratégia

- SQLAlchemy 2.x como ORM;
- SQLite em desenvolvimento/testes;
- PostgreSQL planejado para staging/produção multiusuário;
- Alembic como única fonte oficial de evolução do schema;
- Service Layer como proprietária das transações;
- semântica temporal em UTC.

## Schema atual

```text
meetings
  ├── audios
  │     └── transcriptions
  │            └── speaker_segments
  └── meeting_analysis (1:1)
```

O fato de modelos de transcrição/diarização/análise existirem não significa que os providers correspondentes estejam implementados.

## Áudio

A migration `0002_audio_media_metadata` adicionou:

- `codec_name`;
- `channels`;
- `sample_rate`.

A migration `0003_one_active_audio_per_meeting` garante:

```text
UNIQUE meeting_id
WHERE deleted_at IS NULL
```

Assim, uma reunião possui no máximo um áudio ativo, mas pode manter registros soft-deletados como histórico.

## Unit of Work

```text
Application Service
  ↓
SqlAlchemyUnitOfWork
  ├── commit no sucesso
  └── rollback na exceção
  ↓
Repositories
  └── query / add / update / flush
```

Repositories não executam `commit()` ou `rollback()`.

## Cadeia de migrations

```text
0001_initial_schema
  ↓
0002_audio_media_metadata
  ↓
0003_one_active_audio_per_meeting
```

### Banco novo

```bash
alembic upgrade head
```

### Banco legado equivalente à baseline `0001`

Depois de backup e verificação do schema:

```bash
alembic stamp 0001_initial_schema
alembic upgrade head
```

`stamp head` só deve ser usado quando o schema já corresponder exatamente ao head atual. `stamp` não corrige drift.

### Nova alteração de schema

```bash
alembic revision --autogenerate -m "descricao"
```

A revision deve ser revisada manualmente e validada antes de:

```bash
alembic upgrade head
```

## Lifecycle

O processo web não cria nem migra tabelas automaticamente.

```text
Deployment
  ↓
alembic upgrade head
  ↓
Start FastAPI
```

`reset_db()` é ferramenta explícita apenas para `development`/`test`.

## Tempo

`app.core.time.utc_now()` é o relógio comum. SQLite pode remover `tzinfo` no round-trip com as colunas `DateTime` atuais; uma eventual persistência timezone-aware mais estrita será revisitada junto da adoção do PostgreSQL.

`MeetingRepository.get_stale_processing(minutes)` usa o limiar solicitado e os estados de `ProcessingStatus`.

## Gates

`tests/test_migrations.py` valida explicitamente:

- `upgrade head` em banco vazio;
- ausência de drift contra `Base.metadata`;
- adoção de baseline legada;
- `stamp head` quando o schema já é atual;
- downgrade completo em banco descartável;
- regra de um áudio ativo.

O workflow `Quality` executa esses testes como gate próprio.

## Próxima alteração prevista

A Sprint 6B deverá adicionar o modelo/tabela de jobs persistentes por migration Alembic. PostgreSQL não será introduzido apenas por antecipação; a migração ocorrerá quando staging/produção multiusuário justificar.

---

**Status:** Active  
**Last Updated:** 2026-08-16
