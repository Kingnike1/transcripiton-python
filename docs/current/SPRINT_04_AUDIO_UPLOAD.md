# Sprint 4 — Upload e gerenciamento de áudio

## Objetivo

Transformar a entrada de áudio em um fluxo previsível, seguro e compreensível, mantendo a validação real no backend e separando claramente upload de processamento.

## Entregas

- política pública e sanitizada de upload por reunião em `GET /api/meetings/{meeting_id}/audio/policy`;
- formatos aceitos e limite de tamanho apresentados antes do envio;
- drag & drop e seleção tradicional de arquivo;
- progresso real do upload via `XMLHttpRequest.upload`;
- mensagens distintas para formato inválido, arquivo grande, conflito, indisponibilidade do FFprobe e falha de rede;
- validação client-side somente como conveniência, mantendo `AudioValidator` como autoridade no servidor;
- substituição segura do áudio somente antes do início do processamento;
- novo arquivo é validado e persistido antes de o áudio anterior ser desativado;
- substituição é bloqueada se já houver histórico de jobs ou transcrição;
- ownership continua obrigatório em todos os endpoints;
- nenhum processamento de Whisper/Pyannote/LLM foi movido para a requisição HTTP.

## Fluxo

```text
Selecionar / arrastar arquivo
        ↓
validação preliminar no navegador
        ↓
upload com progresso
        ↓
staging limitado no servidor
        ↓
validação de nome/MIME/assinatura/tamanho
        ↓
FFprobe
        ↓
storage + banco
        ↓
AUDIO_UPLOADED
        ↓
processamento continua separado por jobs
```

## Substituição

A substituição é permitida apenas quando:

- existe um áudio ativo;
- a reunião ainda está em `AUDIO_UPLOADED`;
- ainda não existe transcrição;
- ainda não existe histórico de processamento.

A operação promove o novo arquivo primeiro e faz a troca de metadados dentro da transação. O arquivo antigo só é removido do storage após a persistência do novo áudio ser confirmada.

## Segurança

- nomes de caminhos internos não são retornados pela API;
- ownership é validado via `require_meeting_access`;
- arquivo continua passando por verificação de extensão, MIME, assinatura e FFprobe;
- upload interrompido não cria processamento;
- erro de ambiente não expõe stack trace;
- nenhuma migration foi necessária.

## Critérios de aceite

1. Interface informa formatos e tamanho máximo.
2. Drag & drop e seletor usam o mesmo pipeline seguro.
3. Progresso do upload é distinto do progresso dos jobs.
4. Arquivo inválido apresenta ação compreensível.
5. Upload interrompido pode ser tentado novamente.
6. Áudio pode ser substituído antes do processamento.
7. Substituição é recusada depois que processamento/transcrição começou.
8. O backend permanece a autoridade de validação.
9. Testes cobrem política, upload, conflito, substituição e formato inválido.
