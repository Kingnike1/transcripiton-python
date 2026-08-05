# Sprint 5 — Upload e Armazenamento Seguro de Áudio

## Objetivo

Entregar a primeira fatia vertical funcional de áudio: receber um arquivo, validar, armazenar fora da pasta pública, persistir metadados e mover a reunião para `AUDIO_UPLOADED`.

## Entregas

- `POST /api/meetings/{meeting_id}/audio`
- `GET /api/meetings/{meeting_id}/audio`
- `AudioRepository`
- `AudioService` transacional
- `AudioValidator`
- schemas Pydantic de áudio
- testes unitários e de integração
- CI com cobertura mínima de 80%

## Segurança

A validação verifica nome, extensão, MIME type, tamanho, arquivo vazio e assinatura binária básica. O nome físico é um UUID gerado pelo `StorageService`; o nome original é mantido apenas como metadado.

## Consistência

O serviço controla a unidade de trabalho. Em falha de banco, executa rollback e remove o arquivo já gravado. Upload duplicado retorna conflito e reunião inexistente retorna 404.

## Fora do escopo

Whisper, diarização, gravação por microfone, streaming, autenticação e filas externas permanecem para Sprints futuras.

## Critérios de aceite

- upload válido retorna 201;
- metadados podem ser consultados;
- status muda para `AUDIO_UPLOADED`;
- formatos falsos ou incompatíveis são rejeitados;
- arquivo vazio e arquivo acima do limite são rejeitados;
- upload duplicado retorna 409;
- falha de persistência não deixa arquivo órfão;
- testes existentes continuam protegidos pelo CI.
