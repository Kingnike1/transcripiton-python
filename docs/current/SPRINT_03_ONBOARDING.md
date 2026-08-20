# Sprint 3 — Onboarding e workspace inicial

## Objetivo

Permitir que um usuário novo entenda como começar no AMIP sem conhecer Worker, Whisper, Pyannote ou Ollama, preservando o diagnóstico técnico para quem precisa operá-lo.

A experiência responde no workspace:

1. o ambiente básico está pronto?;
2. qual é o próximo passo?;
3. quais recursos opcionais ainda precisam de configuração?;
4. como criar a primeira reunião e continuar o fluxo?

## Dependências

A Sprint 3 depende das Sprints 1 e 2. Ela foi normalizada sobre `integration/ux-roadmap` após a Sprint 2 ser corrigida, validada e integrada.

## Implementação

### `OnboardingService`

O serviço deriva o estado do onboarding a partir de dados já existentes:

- quantidade de reuniões do workspace;
- payload sanitizado de `ReadinessService`.

Nenhum novo estado de onboarding é persistido no banco.

Capacidades centrais:

- DATABASE;
- WORKER;
- FFPROBE;
- WHISPER;
- STORAGE.

Capacidades complementares:

- MICROPHONE;
- DIARIZATION;
- LLM;
- EXPORT.

### API

`GET /api/onboarding` retorna informações sanitizadas, passos da jornada, problemas centrais e opcionais, respeitando usuário atual/local mode.

### Workspace

A página `/meetings` exibe um guia com quatro passos:

1. verificar ambiente;
2. criar reunião;
3. adicionar áudio;
4. acompanhar processamento.

A preferência de ocultar/reabrir o guia fica apenas em `localStorage`, sem virar estado de domínio.

## Segurança

- nenhuma credencial é exposta;
- onboarding reutiliza somente o payload sanitizado do Readiness;
- ownership permanece no backend;
- nenhum processamento pesado ocorre no request HTTP;
- nenhuma migration foi necessária.

## Critérios de aceite

- usuário sem reuniões enxerga a primeira ação;
- capacidade central indisponível aponta para Diagnóstico;
- recurso opcional indisponível não bloqueia falsamente o workspace;
- usuário com reuniões pode reabrir o guia;
- API não expõe secrets;
- criação de reunião continua o fluxo existente;
- testes cobrem first-run, ambiente bloqueado, workspace existente e payload seguro.
