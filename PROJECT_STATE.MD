# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-17  
**Stack atual:** Stack 14 — Infraestrutura de produção  
**Branch de integração:** `develop`  
**Stack 13:** autenticação/autorização implementada em `agent/stack-13-auth`  
**Status esperado após gate/merge:** Stacks 7–13 concluídas; Stack 14 é a próxima prioridade

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando configurado;
- identificação/confirmação de participantes;
- inteligência estruturada local via Ollama + Qwen3;
- usuários, login e logout;
- senhas protegidas com `scrypt` + salt;
- sessões opacas, persistentes e revogáveis;
- cookie HttpOnly/SameSite e Secure fora de ambiente local;
- ownership de reuniões por usuário;
- isolamento de áudio, transcrição, diarização, participantes, análise e jobs pelo dono da reunião;
- modo local legado preservado enquanto não existem contas;
- primeira conta assume reuniões legadas sem dono;
- Docker/Compose com migrations, web e worker.

## Stack 13 — Autenticação e autorização — IMPLEMENTADA

- [x] entidade `User`;
- [x] entidade `AuthSession`;
- [x] cadastro, login, logout e status de autenticação;
- [x] senha com `hashlib.scrypt`, salt aleatório e comparação constante;
- [x] token de sessão opaco; somente hash SHA-256 persistido;
- [x] sessão expira e pode ser revogada no logout;
- [x] cookie HttpOnly/SameSite=Lax e Secure em staging/produção;
- [x] `Meeting.owner_id`;
- [x] primeira conta faz claim de reuniões legadas sem owner;
- [x] reuniões novas recebem owner quando autenticação está ativa;
- [x] listagem/pesquisa/CRUD filtrados por owner;
- [x] proteção de áudio, transcrição, diarização, participantes, análise e jobs;
- [x] acesso cruzado responde 404 para não revelar recurso alheio;
- [x] UI de login/criação de conta/logout;
- [x] modo local sem contas preservado;
- [x] migration `0009_auth_ownership`;
- [x] testes de sessão, hashing, legacy claim e isolamento multiusuário;
- [x] documentação e ADR-028.

## Próximas stacks

1. Stack 14 — infraestrutura de produção;
2. Stack 15 — busca;
3. Stack 16 — exportação;
4. Stack 17 — gravação por microfone.

## Pendências operacionais independentes

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test com áudio real/modelos baixados na máquina de uso;
- branch protection administrativa da `main` quando permissões permitirem.

## Próxima Stack

**Stack 14 — Infraestrutura de produção** deve tratar banco/storage/deploy/observabilidade/backups e hardening operacional sem transformar prematuramente o monólito em microserviços.

**Document Version:** 9.0  
**Status:** Active
