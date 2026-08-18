# ADR-031 — Meeting export formats

## Status
Accepted — Stack 16

## Context
O AMIP já concentra metadados, participantes, transcrição e inteligência estruturada de uma reunião. Esses dados precisam sair do sistema em formatos adequados tanto para leitura humana quanto para integração com outros softwares.

## Decision
A Stack 16 introduz um `ExportService` ownership-aware e um endpoint único `GET /api/meetings/{meeting_id}/export?format=...`.

Formatos suportados:

- `txt`: leitura simples e máxima portabilidade;
- `md`: documentação e uso em ferramentas de conhecimento;
- `json`: integração estruturada;
- `docx`: documento editável para uso corporativo;
- `pdf`: versão pronta para distribuição.

O exportador reúne metadados da reunião, participantes, transcrição/segmentos e análise. Dados ainda não produzidos não impedem a exportação: as seções permanecem válidas e indicam ausência de conteúdo.

A autorização é aplicada pela reunião-pai antes da montagem do documento. O endpoint retorna 404 para reuniões pertencentes a outro usuário, preservando a política da Stack 13.

## Consequences
- nenhum storage adicional é necessário para exports; os arquivos são gerados sob demanda em memória;
- não persistimos cópias redundantes de documentos gerados;
- DOCX e PDF adicionam dependências específicas de renderização;
- exportações muito grandes poderão futuramente migrar para geração assíncrona/streaming sem mudar o contrato funcional.
