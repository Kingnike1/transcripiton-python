# PROJECT_STATE.MD

## Estado Atual do Projeto

**Projeto:** AI Meeting Intelligence Platform (AMIP)  
**Última atualização:** 2026-08-18  
**Fase atual:** Validação operacional pós-Stack 17  
**Branch de integração:** `develop`  
**Último merge:** PR #21 — Stack 17 Gravação por microfone  
**Commit de integração:** `cf1ae3e81fd81e0d492dc4bda3386070cb9e93b2`  
**Status:** Stacks 7–17 concluídas e integradas; ciclo planejado de Stacks concluído

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

## Stack 17 — Gravação por microfone — CONCLUÍDA

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
- [x] correção da corrida de descarte durante gravação;
- [x] testes de integração com o pipeline existente;
- [x] ADR-032;
- [x] versão 0.13.0;
- [x] CI + Quality + Docker verdes no PR #21;
- [x] PR #21 integrado em `develop`.

## Decisão de arquitetura

A gravação não cria um segundo pipeline de mídia. O navegador produz um arquivo temporário local e, somente após confirmação do usuário, envia esse arquivo ao mesmo pipeline de upload existente. Isso mantém storage, validação, ownership, inspeção e transições de estado em um único caminho.

## Próxima fase

Não há uma Stack 18 planejada no backlog atual. O próximo ciclo deve começar por validação operacional end-to-end e priorização da próxima fase do produto com base no que for observado em uso real.

## Pendências operacionais

- instalar Ollama e baixar `qwen3:4b` na máquina de uso para smoke test real;
- smoke test end-to-end com áudio real/modelos baixados;
- smoke test da gravação em navegador real via HTTPS/localhost;
- configurar destino off-host para backups no ambiente de produção escolhido;
- configurar proxy/TLS e monitor externo no ambiente de produção escolhido;
- branch protection administrativa da `main` quando permissões permitirem.

**Document Version:** 13.1  
**Status:** Active
