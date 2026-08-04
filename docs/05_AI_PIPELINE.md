# 05_AI_PIPELINE.md

## AI Pipeline Architecture

### Overview

The AI Pipeline processes audio files through multiple stages to extract meeting intelligence:

```
Audio File
    ↓
[Transcription] (Whisper)
    ↓
[Speaker Identification] (pyannote)
    ↓
[AI Analysis] (OpenAI/Ollama)
    ↓
Meeting Intelligence
```

### Pipeline Stages

#### Stage 1: Transcription

**Tool**: OpenAI Whisper  
**Purpose**: Convert audio to text with timestamps

**Process**:
1. Load audio file
2. Split into chunks (if > 25MB)
3. Send to Whisper API
4. Receive transcribed text with timestamps
5. Store in database

**Configuration**:
```python
# app/core/config.py
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
WHISPER_LANGUAGE = "auto"  # auto-detect or specify
CHUNK_SIZE = 25 * 1024 * 1024  # 25MB chunks
```

**Example**:
```python
from app.services.transcription_service import TranscriptionService

service = TranscriptionService()
result = await service.transcribe(
    audio_path="/path/to/audio.mp3",
    language="pt"
)
# Returns: {"text": "...", "language": "pt", "segments": [...]}
```

**Output**:
```json
{
  "text": "Full transcribed text...",
  "language": "pt",
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 5.5,
      "text": "Bom dia a todos.",
      "avg_logprob": -0.25
    }
  ]
}
```

#### Stage 2: Speaker Identification

**Tool**: pyannote.audio  
**Purpose**: Identify and segment different speakers

**Process**:
1. Load transcription
2. Load audio file
3. Run speaker diarization
4. Assign speaker labels
5. Segment transcription by speaker
6. Store in database

**Configuration**:
```python
# app/core/config.py
PYANNOTE_MODEL = "pyannote/speaker-diarization-3.1"
PYANNOTE_DEVICE = "cpu"  # or "cuda" for GPU
SPEAKER_THRESHOLD = 0.5
```

**Example**:
```python
from app.services.speaker_service import SpeakerService

service = SpeakerService()
segments = await service.identify_speakers(
    audio_path="/path/to/audio.mp3",
    transcription_text="..."
)
# Returns: [{"speaker": "Speaker 1", "start": 0.0, "end": 5.5, "text": "..."}]
```

**Output**:
```json
[
  {
    "speaker": "Speaker 1",
    "start": 0.0,
    "end": 5.5,
    "text": "Bom dia a todos.",
    "confidence": 0.92
  },
  {
    "speaker": "Speaker 2",
    "start": 5.5,
    "end": 12.3,
    "text": "Obrigado por vir.",
    "confidence": 0.88
  }
]
```

#### Stage 3: AI Analysis

**Tool**: OpenAI GPT or Ollama  
**Purpose**: Extract insights from transcription

**Supported Analyses**:
1. **Summary**: Concise overview of meeting
2. **Action Items**: Tasks to be completed
3. **Decisions**: Decisions made
4. **Risks**: Identified risks
5. **Open Questions**: Unresolved questions
6. **Follow-up Tasks**: Tasks for follow-up

**Configuration**:
```python
# app/core/config.py
AI_PROVIDER = "openai"  # or "ollama"
OPENAI_MODEL = "gpt-4"
OPENAI_API_KEY = "sk-..."
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"
```

**Example**:
```python
from app.services.ai_service import AIService

service = AIService()
analysis = await service.analyze_meeting(
    transcription_text="...",
    speaker_segments=[...]
)
# Returns: {"summary": "...", "action_items": [...], ...}
```

**Output**:
```json
{
  "summary": "A reunião discutiu objetivos do Q3 e alocação de recursos...",
  "action_items": [
    "Completar proposta do projeto até sexta",
    "Agendar reunião de acompanhamento com stakeholders",
    "Revisar alocação de orçamento"
  ],
  "decisions": [
    "Aprovado aumento de orçamento para Q3",
    "Decidido contratar 2 membros adicionais para o time"
  ],
  "risks": [
    "Timeline pode ser apertada para entrega do projeto",
    "Restrições de recursos no Q4"
  ],
  "open_questions": [
    "Como lidaremos com conflitos de recursos?",
    "Qual é o plano de contingência se a timeline atrasar?"
  ],
  "follow_up_tasks": [
    "Enviar ata da reunião para todos os participantes",
    "Atualizar timeline do projeto no sistema"
  ]
}
```

### AI Provider Abstraction

**Strategy**: Support multiple AI providers with same interface

```python
# app/services/ai_service.py
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass
    
    @abstractmethod
    async def extract_action_items(self, text: str) -> List[str]:
        pass
    
    @abstractmethod
    async def extract_decisions(self, text: str) -> List[str]:
        pass

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def summarize(self, text: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a meeting analyst."},
                {"role": "user", "content": f"Summarize this meeting:\n\n{text}"}
            ]
        )
        return response.choices[0].message.content

class OllamaProvider(AIProvider):
    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model
    
    async def summarize(self, text: str) -> str:
        response = await httpx.post(
            f"{self.url}/api/generate",
            json={
                "model": self.model,
                "prompt": f"Summarize this meeting:\n\n{text}",
                "stream": False
            }
        )
        return response.json()["response"]
```

### Prompts for AI Analysis

#### Summary Prompt

```
You are an expert meeting analyst. Analyze the following meeting transcription and provide a concise summary (2-3 paragraphs) of the key points discussed.

Meeting Transcription:
{transcription}

Summary:
```

#### Action Items Prompt

```
You are an expert meeting analyst. Extract all action items from the following meeting transcription. List each action item as a separate bullet point.

Meeting Transcription:
{transcription}

Action Items:
```

#### Decisions Prompt

```
You are an expert meeting analyst. Extract all decisions made during the following meeting. List each decision as a separate bullet point.

Meeting Transcription:
{transcription}

Decisions:
```

#### Risks Prompt

```
You are an expert meeting analyst. Identify any risks or concerns mentioned in the following meeting. List each risk as a separate bullet point.

Meeting Transcription:
{transcription}

Risks:
```

### Processing Pipeline

#### Synchronous Processing

```python
# For small files (< 5 minutes)
async def process_meeting_sync(meeting_id: int):
    meeting = db.get_meeting(meeting_id)
    audio = meeting.audios[0]
    
    # Transcribe
    transcription = await transcribe(audio.file_path)
    db.save_transcription(audio.id, transcription)
    
    # Identify speakers
    speakers = await identify_speakers(audio.file_path, transcription)
    db.save_speaker_segments(transcription.id, speakers)
    
    # Analyze
    analysis = await analyze_meeting(transcription.text)
    db.save_analysis(meeting.id, analysis)
```

#### Asynchronous Processing

```python
# For large files (> 5 minutes)
# Use background tasks or message queue

from celery import shared_task

@shared_task
def process_meeting_async(meeting_id: int):
    meeting = db.get_meeting(meeting_id)
    audio = meeting.audios[0]
    
    try:
        # Transcribe
        transcription = await transcribe(audio.file_path)
        db.save_transcription(audio.id, transcription)
        
        # Identify speakers
        speakers = await identify_speakers(audio.file_path, transcription)
        db.save_speaker_segments(transcription.id, speakers)
        
        # Analyze
        analysis = await analyze_meeting(transcription.text)
        db.save_analysis(meeting.id, analysis)
        
        # Update status
        db.update_meeting_status(meeting.id, "completed")
    except Exception as e:
        db.update_meeting_status(meeting.id, "failed")
        logger.error(f"Processing failed: {e}")
```

### Error Handling

```python
class TranscriptionError(Exception):
    """Raised when transcription fails."""
    pass

class SpeakerIdentificationError(Exception):
    """Raised when speaker identification fails."""
    pass

class AIAnalysisError(Exception):
    """Raised when AI analysis fails."""
    pass

# Usage
try:
    transcription = await transcribe(audio_path)
except TranscriptionError as e:
    logger.error(f"Transcription failed: {e}")
    raise
```

### Performance Optimization

#### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_analysis_cached(text_hash: str):
    """Cache analysis results to avoid re-processing."""
    return await analyze_meeting(text_hash)
```

#### Chunking

```python
def chunk_audio(file_path: str, chunk_size: int = 25 * 1024 * 1024):
    """Split large audio files into chunks."""
    chunks = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks
```

#### Parallel Processing

```python
import asyncio

async def process_chunks_parallel(chunks: List[bytes]):
    """Process multiple chunks in parallel."""
    tasks = [transcribe_chunk(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    return results
```

### Monitoring & Logging

```python
import logging

logger = logging.getLogger(__name__)

async def process_meeting_with_logging(meeting_id: int):
    logger.info(f"Starting processing for meeting {meeting_id}")
    
    try:
        logger.debug("Transcribing audio...")
        transcription = await transcribe(audio_path)
        logger.info(f"Transcription completed: {len(transcription)} chars")
        
        logger.debug("Identifying speakers...")
        speakers = await identify_speakers(audio_path, transcription)
        logger.info(f"Found {len(speakers)} speaker segments")
        
        logger.debug("Analyzing meeting...")
        analysis = await analyze_meeting(transcription)
        logger.info(f"Analysis completed")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
```

### Configuration Management

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    # Transcription
    WHISPER_MODEL: str = "base"
    WHISPER_LANGUAGE: str = "auto"
    
    # Speaker Identification
    PYANNOTE_MODEL: str = "pyannote/speaker-diarization-3.1"
    PYANNOTE_DEVICE: str = "cpu"
    
    # AI Provider
    AI_PROVIDER: str = "openai"  # or "ollama"
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    class Config:
        env_file = ".env"
```

### Future Enhancements

1. **Real-time Transcription**: Stream audio for live transcription
2. **Speaker Names**: Map speaker labels to actual names
3. **Sentiment Analysis**: Analyze sentiment of meeting
4. **Key Topics**: Extract main topics discussed
5. **Follow-up Tracking**: Track completion of action items
6. **Meeting Recommendations**: Suggest improvements for future meetings

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
