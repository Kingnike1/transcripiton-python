# AMIP — Estratégia de Branches das Sprints de UX

**Status:** obrigatório durante o ciclo de Sprints de UX.

> **REGRA OPERACIONAL:** antes de criar, executar, revisar ou integrar qualquer Sprint deste ciclo, reler este documento junto com `docs/current/IMPLEMENTATION_PROTOCOL.md`. Em caso de conflito sobre estratégia Git durante este ciclo, este documento prevalece porque registra a decisão posterior de preservação da `develop`.

## Objetivo

Preservar a branch `develop` como a versão estável existente antes do novo ciclo de experiência do usuário, permitindo que todas as Sprints sejam construídas, testadas e integradas separadamente antes de qualquer alteração na `develop`.

## Estrutura oficial

```text
develop
   │
   └── integration/ux-roadmap
          │
          ├── feature/ux-01-readiness
          ├── feature/ux-02-job-experience
          ├── feature/ux-03-onboarding
          ├── feature/ux-04-audio-upload
          ├── feature/ux-05-microphone
          ├── ...
          └── demais Sprints
```

## Papel de cada branch

### `develop`

- preserva a versão anterior ao ciclo de UX;
- não recebe merges individuais das Sprints durante o ciclo;
- serve como ponto de recuperação estável;
- só recebe o ciclo completo depois da validação final.

### `integration/ux-roadmap`

- é a branch intermediária oficial do ciclo de UX;
- recebe todas as Sprints aprovadas;
- acumula a evolução integrada do produto;
- é a base das próximas feature branches;
- deve permanecer executável e testável após cada merge.

### `feature/*`

- uma branch por Sprint;
- deve nascer da versão mais recente de `integration/ux-roadmap`;
- recebe somente o escopo da Sprint correspondente;
- abre PR contra `integration/ux-roadmap`, nunca diretamente contra `develop` durante este ciclo;
- somente é integrada após os quality gates definidos no protocolo.

## Fluxo de uma Sprint

```text
integration/ux-roadmap
        ↓
criar feature/sprint
        ↓
reler protocolos obrigatórios
        ↓
implementar incrementalmente
        ↓
testes + quality gates
        ↓
PR para integration/ux-roadmap
        ↓
review
        ↓
merge
        ↓
integration/ux-roadmap atualizada
```

A Sprint seguinte nasce **depois** da branch de integração conter as Sprints anteriores aprovadas, quando existir dependência entre elas.

## Encerramento do ciclo

Somente após todas as Sprints planejadas estarem concluídas e integradas:

```text
integration/ux-roadmap
        ↓
validação E2E completa
        ↓
regressão
        ↓
security/quality gates
        ↓
revisão final
        ↓
PR final
        ↓
develop
```

O merge final em `develop` não deve acontecer se houver regressão conhecida, quality gate vermelho, migration não validada ou conflito com `IMPLEMENTATION_PROTOCOL.md`.

## Regra de preservação

Durante todo este ciclo:

> **Não usar `develop` como área de experimentação e não integrar Sprints individuais diretamente nela.**

Se for necessário comparar comportamento antigo e novo, usar:

- `develop` = baseline estável anterior;
- `integration/ux-roadmap` = produto com Sprints já aprovadas;
- `feature/*` = trabalho ainda em desenvolvimento.

## Sprint 1

A Sprint 1 (`feature/ux-01-readiness`) foi redirecionada para `integration/ux-roadmap` e integrada nela após CI, Quality e Docker concluírem com sucesso.
