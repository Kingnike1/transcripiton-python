# ADR-022 — Lifecycle, UTC e configuração de runtime

**Status:** Accepted  
**Data:** 2026-08-16

## Contexto

Após P0.1–P0.5, a aplicação ainda possuía três fragilidades de runtime:

1. `main.py` executava `init_db()` no import, que chamava `Base.metadata.create_all()` e alterava o banco fora do processo de migrations;
2. settings ainda usavam `class Config` do Pydantic V1 e permitiam `DEBUG=true`/segredo fraco em ambientes públicos;
3. timestamps eram produzidos por APIs diferentes (`datetime.utcnow()` e `datetime.now(timezone.utc)`), enquanto `get_stale_processing(minutes)` ignorava completamente o argumento `minutes`.

## Decisão

### Schema e lifecycle

- Alembic permanece a única fonte oficial de evolução do schema;
- o processo web **não executa `create_all()` nem `alembic upgrade` automaticamente**;
- deployment deve executar `alembic upgrade head` explicitamente antes da aplicação;
- FastAPI usa `lifespan` apenas para lifecycle de recursos;
- no shutdown, o SQLAlchemy engine é descartado com `engine.dispose()`;
- `reset_db()` continua disponível somente como ferramenta explícita de desenvolvimento/teste e falha fora desses ambientes.

### Configuração

- todos os módulos de settings herdam de `AMIPBaseSettings`;
- Pydantic V2 usa `SettingsConfigDict`/`ConfigDict` em vez de `class Config`;
- `ENVIRONMENT` aceita `development`, `test`, `staging` e `production`;
- staging/production rejeitam `DEBUG=true`;
- staging/production rejeitam `SECRET_KEY` curta ou conhecida como placeholder;
- desenvolvimento/testes mantêm defaults simples para não criar atrito desnecessário antes da autenticação.

### Tempo

- `app.core.time.utc_now()` é o relógio comum do backend;
- novos timestamps de aplicação são produzidos em UTC com timezone explícito;
- a P0.6 não altera o tipo SQL `DateTime` nem adiciona migration apenas para timezone, porque SQLite não preserva timezone com a mesma fidelidade esperada de PostgreSQL;
- a semântica do projeto é UTC; fidelidade de timezone no armazenamento será revisitada junto da migração para PostgreSQL, se necessária.

### Stale processing

- `get_stale_processing(minutes)` calcula `utc_now() - timedelta(minutes=minutes)`;
- limiar zero/negativo é inválido;
- estados de processamento usam `ProcessingStatus` em vez de strings duplicadas.

## Alternativas rejeitadas

### Rodar Alembic automaticamente no startup

Rejeitado. Múltiplas instâncias poderiam disputar migrations e o processo web passaria a ter permissão implícita para alterar schema.

### Manter `create_all()` no startup apenas em desenvolvimento

Rejeitado como fluxo padrão. Isso criaria dois mecanismos oficiais de schema (Alembic e metadata) e aumentaria drift.

### Migrar imediatamente todas as colunas para `DateTime(timezone=True)`

Adiado. No SQLite o ganho é limitado e criaria migrations sem resolver a fidelidade de timezone de ponta a ponta. O projeto adota UTC semanticamente agora e reavalia armazenamento timezone-aware ao migrar para PostgreSQL.

## Consequências

### Positivas

- importar a aplicação não cria banco/tabelas;
- deploy e schema ficam deterministicamente separados;
- configuração insegura falha cedo em staging/produção;
- warnings de configuração Pydantic V1 são eliminados;
- detecção de processamento obsoleto passa a respeitar o limiar solicitado;
- recursos do engine são liberados no shutdown.

### Trade-offs

- ambientes precisam executar migrations explicitamente antes do app;
- SQLite pode devolver datetimes sem `tzinfo` mesmo quando o valor foi gerado em UTC;
- `reset_db()` deixa de ser uma opção em ambientes públicos, por design.

## Critérios de revisão

Revisar esta decisão quando:

- PostgreSQL virar banco padrão de staging/produção;
- autenticação exigir rotação/gestão avançada de secrets;
- houver múltiplos processos que exijam lifecycle adicional;
- a aplicação precisar de health/readiness checks de dependências mais profundos.
