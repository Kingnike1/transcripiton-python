# ADR-023 — Quality gates e superfície de dependências de runtime

**Status:** Accepted  
**Data:** 2026-08-16

## Contexto

Antes da P0.7, o AMIP possuía apenas um gate de testes/cobertura. O repositório não bloqueava erros de lint, inconsistências de tipo, drift de migrations ou achados de segurança estática. A governança também declarava Python 3.12+ apesar de o CI validar somente 3.11.

A primeira execução de `pip-audit` revelou 27 advisories em 7 pacotes. Parte desse passivo vinha de ferramentas de teste e bibliotecas de exportação ainda não implementadas misturadas no `requirements.txt` de produção.

## Decisão

### Dois workflows complementares

O projeto mantém dois workflows independentes:

- **CI** — suíte completa em Python 3.11 com cobertura >=80%;
- **Quality** — lint, tipos, migrations, segurança, dependências e compatibilidade Python 3.12.

Separar os workflows reduz acoplamento, facilita diagnóstico e permite evolução incremental dos gates.

### GitHub Actions

`actions/checkout` e `actions/setup-python` usam v6, eliminando o runtime legado Node 20 das versões anteriores.

### Compatibilidade Python

O projeto declara suporte comprovado para:

- Python 3.11 — baseline mínima;
- Python 3.12 — matriz de compatibilidade obrigatória.

Versões futuras só serão declaradas suportadas depois de CI verde.

### Ruff

Ruff é o linter oficial. A adoção inicial bloqueia `F` e `E9`, priorizando erros semânticos/sintáticos. Ordenação de imports e formatação poderão ser ampliadas depois sem criar churn cosmético durante a estabilização.

### mypy

mypy é gate bloqueante para `app` e `main.py`. Contratos devem ser corrigidos em vez de silenciados com ignores amplos.

### Migrations

`tests/test_migrations.py` é executado como gate explícito no workflow Quality, além da suíte geral.

### Segurança estática

Bandit bloqueia achados de severidade média/alta no código da aplicação.

### Dependências

- `requirements.txt` contém somente dependências realmente necessárias no runtime atual;
- `requirements-dev.txt` contém testes, lint, type checker e scanners;
- dependências de DOCX/PDF/Markdown foram removidas do runtime porque exportação ainda não está implementada;
- `pip-audit -r requirements.txt` é gate bloqueante;
- upgrades de dependências são direcionados e validados por testes, não executados de forma cega.

A P0.7 atualizou o núcleo HTTP/configuração afetado pelos advisories e reduziu a superfície de produção. Após a remediação, o `pip-audit` retornou `No known vulnerabilities found`.

### Defaults seguros

Bandit identificou bind padrão em `0.0.0.0`. O default passou para `127.0.0.1`; exposição externa exige configuração explícita pelo ambiente/deployment.

### Git e governança

`PROJECT_GOVERNANCE.md` formaliza:

- GitFlow adaptado (`main` estável, `develop` integração, branches por Stack);
- Conventional Commits;
- Definition of Done baseada em CI/Quality + documentação + merge + pós-merge verde.

## Branch protection

Proteção obrigatória da `main` continua desejada, mas a integração GitHub disponível nesta execução respondeu 403 ao endpoint de branch protection e não expõe ação de ruleset/protection com permissão suficiente.

Isso é tratado como **controle administrativo externo pendente**, não como evidência de que a branch esteja protegida. A limitação não justifica remover os gates automatizados existentes nem bloquear indefinidamente o desenvolvimento em `develop`.

## Alternativas rejeitadas

### Um workflow monolítico

Rejeitado por aumentar o acoplamento entre regressão funcional e qualidade estática, dificultando diagnóstico e rollback.

### Deixar scanners apenas como warning

Rejeitado para lint, tipos, migrations, Bandit e runtime dependency audit. Após a remediação, esses checks são suficientemente estáveis para bloquear merge.

### Atualizar todas as dependências indiscriminadamente

Rejeitado. O projeto atualiza somente dependências justificadas por vulnerabilidade, compatibilidade ou uso real e exige regressão verde depois.

### Manter bibliotecas futuras no runtime

Rejeitado. Dependências de funcionalidades não implementadas aumentam superfície de ataque e manutenção sem entregar valor.

## Consequências

### Positivas

- regressões passam por gates funcionais e estáticos;
- Python 3.11/3.12 têm evidência contínua;
- runtime conhecido não possui advisories reportados pelo `pip-audit` no fechamento da P0.7;
- dependências de desenvolvimento não poluem produção;
- governança agora corresponde ao fluxo Git real.

### Trade-offs

- CI fica mais longo e depende de mais ferramentas;
- novos tipos/lints podem exigir manutenção em código legado;
- branch protection ainda precisa de ação administrativa fora da permissão atual da integração.

## Critérios de revisão

Revisar este ADR quando:

- Python 3.13+ for adicionado à matriz;
- Ruff passar a controlar format/import ordering;
- um lockfile/gerenciador de dependências substituir requirements pinados;
- branch rulesets puderem ser geridos pela integração;
- novos scanners forem introduzidos.
