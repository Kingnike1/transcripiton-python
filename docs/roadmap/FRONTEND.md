# Roadmap de Frontend

> **Status: Planned.** Este documento descreve direção futura. Não significa que as telas abaixo já existam.

## Stack definida

A direção atual continua:

- Jinja2;
- Bootstrap 5;
- HTMX para interações incrementais;
- JavaScript mínimo/vanilla;
- server-side rendering.

React/Vue/Angular só devem ser avaliados se a complexidade real de estado/interação ultrapassar o que Jinja2 + HTMX conseguem manter com clareza.

## Estado atual

Hoje existe uma landing page simples. Ainda não existe uma experiência completa de gerenciamento de reuniões no navegador.

A API de reuniões e o upload de áudio existem, mas a UI correspondente ainda precisa ser construída.

## Primeira vertical slice de produto

Depois de jobs persistentes e transcrição real, a prioridade de frontend é permitir:

```text
Lista de reuniões
  ↓
Criar reunião
  ↓
Detalhe da reunião
  ↓
Upload de áudio
  ↓
Acompanhar processamento
  ↓
Visualizar transcrição
```

### Telas mínimas

- lista de reuniões;
- formulário de criação/edição;
- detalhe da reunião;
- upload de áudio;
- metadados/player quando endpoint de streaming/download seguro existir;
- progresso do job;
- visualização da transcrição.

## Progresso do job

Começar com polling/HTMX. Server-Sent Events podem ser avaliados depois se a UX justificar atualização mais imediata. WebSocket não é requisito inicial.

## Microfone

Gravação direta deve ficar no navegador, usando APIs como `getUserMedia`/`MediaRecorder`. O backend recebe e valida o resultado; captura de microfone não deve ser responsabilidade de uma classe Python no servidor.

## Segurança

Antes de UI multiusuário pública:

- autenticação;
- autorização por recurso/organização;
- CSRF para operações baseadas em sessão;
- rate limits/quotas;
- streaming/download autenticado;
- política de retenção e exclusão.

## Acessibilidade

Telas novas devem priorizar:

- HTML semântico;
- navegação por teclado;
- labels explícitos;
- contraste adequado;
- mensagens de erro associadas aos campos;
- estados de loading compreensíveis.

## Fora do escopo imediato

- colaboração em tempo real;
- editor de transcript altamente interativo;
- dashboards complexos;
- SPA;
- WebSockets por padrão.

Esses itens precisam de demanda real antes de adicionar outra stack frontend.

---

**Status:** Planned  
**Last Updated:** 2026-08-16
