# ADR-016 — Upload de áudio com unidade de trabalho e compensação

**Status:** Aceita  
**Data:** 2026-08-04

## Contexto

O upload combina filesystem, banco de dados e transição de estado. Esses recursos não compartilham uma transação ACID única.

## Decisão

O `AudioService` será o coordenador do caso de uso. O repositório de áudio apenas adiciona e executa `flush`; o commit pertence ao serviço. Se qualquer etapa falhar, o serviço executa rollback e remove o arquivo salvo.

Os arquivos serão armazenados em `storage/audio/{meeting_id}/{uuid}.{ext}`. O nome original não será usado como nome físico.

## Alternativas rejeitadas

- Commit dentro de cada repository: impede atomicidade do caso de uso.
- Salvar com nome original: permite colisões e aumenta risco de manipulação de caminhos.
- Integrar Whisper no mesmo endpoint: aumenta timeout e acoplamento antes de existir processamento assíncrono persistente.

## Consequências

A solução mantém o fluxo simples e testável. A compensação é suficiente para armazenamento local, mas deverá evoluir para uma estratégia de jobs/outbox quando houver processamento distribuído ou storage remoto.
