# ADR-027 — LLM local com saída estruturada e rastreável

**Status:** Accepted  
**Data:** 2026-08-17

## Contexto

A Stack 12 precisa transformar transcrição diarizada e participantes confirmados em resumo, action items, decisões, riscos e follow-ups sem tornar uma API paga obrigatória nem acoplar o domínio a um fornecedor.

## Decisão

- usar Ollama como provider local inicial;
- usar `qwen3:4b` como baseline configurável;
- chamar `/api/chat` com `stream=false` e JSON Schema em `format`;
- validar toda resposta com Pydantic antes de persistir;
- executar análise em job durável `SUMMARIZE`, nunca no request HTTP;
- alimentar o modelo com timestamps, speaker labels e nomes confirmados;
- exigir evidências por item sempre que disponíveis;
- persistir provider/modelo usados para rastreabilidade;
- manter o contrato de provider desacoplado para adapters futuros.

## Consequências

O AMIP funciona sem cobrança por token quando Ollama roda localmente. Se Ollama estiver indisponível, somente jobs de análise falham/retry; transcrição, diarização e participantes continuam independentes. Modelos maiores ou providers pagos podem ser adicionados posteriormente sem alterar o contrato público da análise.

## Limites

A Stack 12 não implementa reconhecimento biométrico, RAG, vector database nem provider pago. A qualidade depende do modelo local e da qualidade da transcrição/diarização de entrada.
