# Sprint Futura — Hardening do Runtime de Áudio e Diarização

## Contexto

Durante testes locais no Windows, a transcrição foi concluída normalmente, porém a diarização falhou em aproximadamente 5% com `DIARIZE: FAILED` e `Could not load libtorchcodec`.

No ambiente analisado havia Windows, PyTorch 2.13.0+cpu, TorchCodec 0.16.0, pyannote.audio 4.0.7 e FFmpeg 9 inicialmente instalado como build estática. Posteriormente foi instalado FFmpeg 9.0.1 `full_build-shared`.

Após registrar manualmente no processo Python a pasta `bin` do FFmpeg Shared por `os.add_dll_directory(...)`, `import torchcodec` passou e retornou `TORCHCODEC OK`. Isso confirmou que a causa imediata era descoberta/carregamento das bibliotecas nativas do FFmpeg.

## Objetivo

Tornar o runtime de áudio e diarização robusto e previsível em Windows, Linux e Docker, sem caminhos específicos de uma máquina e com diagnóstico antes de uma diarização real.

## Problemas identificados

### 1. FFmpeg executável não garante compatibilidade com TorchCodec

`ffmpeg -version` pode funcionar enquanto o TorchCodec falha. O TorchCodec precisa carregar bibliotecas compartilhadas (`.dll` no Windows e `.so` no Linux), portanto detectar apenas o executável no PATH é insuficiente.

### 2. Build estática no Windows

Foi encontrado FFmpeg com `--enable-static`. A CLI funcionava, mas não fornecia as DLLs necessárias ao TorchCodec. Foi necessária uma build Shared.

### 3. Múltiplas instalações e aliases

Depois da instalação do FFmpeg Shared pelo WinGet, o comando `ffmpeg` ainda podia apontar para a instalação anterior. Não devemos depender exclusivamente do PATH.

### 4. Dependências de ML parcialmente transitivas

PyTorch e TorchCodec podem ser resolvidos transitivamente. A Sprint deverá definir/documentar uma matriz homologada de Python, PyTorch, TorchCodec, pyannote.audio, faster-whisper e FFmpeg.

### 5. Ausência de preflight

A diarização pode ser anunciada como disponível mesmo quando bibliotecas nativas não carregam. O runtime precisa ser validado antes de aceitar trabalho de diarização.

### 6. Erros pouco específicos

Diferenciar FFmpeg ausente, shared libraries ausentes, Torch/TorchCodec incompatíveis, CUDA, modelo/token Pyannote e áudio inválido.

## Arquitetura proposta

Criar uma camada de runtime de mídia, por exemplo:

```text
app/
├── infrastructure/
│   └── media_runtime.py
├── exceptions/
│   └── media.py
├── providers/
│   └── speaker_identifier/
│       └── pyannote.py
└── config/
    └── audio.py
```

Fluxo:

```text
Worker inicia
  ↓
Media Runtime Preflight
  ↓
Detectar SO
  ↓
Localizar FFmpeg
  ↓
Validar bibliotecas nativas
  ↓
Validar PyTorch
  ↓
Validar TorchCodec
  ↓
Validar Pyannote
  ↓
Diarização disponível
```

Se houver falha, o worker deve continuar funcionando quando possível, mas marcar diarização como indisponível com diagnóstico claro.

## Windows

1. Permitir configuração explícita opcional, por exemplo `FFMPEG_BIN_DIR`.
2. Sem configuração, fazer auto-discovery em PATH, WinGet, Chocolatey, Scoop e locais conhecidos.
3. Validar não apenas `ffmpeg.exe`, mas as DLLs compartilhadas esperadas.
4. Antes de importar TorchCodec/Pyannote, usar `os.add_dll_directory(ffmpeg_bin_dir)` e manter o handle vivo durante o processo.
5. Nunca persistir caminhos específicos como `C:\Users\3A\...`.

## Linux

1. Detectar `ffmpeg` e validar sua execução.
2. Validar carregamento real do TorchCodec e das bibliotecas `.so`.
3. Não usar `os.add_dll_directory`.
4. Preservar Docker como ambiente homologado quando aplicável.

O teste definitivo deve ser funcional (`import torchcodec`), não apenas `ffmpeg -version`.

## Preflight funcional

Validar efetivamente os componentes, conceitualmente:

```python
import torch
import torchcodec
from pyannote.audio import Pipeline
```

Produzir diagnóstico estruturado, por exemplo:

```json
{
  "ffmpeg": "ok",
  "torch": "ok",
  "torchcodec": "ok",
  "pyannote": "ok",
  "diarization": "available"
}
```

Em falha, retornar motivo específico como `FFMPEG_SHARED_LIBRARIES_NOT_FOUND`.

## Exceções específicas

Considerar:

```text
MediaRuntimeUnavailable
FFmpegNotFound
FFmpegSharedLibrariesNotFound
TorchCodecUnavailable
TorchRuntimeUnavailable
PyannoteUnavailable
ModelUnavailable
AudioDecodeError
```

## Normalização central de áudio

Como evolução, reduzir a dependência do decoder interno do Pyannote:

```text
Áudio de entrada
  ↓
Audio Normalizer
  ↓
FFmpeg controlado pelo Transcripition
  ↓
PCM/WAV mono 16 kHz
  ↓
 ┌────┴────┐
 ↓         ↓
Whisper  Pyannote
```

Quando suportado, avaliar entregar ao Pyannote waveform + sample rate diretamente.

## Dependências homologadas

Avaliar `requirements-ml.txt` ou mecanismo equivalente para definir combinação oficialmente testada de Python, PyTorch, TorchCodec, pyannote.audio, faster-whisper e FFmpeg.

## Cenários de teste

| Cenário | Resultado esperado |
|---|---|
| Windows sem FFmpeg | Diarização indisponível com erro claro |
| Windows + FFmpeg static | Detectar incompatibilidade |
| Windows + FFmpeg shared | Carregamento bem-sucedido |
| Windows com múltiplos FFmpeg | Selecionar instalação válida |
| Windows com PATH incorreto | Auto-discovery/configuração resolve |
| Linux sem FFmpeg | Preflight falha claramente |
| Linux com FFmpeg válido | Diarização disponível |
| Docker Worker | Preflight verde |
| TorchCodec incompatível | Bloquear diarização com diagnóstico |
| PyTorch incompatível | Bloquear diarização com diagnóstico |
| Modelo Pyannote inacessível | Erro específico de modelo/token |
| Áudio inválido | AudioDecodeError |
| CPU | Diarização funcional |
| CUDA inválido | Fallback CPU ou diagnóstico claro |
| FFmpeg futuro | Capability test decide compatibilidade |

## Critérios de aceite

1. Nenhum caminho de FFmpeg específico de máquina no código.
2. Windows registra automaticamente bibliotecas Shared válidas.
3. Linux continua funcionando sem lógica Windows.
4. Docker Worker passa no preflight.
5. TorchCodec é testado funcionalmente.
6. Diarização só é anunciada como disponível com runtime operacional.
7. Erros de dependência são diferenciados de modelo/áudio.
8. Testes unitários para discovery e preflight.
9. Teste real de diarização em Windows.
10. Teste real de diarização em Linux/Docker.
11. Documentação de instalação atualizada.
12. Matriz de dependências homologadas documentada.

## Arquivos prováveis

```text
app/infrastructure/media_runtime.py
app/exceptions/media.py
app/providers/speaker_identifier/pyannote.py
app/config/audio.py
requirements-worker.txt
.env.example
Dockerfile
docs/08_DEPLOYMENT.md
tests/test_media_runtime.py
```

## Prioridade

Sprint de hardening do Worker recomendada antes de considerar a pipeline de diarização pronta para distribuição em múltiplas máquinas.

## Resultado esperado

```text
Windows local ✅
Linux local ✅
Docker ✅
FFmpeg runtime validado ✅
Torch/TorchCodec validados ✅
Pyannote validado ✅
Erros diagnosticáveis ✅
Diarização portátil ✅
```

A arquitetura deixa de depender de configuração implícita do sistema operacional e passa a tratar o runtime de áudio como infraestrutura explícita do Transcripition.
