# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-18  
**Stack atual:** Stack 17 — Gravação por microfone  
**Branch de integração:** `develop`  
**Branch da Stack 17:** `agent/stack-17-microphone-recording`  
**Status esperado após gate/merge:** Stacks 7–17 concluídas; ciclo planejado de Stacks concluído

## Capacidade atual

- CRUD e interface de reuniões;
- upload/armazenamento seguro de áudio;
- gravação de reunião pelo microfone do navegador;
- preview local antes do envio;
- jobs duráveis e worker separado;
- transcrição local com `faster-whisper`;
- diarização local com `pyannote.audio` quando configurado;
- identificação/confirmação de participantes;
- inteligência estruturada local via Ollama + Qwen3;
- autenticação, sessões revogáveis e ownership;
- baseline de produção com PostgreSQL, migrations, web, worker e backups;
- busca textual ownership-aware em título, descrição e transcrição;
- exportação sob demanda em TXT, Markdown, JSON, DOCX e PDF.

## Stack 17 — Gravação por microfone — IMPLEMENTADA

- [x] captura via `getUserMedia`;
- [x] gravação via `MediaRecorder`;
- [x] seleção de formato compatível pelo navegador;
- [x] suporte a WebM/Opus, WebM, Ogg/Opus e MP4 quando disponíveis;
- [x] contador de duração;
- [x] parar e descartar gravação;
- [x] preview local antes do upload;
- [x] áudio não é enviado sem confirmação do usuário;
- [x] reaproveitamento do endpoint seguro de upload existente;
- [x] normalização segura de MIME types com parâmetros de codec;
- [x] validação de assinatura/tamanho/ffprobe preservada;
- [x] encerramento das tracks do microfone ao parar, descartar ou sair;
- [x] tratamento de permissão negada e navegador incompatível;
- [x] requisito explícito de HTTPS ou localhost;
- [x] testes de integração com o pipeline existente;
- [x] ADR-032;
- [x] versão 0.13.0;
- [ ] CI + Quality + Docker verdes;
- [ ] PR integrado em `develop`.

## Decisão de arquitetura

A gravação não cria um segundo pipeline de mídia. O navegador produz um arquivo temporário local e, somente após confirmação do usuário, envia esse arquivo ao mesmo pipeline de upload existente. Isso mantém storage, validação, ownership, inspeção e transições de estado em um único caminho.

## Próximos passos após Stack 17

Não há uma Stack 18 planejada no backlog atual. Depois do merge, o foco passa para validação operacional end-to-end, smoke tests reais, hardening de produção e definição de uma próxima fase de produto baseada no uso real.

## Pendências operacionais independentes

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test com áudio real/modelos baixados na máquina de uso;
- smoke test da gravação em navegador real via HTTPS/localhost;
- configurar destino off-host para backups no ambiente de produção escolhido;
- configurar proxy/TLS e monitor externo no ambiente de produção escolhido;
- branch protection administrativa da `main` quando permissões permitirem.

**Document Version:** 13.0  
**Status:** Active
