# ADR-028 — Authentication and resource ownership

**Status:** Accepted  
**Date:** 2026-08-17

## Context

O AMIP deixou de ser somente um workspace local e precisa separar dados entre usuários sem introduzir infraestrutura desnecessária antes da Stack 14.

## Decision

- `User` representa a conta local do AMIP;
- senhas usam `hashlib.scrypt` com salt aleatório e comparação constante;
- sessões são tokens opacos aleatórios; somente o SHA-256 do token é persistido;
- sessões são revogáveis e expiram em sete dias;
- o browser recebe cookie `HttpOnly`, `SameSite=Lax` e `Secure` em staging/produção;
- `Meeting.owner_id` define ownership; recursos derivados são autorizados pela reunião-pai;
- tentativa de acessar recurso de outro usuário retorna 404 para reduzir enumeração de IDs;
- antes de existir qualquer conta, o modo local legado continua disponível;
- a primeira conta criada assume reuniões legadas cujo `owner_id` esteja nulo;
- toda reunião criada após autenticação ativa recebe explicitamente o usuário atual como owner;
- workers continuam operando por IDs internos e não dependem de sessão HTTP.

## Consequences

A aplicação ganha isolamento multiusuário sem JWT, Redis ou serviço externo de identidade. Sessões podem ser revogadas imediatamente. `owner_id` permanece nullable no schema apenas para migração/compatibilidade de dados legados; o fluxo autenticado não cria reuniões sem dono.

## Deferred

SSO/OAuth, convite obrigatório, RBAC granular, MFA e provedores externos de identidade ficam adiados até existir requisito real. A Stack 14 tratará hardening e infraestrutura pública.
