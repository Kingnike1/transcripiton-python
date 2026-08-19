# Sprint 1 — Prontidão e diagnóstico do ambiente

A Sprint 1 introduz um contrato único para representar as capacidades operacionais do AMIP e um painel seguro de diagnóstico.

## Objetivo

Permitir que usuário e operador entendam, antes de iniciar um fluxo, quais recursos estão prontos, quais precisam de configuração, quais estão indisponíveis e quais só podem ser verificados no navegador.

## Estados

- `READY`
- `CONFIGURATION_REQUIRED`
- `UNAVAILABLE`
- `NOT_VERIFIED`

A UI traduz esses estados para linguagem humana. Nenhuma resposta de prontidão deve expor tokens, senhas, connection strings ou outros segredos.

## Capacidades verificadas

- banco de dados;
- worker por heartbeat em storage compartilhado;
- FFprobe;
- faster-whisper;
- microfone (marcado como não verificado até o browser validar permissão/dispositivo);
- pyannote + presença do token Hugging Face;
- Ollama + modelo configurado;
- storage gravável e espaço mínimo;
- dependências de exportação PDF/DOCX.

## Endpoints e interface

- `GET /api/readiness` — diagnóstico estruturado e seguro;
- `GET /readiness` — painel visual de prontidão;
- `/meetings` — possui entrada para diagnóstico e onboarding de estado vazio.

## Heartbeat do worker

O entrypoint do worker publica um heartbeat a cada 5 segundos em `.amip-worker-heartbeat` dentro de `STORAGE_PATH`. O painel considera o worker indisponível quando não encontra heartbeat ou quando ele está desatualizado por mais de 15 segundos.

A escolha evita migration nesta Sprint e funciona no desenho atual em que web e worker compartilham storage. Se a topologia futura separar os filesystems, o heartbeat deve migrar para um backend compartilhado apropriado.

## Segurança

- valores de secrets nunca são retornados;
- o token Hugging Face é testado apenas por presença nesta Sprint;
- detalhes técnicos completos continuam nos logs, não na UI;
- a página respeita o mesmo modo de autenticação do workspace.

## Limites conhecidos

- permissão/dispositivo de microfone só podem ser validados no navegador;
- presença de `faster-whisper`/`pyannote` não garante que o modelo já esteja baixado; o primeiro carregamento real continua sendo a validação definitiva;
- o check do Ollama valida conectividade e presença do nome do modelo configurado.

## Próxima Sprint

A Sprint 2 deve consumir estes estados na experiência de jobs/pipeline, distinguindo fila, processamento, retry, bloqueio, falha e conclusão.
