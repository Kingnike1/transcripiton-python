# Sprint 3 — Onboarding e workspace inicial

## Objetivo

Permitir que um usuário novo entenda como começar no AMIP sem conhecer Worker, Whisper, Pyannote ou Ollama, preservando o diagnóstico técnico para quem precisa operá-lo.

A experiência deve responder, já no workspace:

1. o ambiente básico está pronto?;
2. qual é o próximo passo?;
3. quais recursos opcionais ainda precisam de configuração?;
4. como criar a primeira reunião e continuar o fluxo?

## Dependência da Sprint 2

A Sprint 3 depende dos conceitos introduzidos nas Sprints 1 e 2. No momento da execução, o PR da Sprint 2 ainda estava aberto e os workflows de PR não estavam sendo retornados pelo GitHub.

Como houve solicitação explícita para executar a Sprint 3 mesmo assim, esta branch foi criada temporariamente **sobre `feature/ux-02-job-experience`**, formando um PR empilhado. Isso evita reconstruir onboarding sobre contratos anteriores à Sprint 2.

Regra para integração:

- Sprint 3 **não deve ser integrada diretamente em `integration/ux-roadmap` antes da Sprint 2**;
- após Sprint 2 ser aprovada e integrada, o PR da Sprint 3 deve ser retargetado para `integration/ux-roadmap`;
- `develop` permanece intocada.

## Implementação

### `OnboardingService`

O serviço deriva o estado do onboarding a partir de dados já existentes:

- quantidade de reuniões do workspace;
- payload sanitizado de `ReadinessService`.

Nenhum novo estado de onboarding é persistido no banco nesta Sprint.

Capacidades centrais para o primeiro processamento:

- DATABASE;
- WORKER;
- FFPROBE;
- WHISPER;
- STORAGE.

Capacidades complementares exibidas sem bloquear o início básico:

- MICROPHONE;
- DIARIZATION;
- LLM;
- EXPORT.

### API

`GET /api/onboarding`

Retorna somente informações sanitizadas, passos da jornada, problemas centrais e problemas opcionais. O endpoint respeita o usuário atual/local mode por meio das dependências existentes.

### Workspace

A página `/meetings` passa a exibir um guia opcional com quatro passos:

1. verificar ambiente;
2. criar reunião;
3. adicionar áudio;
4. acompanhar processamento.

Quando o workspace está vazio, o guia permanece visível mesmo que tenha sido ocultado anteriormente no navegador. Para workspaces já iniciados, o usuário pode ocultar ou reabrir o guia; essa preferência é apenas de apresentação e fica em `localStorage`, não no domínio.

O formulário de criação ganhou contexto sobre o que acontece depois e ajuda nos campos sem alterar as regras de negócio.

## Segurança

- nenhuma credencial é exposta;
- o onboarding reutiliza somente o payload sanitizado do Readiness;
- ownership das reuniões continua no backend;
- nenhum processamento pesado foi movido para request HTTP;
- nenhuma migration foi necessária;
- nenhuma preferência visual do onboarding é tratada como estado de domínio.

## Critérios de aceite

- usuário sem reuniões enxerga claramente a primeira ação;
- problema em capacidade central aponta para Diagnóstico antes do processamento;
- recurso opcional indisponível não é apresentado como falha total do workspace;
- usuário com reuniões pode reabrir o guia a qualquer momento;
- API não expõe tokens/secrets;
- criação de reunião continua levando ao fluxo já existente;
- testes cobrem first-run, ambiente bloqueado, workspace existente e payload seguro.

## Quality gates

Antes da integração final:

- pytest;
- coverage conforme protocolo;
- Ruff;
- mypy;
- Bandit;
- pip-audit;
- Docker/CI aplicável;
- validação visual do workspace em desktop e viewport estreito.
