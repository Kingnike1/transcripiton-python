# Roadmap do pipeline de IA

> **Status: Planned.** O AMIP ainda não possui provider operacional de transcrição, diarização ou análise por LLM.

## Ordem obrigatória

```text
Audio persistido
  ↓
Jobs persistentes + worker
  ↓
Transcrição real
  ↓
Diarização
  ↓
Análise por LLM
  ↓
Busca / exportação / UX avançada
```

A integração de Whisper não deve começar antes da Sprint 6B, porque o processamento pesado precisa sobreviver a restart, retry e concorrência sem depender do request HTTP.

## Sprint 6B — Jobs persistentes

Primeiro passo:

- tabela/model `ProcessingJob`;
- status persistente;
- progress/tentativas/erros;
- idempotência;
- worker separado;
- lease/heartbeat;
- retry com backoff;
- recuperação de jobs interrompidos;
- endpoint de acompanhamento.

O primeiro worker pode usar polling no banco. Redis/Celery/Dramatiq/RQ só entram quando houver necessidade comprovada.

## Transcrição

Depois dos jobs:

- modelar `TranscriptionSegment` com sequência, início, fim, texto e confiança;
- escolher **um** provider inicial;
- executar fora do processo HTTP;
- persistir texto/idioma/segmentos/timestamps;
- timeout/retry;
- testes de contrato com provider fake.

### Decisão ainda pendente

A direção histórica é Whisper, mas o modo inicial precisa ser decidido na Sprint correspondente:

- **local** — mais controle de privacidade, exige recursos/model weights/ffmpeg;
- **API externa** — operação mais simples, envolve custo, privacidade e limites do provider.

Não implementar as duas estratégias simultaneamente na primeira entrega.

## Estado de processamento sugerido

O modelo atual pode precisar evoluir para não tornar diarização obrigatória:

```text
AUDIO_UPLOADED
  ↓
TRANSCRIBING
  ↓
TRANSCRIBED
  ├── DIARIZING
  ├── SUMMARIZING
  └── COMPLETED
```

Essa alteração deve ser decidida e migrada somente quando a vertical slice de transcrição for implementada.

## Diarização

Pré-requisitos:

- transcrição estável;
- segmentos temporais;
- jobs persistentes;
- armazenamento de resultados.

A direção atual é `pyannote.audio` ou provider equivalente atrás de `ISpeakerIdentifier`. Dependências ML pesadas devem ficar isoladas do processo web/requirements de runtime básico quando possível.

## Análise por LLM

Somente depois de transcrição/diarização estáveis.

Saída desejada:

- resumo;
- action items;
- decisões;
- riscos;
- perguntas abertas;
- follow-ups.

Requisitos:

- saída estruturada/validada;
- prompts versionados;
- timeout/retry;
- limites de tokens/custo;
- rastreabilidade de provider/model;
- resultados editáveis/confirmáveis por usuário.

Saída de modelo não deve ser tratada automaticamente como fato.

## Providers

O projeto mantém interfaces para permitir adapters, mas a asynchrony/status de jobs pertence à aplicação/worker, não ao provider. A Sprint de jobs/transcrição pode simplificar contratos muito amplos antes de implementar providers reais.

## Busca

Começar com SQL/PostgreSQL Full-Text Search. Busca semântica/embeddings/pgvector só entram quando existir caso de uso validado. Elasticsearch/OpenSearch ou banco vetorial separado não são requisitos atuais.

## Exportação

Ordem futura recomendada:

1. Markdown;
2. TXT;
3. DOCX;
4. PDF.

As bibliotecas de exportação foram retiradas do runtime na P0.7 e só devem retornar quando esse módulo for efetivamente implementado.

## Fora do escopo atual

- Celery/Redis por antecipação;
- microservices de IA;
- Kubernetes/GPU orchestration;
- múltiplos providers simultâneos na primeira versão;
- RAG/vector DB sem funcionalidade comprovada.

---

**Status:** Planned  
**Last Updated:** 2026-08-16
