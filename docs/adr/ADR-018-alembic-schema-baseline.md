# ADR-018 — Alembic como fonte de evolução do schema

**Status:** Aceita  
**Data:** 2026-08-16  
**Stack:** P0.2 — Migrations

## Contexto

O projeto já declarava Alembic como padrão de governança e possuía a dependência instalada, mas ainda criava o schema por `Base.metadata.create_all()` e não tinha `alembic.ini`, ambiente de migrations ou revisions versionadas.

Isso impediria evoluções seguras para constraints de áudio, jobs persistentes e futuras alterações de produção.

## Decisão

- Alembic passa a ser a ferramenta oficial de evolução de schema.
- A revision `0001_initial_schema` representa o schema SQLAlchemy existente no momento da adoção.
- SQLite usa `render_as_batch=True` no ambiente Alembic para suportar alterações que exigem recriação de tabela.
- `compare_type=True` detecta mudanças de tipo durante autogenerate.
- A URL do banco vem de `settings.DATABASE_URL`; o valor em `alembic.ini` é somente fallback local.
- Bancos novos usam `alembic upgrade head`.
- Bancos existentes criados antes do Alembic devem ter o schema verificado e então usar `alembic stamp head`; a baseline não deve ser reaplicada sobre tabelas existentes.

## Alternativas rejeitadas

### Continuar somente com `Base.metadata.create_all()`

Rejeitada porque `create_all()` cria estruturas ausentes, mas não fornece histórico, downgrade ou alteração segura de schemas existentes.

### Migration inicial gerada e aceita sem revisão

Rejeitada. A baseline foi escrita de forma explícita e é validada contra `Base.metadata` para evitar que um autogenerate acidental consolide divergências da documentação ou do banco local.

### Recriar bancos existentes

Rejeitada porque pode causar perda de dados. A adoção por `stamp` preserva o schema legado quando ele corresponde à baseline.

## Validação

A Stack P0.2 inclui testes que verificam:

- `upgrade head` em banco SQLite vazio;
- ausência de diferenças entre o schema migrado e `Base.metadata`;
- adoção de banco preexistente por `stamp head`;
- `downgrade base` em banco descartável.

## Consequências

### Positivas

- alterações de banco passam a ser versionadas;
- P0.4 pode adicionar constraints por migration;
- Sprint 6B pode criar jobs persistentes com histórico de schema;
- deployment futuro pode aplicar migrations de modo previsível;
- drift entre models e migrations passa a ser testável.

### Cuidados

- `Base.metadata.create_all()` ainda existe na inicialização e será removido do fluxo normal na Stack P0.6;
- `stamp head` só é seguro após confirmar que o schema existente corresponde à baseline;
- migrations destrutivas exigem backup e estratégia de rollback antes de produção.
