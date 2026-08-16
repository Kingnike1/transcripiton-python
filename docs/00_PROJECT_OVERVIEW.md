# Visão geral do AMIP

## O que é

O **AI Meeting Intelligence Platform (AMIP)** é uma aplicação web em Python/FastAPI para organizar reuniões e processar seus áudios. A visão de longo prazo é produzir transcrição, identificação de speakers e inteligência estruturada; a documentação atual distingue claramente visão de produto de funcionalidades já entregues.

## Estado atual

### Disponível

- CRUD de reuniões pela API;
- upload e metadados de áudio;
- streaming/staging de upload;
- inspeção com `ffprobe`;
- storage local;
- transações com Unit of Work;
- migrations Alembic;
- integridade de um áudio ativo por reunião;
- error boundary + request ID;
- lifecycle/configuração seguros;
- CI/Quality completo em Python 3.11/3.12.

### Não disponível ainda

- jobs persistentes/worker;
- transcrição real;
- diarização;
- análise por LLM;
- UI completa;
- autenticação/autorização;
- busca/exportação;
- deployment público de produção.

## Arquitetura

O projeto é um monólito modular:

```text
FastAPI → Services → Unit of Work → Repositories → SQLAlchemy
                  ↘ Storage / ffprobe / providers futuros
```

SQLite permanece em desenvolvimento/testes. PostgreSQL é evolução planejada quando staging/produção multiusuário justificar.

## Qualidade

Gates atuais:

- pytest + cobertura >=80%;
- Python 3.11 e 3.12;
- Ruff;
- mypy;
- migration integrity;
- Bandit;
- `pip-audit` do runtime.

## Fluxo de desenvolvimento

```text
main → release estável
develop → integração
agent/stack-* → Stack em desenvolvimento
```

Toda Stack passa por análise, branch própria, testes, documentação, PR, CI/Quality, merge em `develop` e pós-merge verde.

## Roadmap imediato

```text
P0.8 documentação
  ↓
Sprint 6B jobs persistentes
  ↓
primeira transcrição real
  ↓
vertical slice de UI
  ↓
diarização / LLM / busca / exportação
```

Whisper ou outro provider de transcrição não deve ser integrado antes do sistema de jobs persistentes.

## Mapa da documentação

Use [`README.md`](README.md) desta pasta para navegar pelas categorias:

- `current/` — implementação real;
- `roadmap/` — futuro;
- `archive/` — histórico;
- `adr/` — decisões;
- `06_BACKLOG.md` — planejamento operacional.

## Fontes da verdade

Em caso de divergência:

1. código, migrations, testes e CI;
2. governança/estado/decisões;
3. `docs/current/`;
4. backlog/roadmap;
5. archive apenas como histórico.

---

**Document Version:** 2.0  
**Last Updated:** 2026-08-16  
**Status:** Active
