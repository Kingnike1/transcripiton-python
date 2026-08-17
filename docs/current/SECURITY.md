# Segurança atual

## Autenticação

A Stack 13 introduz contas locais, sessões persistentes e ownership de reuniões.

- senha: `hashlib.scrypt` + salt aleatório;
- comparação de hash: `hmac.compare_digest`;
- sessão: token opaco gerado com `secrets.token_urlsafe`;
- persistência: somente SHA-256 do token;
- expiração: 7 dias;
- logout: remove a sessão do banco;
- cookie: `HttpOnly`, `SameSite=Lax` e `Secure` em staging/produção.

## Autorização

`Meeting.owner_id` é a raiz de ownership. Áudio, transcrição, diarização, participantes, análise e jobs são autorizados pela reunião-pai. Acesso a recurso de outro usuário retorna 404.

## Compatibilidade local

Enquanto não existe nenhuma conta, o modo local legado continua disponível. A primeira conta criada assume reuniões antigas sem owner. Depois que autenticação é ativada pela existência de uma conta, APIs protegidas e workspace exigem sessão válida.

## Limites atuais

Ainda não existem MFA, SSO/OAuth, RBAC granular, rate limiting distribuído ou política de convites. Hardening operacional/publicação pertence à Stack 14.

---

**Status:** Active  
**Last Updated:** 2026-08-17
