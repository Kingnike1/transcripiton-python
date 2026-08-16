# ADR-021 — Contrato público de erros sanitizado e correlacionável

**Status:** Aceita  
**Data:** 2026-08-16  
**Stack:** P0.5 — Tratamento seguro de erros

## Contexto

Os handlers globais devolviam `exc.details` e o handler genérico devolvia `str(exc)`. Isso podia expor SQL, caminhos internos, URLs, credenciais ou mensagens de SDKs. Respostas de áudio também expunham `file_path` do storage.

## Decisão

Todo erro tratado pela aplicação usa o envelope público:

```json
{
  "status": "error",
  "code": "INTERNAL_ERROR",
  "detail": "An unexpected error occurred",
  "request_id": "<uuid>"
}
```

- detalhes internos ficam somente nos logs;
- cada request recebe um UUID gerado pelo servidor;
- o mesmo ID aparece no corpo dos erros e no header `X-Request-ID`;
- HTTP exceptions e erros de validação também são normalizados;
- mensagens de validação de upload podem ser expostas quando forem feedback seguro ao usuário;
- falhas de banco/storage/pipeline/erro genérico recebem mensagens públicas genéricas;
- `AudioResponse` não expõe `file_path`.

## Alternativas rejeitadas

### Expor `details` apenas em DEBUG

Rejeitada no contrato HTTP porque aumenta risco de configuração incorreta em ambientes públicos. Diagnóstico detalhado pertence aos logs.

### Aceitar livremente `X-Request-ID` do cliente

Não adotado nesta fase. O servidor gera um ID confiável, evitando spoofing de correlação. Propagação de tracing externo poderá ser revisitada com observabilidade distribuída.

## Consequências

- clientes ganham códigos estáveis e rastreabilidade;
- informações internas deixam de atravessar a fronteira HTTP;
- logs precisam preservar contexto interno e `request_id`;
- mudanças futuras de autenticação/rate limiting devem reutilizar o mesmo envelope.
