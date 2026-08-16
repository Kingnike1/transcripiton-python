# ADR-019 — Upload em chunks com staging e inspeção por ffprobe

**Status:** Aceita  
**Data:** 2026-08-16  
**Stack:** P0.3 — Upload seguro em streaming

## Contexto

O endpoint de áudio executava `await file.read()`, materializando o upload inteiro em memória antes da validação. Com limite configurável de centenas de MB, múltiplos uploads poderiam consumir RAM proporcional ao tamanho total recebido.

Além disso, a validação existente verificava apenas extensão, MIME e assinatura binária curta, sem confirmar se o container possuía um stream de áudio legível.

## Decisão

O upload passa a seguir este fluxo:

```text
UploadFile.file
  ↓ leitura síncrona em threadpool
chunks de 1 MiB
  ↓ limite contado durante a escrita
storage/temp/{uuid}.staged.{ext}
  ↓ validação de assinatura
ffprobe
  ↓ duração / codec / canais / sample rate
promoção atômica com os.replace
  ↓
storage/audio/{meeting_id}/{uuid}.{ext}
  ↓
Unit of Work
  ├── Audio
  └── Meeting.status
```

### Regras

- O endpoint nunca chama `file.read()` sem limite.
- `AudioUploadStager` escreve o stream em chunks e aborta imediatamente ao exceder o limite.
- Arquivos em staging preservam a extensão declarada para melhorar a detecção de container.
- O arquivo temporário é descartado em qualquer falha de validação ou inspeção.
- A promoção usa `os.replace` dentro do mesmo storage root para ser atômica no filesystem local.
- Se o banco falhar depois da promoção, o arquivo final é removido por compensação enquanto o commit não tiver sido confirmado.
- `ffprobe` deve existir no ambiente de execução; ausência é tratada como indisponibilidade do servidor (HTTP 503), não como erro do usuário.
- Metadados técnicos são persistidos em `audios` pela migration `0002_audio_media_metadata`.

## Metadados persistidos

- duração em segundos inteiros;
- codec;
- número de canais;
- sample rate.

## Alternativas rejeitadas

### Continuar com `await file.read()`

Rejeitada por crescimento de memória proporcional ao arquivo.

### Escrever diretamente no destino final

Rejeitada porque arquivos ainda não validados poderiam aparecer como definitivos e exigiriam mais estados de recuperação.

### Executar ffprobe dentro do event loop

Rejeitada. O pipeline síncrono de filesystem/ffprobe é executado via threadpool para não bloquear o event loop do FastAPI.

### Introduzir object storage multipart agora

Rejeitada por YAGNI. O storage ainda é local e `os.replace` oferece uma implementação simples para o MVP. O contrato deverá evoluir quando S3/MinIO forem realmente necessários.

## Consequências

### Positivas

- memória do processo deixa de crescer com o arquivo inteiro;
- limite é aplicado durante a transferência para storage;
- temporários não sobrevivem a falhas conhecidas;
- containers inválidos são rejeitados antes do commit;
- metadados reais ficam disponíveis para o futuro worker de transcrição.

### Riscos residuais

- o limite ainda precisa ser duplicado no reverse proxy/gateway antes de produção;
- disco pode ser pressionado por uploads simultâneos até P0.4/P3 adicionar quotas e proteção contra abuso;
- `ffprobe` é dependência de sistema e precisa entrar no deployment/containers;
- storage local continua limitado a uma instância.
