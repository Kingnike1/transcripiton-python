# ADR-030 — Search baseline

## Status
Accepted — Stack 15

## Context
O AMIP precisa localizar reuniões por metadados e conteúdo transcrito sem introduzir infraestrutura de busca prematuramente. Produção já usa PostgreSQL, mas desenvolvimento e testes continuam em SQLite.

## Decision
A Stack 15 introduz um `SearchService` ownership-aware que pesquisa título, descrição e texto integral da transcrição. A API pública é `GET /api/search?q=...`, e a interface de reuniões expõe o mesmo recurso.

A primeira versão usa SQL portável (`ILIKE`/equivalente do SQLAlchemy) para manter paridade SQLite/PostgreSQL. O contrato fica isolado no service para permitir migrar a implementação PostgreSQL para Full Text Search (`tsvector`/GIN) quando volume e métricas justificarem.

Não será introduzido vector database nesta Stack. Busca semântica só deve existir quando houver requisito real que a busca textual não resolva.

## Consequences
- busca funciona em dev/test e produção sem serviço adicional;
- ownership da Stack 13 continua sendo aplicado antes dos resultados;
- transcrições tornam-se pesquisáveis sem duplicar conteúdo em outra base;
- para grandes volumes, `ILIKE` sobre texto integral precisará ser substituído pelo backend FTS PostgreSQL mantendo o contrato da API.
