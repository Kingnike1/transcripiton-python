"""
Providers package for AMIP.

This package contains implementations of AI and processing providers.
Each provider implements an interface defined in app/services/interfaces.py

Providers are organized by functionality:
- transcriber: Speech-to-text implementations (Whisper, etc.)
- speaker_identifier: Speaker diarization implementations (pyannote, etc.)
- summarizer: AI summarization implementations (OpenAI, Ollama, etc.)
- exporter: Export format implementations (Markdown, PDF, etc.)
- storage: Storage backend implementations (Local filesystem, S3, etc.)

All providers must implement their respective interfaces to ensure
interchangeability and testability.

Example:
    >>> from app.providers.transcriber import WhisperTranscriber
    >>> from app.services.pipeline_service import pipeline_service
    >>> 
    >>> transcriber = WhisperTranscriber()
    >>> pipeline_service.register_transcriber(transcriber)
"""
