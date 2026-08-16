# Technical Decisions Register

Este arquivo mantém o registro ativo das principais decisões técnicas do AMIP. Decisões arquiteturais com maior impacto também possuem ADR dedicado em `docs/adr/`. O histórico detalhado das versões anteriores permanece preservado no Git.

---

## TD-001 — Arquitetura Monolítica Modular

**Status:** Accepted  
**Data:** 2026-08-03

O AMIP permanece como monólito modular com separação entre apresentação, API, services, persistência e providers. Microservices só devem ser avaliados mediante necessidade real de escala, isolamento ou equipes independentes.

---

## TD-002 — FastAPI como framework principal

**Status:** Accepted  
**Data:** 2026-08-03

FastAPI é o framework HTTP principal, com Pydantic para contratos e Uvicorn/ASGI para execução.

---

## TD-003 — SQLite como banco padrão de desenvolvimento

**Status:** Accepted  
**Data:** 2026-08-03

SQLite continua sendo a opção local e de testes. PostgreSQL permanece a evolução planejada para staging/produção multiusuário e concorrência maior.

---

## TD-004 — Jinja2 + HTMX em vez de SPA

**Status:** Accepted  
**Data:** 2026-08-03

A interface prioriza server-side rendering com Jinja2, HTMX e JavaScript mínimo. React/Vue só serão considerados se a complexidade real da UI justificar.

---

## TD-005 — Bootstrap 5 como framework CSS

**Status:** Accepted  
**Data:** 2026-08-03

Bootstrap 5 é o framework visual padrão para acelerar a entrega e manter responsividade e consistência.

---

## TD-006 — Whisper como direção inicial de transcrição

**Status:** Accepted, sujeito a revisão na Sprint de provider  
**Data:** 2026-08-03

Whisper permanece a referência inicial para speech-to-text. A implementação concreta só será escolhida após jobs persistentes e deverá ficar atrás de `ITranscriber`.

---

## TD-007 — pyannote.audio como direção inicial de diarização

**Status:** Accepted, futuro  
**Data:** 2026-08-03

pyannote.audio continua sendo a referência planejada para diarização, atrás de `ISpeakerIdentifier` e executada fora do request HTTP.

---

## TD-008 — Repository Pattern

**Status:** Accepted  
**Data:** 2026-08-03

Queries e operações de persistência ficam encapsuladas em repositories. A partir da TD-016, repositories são explicitamente transaction-neutral e não podem executar `commit()` ou `rollback()`.

---

## TD-009 — Service Layer

**Status:** Accepted  
**Data:** 2026-08-03

Regras de negócio e coordenação de casos de uso ficam em services. Routes HTTP devem permanecer finas e sem SQL.

---

## TD-010 — Interfaces para providers de IA

**Status:** Accepted  
**Data:** 2026-08-03

Transcrição, diarização, análise e exportação devem ser acessadas por contratos estáveis para permitir troca de providers sem alterar o núcleo do domínio.

---

## TD-011 — BackgroundTasks/fila em memória para protótipo

**Status:** Deprecated — será superseded pela Sprint 6B  
**Data original:** 2026-08-03  
**Revisão:** 2026-08-06

A fila em memória continua existindo apenas como protótipo. Ela não é aprovada para Whisper ou processamento pesado. A Sprint 6B deverá substituí-la por jobs persistentes e worker recuperável.

---

## TD-012 — Storage local no MVP

**Status:** Accepted  
**Data:** 2026-08-03

Filesystem local continua válido para desenvolvimento e servidor único. Storage compatível com S3 será introduzido apenas quando múltiplas instâncias ou requisitos operacionais justificarem.

---

## TD-013 — Arquitetura preparada para múltiplos providers

**Status:** Accepted  
**Data:** 2026-08-03

O desenho suporta múltiplos adapters, mas cada funcionalidade deve começar com apenas um provider concreto estável antes de adicionar fallback ou seleção dinâmica.

---

## TD-014 — KISS e YAGNI

**Status:** Accepted  
**Data:** 2026-08-03

O projeto prioriza a solução mais simples que satisfaça os requisitos atuais. Redis, Celery, microservices, Kubernetes e stacks semelhantes exigem justificativa baseada em necessidade real.

---

## TD-015 — Desenvolvimento incremental

**Status:** Accepted  
**Data:** 2026-08-03

O projeto evolui por stacks e Sprints pequenas, com testes, documentação e quality gate antes de avançar para dependências posteriores.

---

## TD-016 — Service Layer é proprietária das transações

**Status:** Accepted  
**Data:** 2026-08-06  
**ADR:** `docs/adr/ADR-017-service-layer-transaction-ownership.md`

A camada de serviço possui as fronteiras transacionais. Repositories usam query/add/flush e não executam commit ou rollback. `SqlAlchemyUnitOfWork` coordena a Session compartilhada pelo caso de uso.

---

## TD-017 — Alembic é a fonte oficial de evolução do schema

**Status:** Accepted  
**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-018-alembic-schema-baseline.md`

Alembic é a fonte oficial para evolução do schema. Bancos novos usam `upgrade head`; bancos legados devem ser marcados na revision que realmente representam e depois avançados pelas revisions posteriores. Migrations autogeradas exigem revisão manual.

---

## TD-018 — Upload de áudio usa staging em chunks e ffprobe

**Status:** Accepted  
**Data:** 2026-08-16  
**ADR:** `docs/adr/ADR-019-streaming-audio-staging.md`

### Contexto

O endpoint materializava o arquivo inteiro com `await file.read()`, fazendo o consumo de memória crescer proporcionalmente ao tamanho do upload. A validação também não confirmava a presença de um stream de áudio real.

### Decisão

- `UploadFile.file` é processado fora do event loop via threadpool;
- o arquivo é escrito em `storage/temp` em chunks de 1 MiB;
- o limite é contabilizado durante a escrita;
- assinatura e metadados são validados antes da promoção;
- `ffprobe` confirma o stream de áudio e extrai duração, codec, canais e sample rate;
- o arquivo validado é promovido atomicamente com `os.replace`;
- falhas antes do commit limpam temporário ou arquivo final por compensação;
- ausência de `ffprobe` é falha operacional do servidor, não entrada inválida do usuário.

### Consequências

O upload deixa de manter o arquivo completo em RAM e cria uma base adequada para o futuro worker de transcrição. `ffprobe` passa a ser dependência operacional e o limite também deverá ser aplicado no reverse proxy antes de produção.

---

**Document Version:** 1.3  
**Last Updated:** 2026-08-16  
**Status:** Active
