# AMIP --- Protocolo de Implementação Segura de Features

**Projeto:** AI Meeting Intelligence Platform --- AMIP
**Finalidade:** definir as regras obrigatórias de segurança, arquitetura, estratégia, qualidade e execução para implementação das Sprints de experiência do usuário.
**Status:** norma de trabalho para as próximas features de UX.

> **REGRA OPERACIONAL OBRIGATÓRIA:** antes de planejar, executar, revisar ou concluir qualquer Sprint/feature do AMIP, reler este documento. Se uma decisão de implementação conflitar com estas regras, interromper a implementação e resolver o conflito antes de prosseguir.

## 1. Objetivo

Este documento estabelece **como a equipe deve agir antes, durante e depois de qualquer implementação** relacionada às melhorias de experiência do AMIP.

Cada mudança deve preservar arquitetura e integridade do sistema; segurança e ownership; previsibilidade dos jobs; compatibilidade com o pipeline; legibilidade/manutenção; testes e observabilidade; rollback; experiência clara para usuário e administrador.

> **A interface nunca deve esconder um problema arquitetural. Primeiro tornamos o estado do sistema confiável e observável; depois construímos a experiência sobre ele.**

## 2. Arquitetura que deve ser preservada

O AMIP continuará, salvo decisão arquitetural formal posterior, como um **monólito modular em camadas**, com servidor web e worker separados.

```text
Browser
   ↓
FastAPI / UI
   ↓
Application Services
   ↓
Repositories / SQLAlchemy
   ↓
Database

FastAPI
   ↓ cria job
ProcessingJob
   ↓
Database Queue
   ↓
Worker
   ↓
Whisper / Pyannote / Ollama-Qwen
```

### Regras arquiteturais

1. Processamento pesado **não deve acontecer dentro da requisição HTTP**.
2. FastAPI cria/consulta recursos e jobs; o Worker executa processamento pesado.
3. Banco e storage continuam sendo fontes persistentes de dados.
4. Regras de negócio não devem ser espalhadas por templates ou JavaScript.
5. A UI deve consumir estados fornecidos pelo domínio/application layer, e não reinventá-los.
6. Não introduzir microserviços, React/Next.js ou reescrita completa sem necessidade comprovada e decisão arquitetural explícita.
7. Mudanças estruturais relevantes exigem ADR/documentação correspondente.

## 3. Fonte única da verdade

Não duplicar estados entre backend e frontend.

### Incorreto

```text
Backend: DIARIZING
Frontend: processing-speakers
JavaScript: loading-diarization
Template: waiting
```

### Correto

```text
ProcessingStatus.DIARIZING
        ↓
Application Service
        ↓
DTO/API
        ↓
UI Presenter
        ↓
"Diarizando..."
```

O backend/domínio é a **fonte da verdade**. A interface traduz o estado técnico para linguagem compreensível.

## 4. Sistema de capacidades

Antes do redesign avançado, implementar uma camada de **Capabilities/Readiness**.

Capacidades mínimas: `WEB`, `DATABASE`, `WORKER`, `FFPROBE`, `WHISPER`, `MICROPHONE`, `DIARIZATION`, `LLM`, `STORAGE`, `EXPORT`.

Estados recomendados: `READY`, `CONFIGURATION_REQUIRED`, `UNAVAILABLE`, `NOT_VERIFIED`.

Nunca revelar tokens, senhas, connection strings ou outros secrets durante diagnóstico.

## 5. Estados de processamento e jobs

Estados esperados: `PENDING`, `RUNNING`, `RETRYING`, `COMPLETED`, `FAILED`, `BLOCKED`, `CANCELLED`.

| Estado | Usuário vê |
|---|---|
| PENDING | Aguardando na fila |
| RUNNING | Processando |
| RETRYING | Tentando novamente |
| COMPLETED | Concluído |
| FAILED | Não foi possível concluir |
| BLOCKED | Bloqueado por configuração |
| CANCELLED | Cancelado |

Um job não deve permanecer indefinidamente como `PENDING` quando o sistema sabe que existe um bloqueio.

## 6. Classificação obrigatória de erros

Toda nova feature deve distinguir pelo menos três categorias:

1. **Recuperável pelo usuário**, ex.: `MICROPHONE_PERMISSION_DENIED`.
2. **Problema de configuração/ambiente**, ex.: `DIARIZATION_NOT_CONFIGURED`.
3. **Falha interna**, ex.: `TRANSCRIPTION_PROCESSING_FAILED`.

Internamente preservar quando aplicável: `request_id`, `job_id`, `error_code`, stack trace e contexto técnico seguro.

Stack traces, JSON bruto, credenciais e detalhes internos **não devem ser exibidos ao usuário final**.

## 7. Segurança e ownership

```text
User
 ↓ owns
Meeting
 ↓
Audio / Transcription / Diarization / Participants / Analysis / Jobs
```

1. Nunca confiar em IDs enviados pelo cliente sem validar ownership.
2. Recursos derivados só podem ser acessados através de reunião pertencente ao usuário autorizado.
3. Worker não recebe cookie/sessão HTTP; processa jobs internos já autorizados e persistidos.
4. Nunca colocar secrets em HTML, JavaScript, logs públicos ou respostas de diagnóstico.
5. Nunca commitar `.env`, tokens do Hugging Face, chaves ou senhas.
6. Mensagens externas devem evitar enumeração desnecessária de recursos.
7. Ações destrutivas precisam de confirmação proporcional ao impacto.
8. Mudanças de autenticação/autorização exigem testes específicos de acesso cruzado.

## 8. Estratégia Git

A implementação deve partir de `develop` e usar uma branch por Sprint:

```text
feature/ux-01-readiness
feature/ux-02-job-experience
feature/ux-03-meeting-experience
feature/ux-04-intelligence-experience
feature/ux-05-accessibility-responsive
```

Nenhuma Sprint deve virar um único commit gigante.

Fluxo: `develop → feature branch → implementação incremental → quality gates → review → PR → develop`.

Evitar commits diretamente na branch protegida quando houver fluxo de feature/PR disponível.

## 9. Implementação vertical

Cada capacidade deve ser implementada **end-to-end** antes de iniciar a próxima:

```text
Detector/Regra
   ↓
Application Service
   ↓
API/DTO
   ↓
Interface
   ↓
Tratamento de erro
   ↓
Testes
```

Evitar construir todo backend, depois todo frontend e somente no final testar tudo.

## 10. Ordem das Sprints

### UX-01 — Readiness e onboarding
Capability System; diagnóstico; Worker heartbeat; FFmpeg/ffprobe; Whisper; Pyannote/Hugging Face; Ollama/Qwen; Storage; exportação; microfone; onboarding e estados vazios.

### UX-02 — Jobs e pipeline
Timeline; progresso; retry; cancelamento quando suportado; `BLOCKED`; Worker parado; atualização automática; próxima ação recomendada.

### UX-03 — Experiência da reunião
Upload; microfone; preview; transcrição navegável; timestamps; sincronização áudio/texto; diarização; revisão/confirmação de participantes.

### UX-04 — Inteligência
Checklist LLM; análise Qwen; resumo; decisões; action items; riscos; follow-ups; referências/evidências; busca; preview de exportação.

### UX-05 — Acessibilidade, responsividade e acabamento
Mobile/tablet/desktop; teclado; foco; labels; contraste; leitores de tela; estados não dependentes só de cor; loading/skeleton; consistência; E2E multi-browser.

**Acessibilidade e responsividade são consideradas desde UX-01; UX-05 é auditoria/acabamento.**

## 11. Máquina de estados visual da reunião

```text
MEETING_CREATED
      ↓
AUDIO_READY
      ↓
TRANSCRIBING
      ↓
TRANSCRIBED
      ↓
DIARIZING
      ↓
DIARIZED
      ↓
PARTICIPANTS_REVIEW
      ↓
READY_FOR_ANALYSIS
      ↓
ANALYZING
      ↓
COMPLETED
```

Falhas, retry, cancelamento e bloqueios devem aparecer como ramificações explícitas e recuperáveis.

## 12. Regras específicas de IA

### Whisper
- transcrição, não identidade das pessoas;
- distinguir falha de modelo de áudio sem fala;
- modelo/idioma efetivos observáveis sem expor configuração sensível.

### Pyannote
- responsável pela diarização;
- `SPEAKER_00`, `SPEAKER_01` são rótulos automáticos;
- nunca apresentar speaker como identidade real antes de confirmação humana;
- ausência de token/modelo deve gerar `BLOCKED`, não espera infinita.

### Ollama/Qwen
- análise só habilitada quando pré-requisitos forem satisfeitos;
- verificar provider/modelo antes da execução;
- JSON inválido/resposta bruta não chega diretamente à UI;
- resultados são conteúdo revisável;
- quando possível, decisões/tarefas/riscos possuem referência ao trecho de origem.

## 13. Banco e migrations

1. Alteração de schema exige migration Alembic.
2. Não editar banco manualmente para resolver feature.
3. Testar migration em banco novo e existente quando aplicável.
4. Preservar compatibilidade de dados quando razoável.
5. Mudanças destrutivas exigem estratégia explícita de migração/rollback.
6. SQLite para desenvolvimento local; PostgreSQL recomendado para multiusuário/staging/produção.

## 14. Quality gates obrigatórios

Antes de merge:

```text
pytest
↓
coverage >= 80%
↓
Ruff
↓
mypy
↓
migration integrity
↓
Bandit
↓
pip-audit
↓
testes de integração
↓
E2E relevante
↓
documentação
↓
review
```

Uma feature não é concluída apenas porque funciona manualmente.

## 15. Estratégia de testes

Testes acompanham a implementação: `Unit → Integration → API → E2E quando aplicável`.

Exemplo diarização:

```text
Token + Worker + modelo disponíveis → READY
Token ausente                       → BLOCKED
Worker parado                       → BLOCKED/UNAVAILABLE
Job iniciado                        → RUNNING
Job concluído                       → COMPLETED
Pyannote falhou                     → FAILED
```

A UI deve ser testada para garantir tradução correta de cada estado técnico.

## 16. Observabilidade

Quando aplicável registrar: `request_id`, `job_id`, recurso de forma segura, etapa, tentativa, início/fim, duração, error code, provider/modelo e status final.

Nunca registrar secrets ou conteúdo sensível desnecessário.

## 17. Performance e processamento pesado

1. Não bloquear HTTP com Whisper, Pyannote ou LLM.
2. Jobs longos pertencem ao Worker.
3. Evitar carregamento repetido de modelos quando reutilização segura for possível.
4. Upload e processamento têm progressos distintos.
5. UI permanece responsiva durante jobs.
6. Timeouts/retries explícitos e limitados.
7. Preferir operações idempotentes para retry seguro.

## 18. UX e mensagens

Toda etapa deve responder:

1. **O que está acontecendo?**
2. **Existe algum problema?**
3. **O que faço agora?**

Não usar mensagens genéricas quando a causa for conhecida.

## 19. Definition of Done

Uma feature só está pronta quando:

- comportamento funcional implementado;
- arquitetura respeitada;
- autorização/ownership preservados;
- erros classificados;
- estados visíveis ao usuário;
- próxima ação compreensível;
- testes adicionados/atualizados;
- quality gates aprovados;
- migrations verificadas quando aplicável;
- logs/observabilidade adequados;
- documentação atualizada;
- sem secrets no código/repositório;
- responsividade/acessibilidade verificadas no escopo afetado;
- PR revisável e commits compreensíveis.

## 20. O que não fazer

- reescrever o sistema inteiro;
- introduzir microserviços sem justificativa;
- trocar stack de frontend apenas por estética;
- colocar lógica de negócio em JavaScript/templates;
- duplicar estados do domínio;
- executar IA pesada dentro do request;
- corrigir schema manualmente sem migration;
- esconder falha de configuração como `PENDING`;
- expor stack traces ao usuário;
- expor tokens/secrets;
- fazer commit gigante com uma Sprint inteira;
- deixar testes para o final;
- fazer redesign antes de readiness/jobs;
- considerar feature pronta apenas por funcionar na máquina do desenvolvedor.

## 21. Procedimento padrão para cada nova feature

### Antes de codificar
1. **Reler este documento integralmente.**
2. Definir problema do usuário.
3. Identificar capacidade/estado envolvido.
4. Mapear impacto arquitetural.
5. Mapear segurança/ownership.
6. Definir contratos e erros.
7. Definir critérios de aceite.
8. Definir testes.

### Durante
9. Implementar verticalmente.
10. Manter commits pequenos.
11. Executar testes continuamente.
12. Preservar observabilidade.
13. Atualizar documentação necessária.

### Antes do merge
14. **Reler este documento e conferir aderência da implementação.**
15. Executar quality gates.
16. Validar fluxo feliz.
17. Validar falhas/bloqueios.
18. Validar acesso não autorizado.
19. Validar responsividade/acessibilidade afetada.
20. Revisar migrations.
21. Revisar secrets/logs.
22. Abrir/revisar PR.

## 22. Princípio final

```text
ESTADO CONFIÁVEL
      ↓
ESTADO OBSERVÁVEL
      ↓
ERRO EXPLICÁVEL
      ↓
RECUPERAÇÃO POSSÍVEL
      ↓
INTERFACE CLARA
      ↓
EXPERIÊNCIA SOFISTICADA
```

**Não construir uma interface sofisticada sobre estados internos ambíguos.**

O objetivo é fazer o AMIP não apenas funcionar, mas também **explicar seu próprio funcionamento, seus bloqueios e a próxima ação correta** ao usuário.
