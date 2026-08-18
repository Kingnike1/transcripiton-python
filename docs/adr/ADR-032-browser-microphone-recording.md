# ADR-032 — Gravação de reunião pelo microfone do navegador

## Status
Accepted — Stack 17

## Context
O AMIP já possui um pipeline seguro para upload, inspeção, persistência e transcrição de áudio. A Stack 17 precisa permitir que o usuário capture uma reunião diretamente no navegador sem criar um segundo pipeline de mídia.

## Decision
A captura usa `navigator.mediaDevices.getUserMedia` + `MediaRecorder` no navegador. O áudio permanece local até o usuário encerrar, revisar e confirmar **Usar gravação**. Depois disso, o blob é enviado ao endpoint existente `POST /api/meetings/{meeting_id}/audio` e passa pelas mesmas validações, limites, `ffprobe`, storage e transições de estado de qualquer arquivo enviado manualmente.

O navegador escolhe o primeiro formato compatível entre WebM/Opus, WebM, Ogg/Opus e MP4. O backend normaliza parâmetros MIME como `audio/webm;codecs=opus` para `audio/webm`, mas continua validando extensão, assinatura do arquivo, tamanho e conteúdo real.

A gravação exige secure context do navegador (HTTPS ou localhost). Tracks do microfone são sempre encerradas ao parar, descartar ou sair da página.

## Consequences
- não existe pipeline de áudio duplicado;
- gravações recebem exatamente as mesmas proteções do upload convencional;
- o usuário pode revisar o áudio antes de enviá-lo;
- permissão de microfone permanece sob controle do navegador;
- compatibilidade depende do suporte a `MediaRecorder` do navegador;
- gravações longas permanecem em memória no navegador até o envio; streaming/chunk upload pode ser adicionado no futuro se métricas justificarem.
