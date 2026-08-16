# ADR-024 — Taxonomia documental e fontes da verdade

**Status:** Accepted  
**Data:** 2026-08-16

## Contexto

Até a P0.8, a pasta `docs/` misturava três classes de conteúdo no mesmo nível:

1. documentação do sistema realmente implementado;
2. especificações/roadmaps de funcionalidades futuras;
3. prompts e registros históricos de Sprints antigas.

Isso produziu divergências graves: documentos de frontend, IA e deployment descreviam componentes inexistentes como se fossem atuais, enquanto arquivos antigos continuavam apontando para Python, comandos, endpoints e estrutura de pastas superseded.

## Decisão

A documentação passa a usar a seguinte taxonomia:

```text
docs/
├── README.md          # mapa e regra de fontes da verdade
├── 00_PROJECT_OVERVIEW.md
├── 06_BACKLOG.md
├── current/           # somente implementação real
├── roadmap/           # futuro explicitamente planejado
├── archive/           # histórico/superseded
└── adr/               # decisões arquiteturais
```

### `docs/current/`

Pode descrever apenas comportamento comprovado pelo código, migrations, testes e CI. Endpoints futuros não entram em `current/API.md` antes da implementação.

### `docs/roadmap/`

Descreve intenção futura. Todo documento deve deixar claro que seu conteúdo é planejado e não representa funcionalidade disponível.

### `docs/archive/`

Contém catálogo/resumos de materiais superseded. A versão integral de documentos removidos continua preservada no histórico Git, com o commit-base registrado quando necessário.

### `docs/adr/`

Mantém decisões arquiteturais e sua evolução. Decisões superseded devem ser marcadas, não apagadas sem rastreabilidade.

## Ordem de autoridade

Em caso de divergência:

1. código, migrations, testes e CI;
2. `PROJECT_GOVERNANCE.md` e `PROJECT_STATE.MD`;
3. `TECH_DECISIONS.md` e ADRs aceitos;
4. `docs/current/`;
5. `docs/06_BACKLOG.md` e `docs/roadmap/`;
6. `docs/archive/` apenas como histórico.

`docs/roadmap/` e `docs/archive/` nunca são prova de que uma funcionalidade existe.

## Documentos raiz

- `PROJECT_CONTEXT.md` mantém visão de produto e matriz de capacidade atual;
- `PROJECT_GOVERNANCE.md` mantém regras obrigatórias;
- `PROJECT_STATE.MD` mantém estado operacional mais recente;
- `README.md` é a entrada pública do repositório;
- `docs/README.md` é o índice documental.

## Alternativas rejeitadas

### Manter todos os documentos numerados na raiz de `docs/`

Rejeitado porque o número/ordem não comunica se o conteúdo é atual, futuro ou histórico.

### Copiar documentos para novas pastas e manter os antigos ativos

Rejeitado porque criaria duas fontes concorrentes de verdade. Caminhos antigos são removidos depois que referências são atualizadas.

### Apagar todo conteúdo histórico

Rejeitado. O Git mantém o material integral e `docs/archive/` registra contexto suficiente para encontrá-lo, preservando rastreabilidade sem poluir a documentação operacional.

## Consequências

### Positivas

- reduz risco de implementar uma especificação antiga por engano;
- torna o estado atual auditável;
- permite roadmap detalhado sem fingir que o produto já existe;
- facilita entrada de novos colaboradores/agentes;
- prepara a Sprint 6B com documentação consistente.

### Trade-offs

- links antigos precisam ser atualizados;
- referências externas aos caminhos antigos podem quebrar;
- a equipe precisa respeitar a categoria correta ao criar novos documentos.

## Regra de manutenção

Toda Stack deve avaliar se sua mudança afeta:

- `PROJECT_STATE.MD`;
- `PROJECT_CONTEXT.md`;
- `docs/current/`;
- backlog/roadmap;
- decisões/ADRs.

Se um documento deixar de representar o sistema, ele deve ser atualizado, movido para roadmap/archive ou removido como fonte ativa.
