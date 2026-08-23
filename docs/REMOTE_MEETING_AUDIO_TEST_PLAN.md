# Homologação — Captura de Áudio de Reunião Online

## Objetivo

Validar a funcionalidade implementada na branch `fix/remote-meeting-audio-capture` antes de qualquer merge para `develop`.

A gravação online deve preservar simultaneamente:

- voz do usuário local pelo microfone;
- áudio dos participantes remotos vindo da aba da reunião;
- fala simultânea local + remota;
- preview reproduzível antes do upload;
- compatibilidade com o pipeline existente de transcrição e diarização.

## Pré-condições

- Backend AMIP iniciado.
- Worker iniciado.
- Navegador atualizado.
- Microfone funcionando.
- Reunião Google Meet/Teams/Zoom Web aberta em uma aba separada.
- Branch local: `fix/remote-meeting-audio-capture`.
- Página recarregada sem cache após `git pull`.

## Cenário principal — Google Meet + fone USB

1. Entrar na reunião pelo computador de teste usando fone USB.
2. Criar/abrir uma reunião no AMIP.
3. Escolher `Online`.
4. Clicar em `Selecionar aba da reunião`.
5. Escolher especificamente a aba do Google Meet.
6. Habilitar compartilhamento de áudio no seletor do navegador.
7. Confirmar que a interface mostra `Áudio da reunião: Pronto`.
8. Iniciar a gravação e autorizar o microfone.
9. Confirmar os dois monitores de áudio.
10. Executar a sequência abaixo.

### Sequência de fala

- 0–5 s: apenas participante local fala.
- 5–10 s: apenas participante remoto fala.
- 10–15 s: ambos falam simultaneamente.
- 15–20 s: silêncio.

### Resultado esperado

Na prévia da gravação:

- voz local audível;
- voz remota audível;
- ambas presentes no trecho simultâneo;
- ausência de eco gerado pelo próprio AMIP;
- nenhuma dependência de Stereo Mix/Realtek/FxSound;
- áudio remoto continua presente mesmo com fone USB.

## Monitor de fontes

Durante a sequência principal:

- ao falar localmente, o medidor `Microfone` deve reagir;
- ao participante remoto falar, o medidor `Reunião online` deve reagir;
- quando ambos falarem, ambos devem reagir;
- silêncio deve mostrar nível baixo/estado de silêncio sem encerrar a gravação.

## Perda da aba compartilhada

Durante uma gravação online:

1. Encerrar manualmente o compartilhamento da aba.

Resultado esperado:

- AMIP detecta perda da fonte remota;
- gravação é encerrada automaticamente;
- usuário recebe aviso claro;
- trecho já gravado fica disponível para revisão;
- aplicação não continua gravando silenciosamente apenas o microfone.

## Perda do microfone

Durante uma gravação, desconectar ou interromper o microfone quando possível.

Resultado esperado:

- perda detectada;
- gravação encerrada;
- aviso claro;
- trecho parcial preservado para revisão.

## Aba sem áudio

1. Escolher modo Online.
2. Compartilhar uma fonte que não entregue track de áudio ou desmarcar compartilhamento de áudio.

Resultado esperado:

- início da gravação bloqueado;
- mensagem informa que não houve áudio compartilhado;
- nenhuma gravação online incompleta é iniciada.

## Permissões negadas

Validar separadamente:

- microfone negado;
- seleção de aba cancelada/negada.

Resultado esperado: mensagem clara, recursos liberados e possibilidade de tentar novamente.

## Modo presencial — regressão

Executar gravação usando `Presencial`.

Resultado esperado:

- apenas microfone é usado;
- seleção de aba não é solicitada;
- preview e upload continuam funcionando;
- mudanças de reunião online não quebram o fluxo anterior.

## Navegadores

Homologação mínima recomendada:

- Chrome atual no Windows;
- Edge atual no Windows.

Homologação adicional:

- Chrome/Chromium em Linux.

Se um navegador não retornar áudio em `getDisplayMedia`, a aplicação deve indicar incompatibilidade/ausência de áudio em vez de iniciar uma gravação inválida.

## Pipeline completo

Depois de aprovar a prévia:

1. `Usar gravação`.
2. Iniciar transcrição.
3. Confirmar `TRANSCRIBE: COMPLETED`.
4. Conferir se falas local e remota aparecem na transcrição.
5. Iniciar identificação de vozes.
6. Confirmar `DIARIZE: COMPLETED`.
7. Conferir identificação de mais de uma voz quando o material permitir.

## Gate para merge

A branch só deve ser considerada pronta para integração quando:

- testes automatizados passarem;
- modo Presencial não apresentar regressão;
- teste real Google Meet + fone USB capturar local e remoto;
- fala simultânea estiver presente na prévia;
- perda de uma fonte for detectada;
- transcrição completa funcionar;
- diarização completa funcionar;
- nenhum erro crítico aparecer no console do navegador/backend/worker.
