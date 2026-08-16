# Roadmap do pipeline de IA

> **Status: Planned para IA.** Jobs persistentes/worker já foram implementados na Sprint 6B; ainda não existe provider operacional de transcrição, diarização ou LLM.

## Ordem

```text
Áudio persistido
  ↓
Jobs persistentes + worker ✅
  ↓
Transcrição real ← próxima
  ↓
Diarização
  ↓
Análise por LLM
  ↓
Busca / exportação / UX avançada
```

## Base assíncrona concluída

A Sprint 6B entregou `ProcessingJob`, fila no banco, worker separado, idempotência, lease/heartbeat, retry e recuperação de trabalho stale. Redis/Celery/RQ/Dramatiq continuam adiados.

## Sprint 7 — Transcrição

Próxima vertical:

- modelar `TranscriptionSegment` com sequência, início, fim, texto e confiança;
- escolher **um** provider inicial;
- manter dependência ML fora do runtime web básico quando possível;
- registrar handler `TRANSCRIBE` no worker;
- persistir texto/idioma/segmentos/timestamps;
- adaptar estados para possuir `TRANSCRIBED` sem tornar diarização obrigatória;
- usar retry do job para falhas recuperáveis;
- marcar reunião como falha somente quando o job esgotar tentativas;
- testes de contrato com provider fake; IA real não roda no CI.

### Escolha de provider

Para uso interno/pessoal será avaliado um provider Whisper local como primeira opção, comparado a API externa em custo operacional, privacidade, recursos de máquina e simplicidade. Apenas um será implementado na primeira entrega.

## Diarização

Só entra depois de transcrição/segmentos estáveis. Provider deve ficar atrás de `ISpeakerIdentifier`; dependências pesadas não pertencem ao processo web quando puderem ser isoladas no worker.

## LLM

Depois do texto confiável. Saídas desejadas: resumo, action items, decisões, riscos, perguntas e follow-ups. Saída deve ser estruturada/validada, rastreável e confirmável pelo usuário, não tratada automaticamente como fato.

## Busca e exportação

Começar busca por SQL/PostgreSQL FTS quando necessário. Embeddings/vector DB somente com caso de uso comprovado. Exportação: Markdown → TXT → DOCX → PDF.

## Fora do escopo próximo

- Redis/Celery por antecipação;
- microservices de IA;
- Kubernetes/GPU orchestration;
- múltiplos providers de STT simultâneos;
- RAG/vector DB sem necessidade real.

---

**Status:** Planned  
**Last Updated:** 2026-08-16
