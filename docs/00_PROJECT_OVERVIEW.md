# 00_PROJECT_OVERVIEW.md

## AI Meeting Intelligence Platform - Project Overview

### Executive Summary

The **AI Meeting Intelligence Platform (AMIP)** is a comprehensive, modular Python application designed to capture, transcribe, analyze, and archive meeting content. It combines modern AI technologies (Whisper, pyannote, GPT) with a clean, maintainable architecture to help organizations extract maximum value from their meetings.

### Project Objectives

1. **Capture**: Record or upload meeting audio seamlessly
2. **Transcribe**: Convert audio to accurate text with speaker identification
3. **Analyze**: Extract summaries, action items, decisions, and risks
4. **Archive**: Store meetings with full-text search capabilities
5. **Export**: Generate professional reports in multiple formats

### Key Features

| Feature | Capability | Status |
|---------|-----------|--------|
| **Meeting Management** | Create, edit, delete, organize meetings | Phase 2 |
| **Audio Capture** | Record from microphone or upload files | Phase 3 |
| **Transcription** | Convert audio to text with timestamps | Phase 4 |
| **Speaker ID** | Identify and label different speakers | Phase 5 |
| **AI Analysis** | Generate summaries, minutes, action items | Phase 6 |
| **Search** | Full-text search with advanced filters | Phase 7 |
| **Export** | Markdown, PDF, TXT, DOCX formats | Phase 8 |

### Technology Stack

#### Backend

```
Python 3.12+
├── FastAPI (web framework)
├── SQLAlchemy (ORM)
├── Pydantic (data validation)
├── Jinja2 (templates)
└── python-dotenv (configuration)
```

#### Frontend

```
HTML5 + Bootstrap 5
├── HTMX (dynamic interactions)
├── Vanilla JavaScript (minimal)
└── Server-side rendering
```

#### Database

```
SQLite (default)
└── Future: PostgreSQL
```

#### AI & ML

```
├── Whisper (transcription)
├── pyannote.audio (speaker identification)
├── OpenAI API (GPT models)
└── Ollama (local LLM alternative)
```

#### Testing & Quality

```
pytest (unit & integration tests)
```

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           Web Interface (Frontend)              │
│  HTML5 + Bootstrap 5 + HTMX + Vanilla JS        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         FastAPI Application (Backend)           │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐             │
│  │  API Routes  │  │  Services    │             │
│  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐             │
│  │  Database    │  │  AI Pipeline │             │
│  │  Layer       │  │  (Whisper,   │             │
│  │              │  │   pyannote)  │             │
│  └──────────────┘  └──────────────┘             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  SQLite Database + File Storage                 │
└─────────────────────────────────────────────────┘
```

### Development Phases

#### Phase 1: Foundation (Current)
- Project structure
- Environment setup
- Database initialization
- Logging system
- Configuration management
- Testing framework
- Basic FastAPI app
- Basic UI

#### Phase 2: Meeting Management
- Create meetings
- Edit meetings
- Delete meetings
- Meeting history

#### Phase 3: Audio Module
- Record audio
- Upload audio
- Store audio
- Audio metadata

#### Phase 4: Transcription
- Whisper integration
- Chunk processing
- Timestamp generation
- Language detection

#### Phase 5: Speaker Identification
- pyannote integration
- Speaker segmentation
- Speaker labeling

#### Phase 6: AI Processing
- Summaries
- Meeting minutes
- Action items
- Risks
- Decisions
- Open questions
- Follow-up tasks

#### Phase 7: Search
- Full-text search
- Filters
- Meeting history search

#### Phase 8: Export
- Markdown export
- PDF export
- TXT export
- DOCX export

### Project Structure

```
transcripiton-python/
├── app/
│   ├── __init__.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── meetings.py
│   │   ├── audio.py
│   │   └── search.py
│   ├── core/                # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── database/            # Database layer
│   │   ├── __init__.py
│   │   └── session.py
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── meeting.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   └── meeting.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── meeting_service.py
│   │   ├── audio_service.py
│   │   └── ai_service.py
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       └── meeting.html
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── storage/                 # Audio files storage
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_api.py
├── docs/                    # Documentation
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_ARCHITECTURE.md
│   ├── 02_DATABASE.md
│   ├── 03_API.md
│   ├── 04_FRONTEND.md
│   ├── 05_AI_PIPELINE.md
│   ├── 06_BACKLOG.md
│   ├── 07_PROMPTS_FOR_MANUS.md
│   ├── 08_DEPLOYMENT.md
│   └── 09_CONTRIBUTING.md
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── README.md                # Project README
├── PROJECT_CONTEXT.md       # Project context
├── PROJECT_GOVERNANCE.md    # Governance rules
└── PROJECT_STATE.MD         # Current state
```

### Development Workflow

1. **Read Documentation**: Understand context and architecture
2. **Plan Phase**: Define scope and tasks
3. **Implement**: Write code following guidelines
4. **Test**: Ensure >80% coverage
5. **Document**: Update relevant docs
6. **Review**: Verify quality and completeness
7. **Commit**: Push changes with descriptive messages
8. **Advance**: Move to next phase

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Simplicity** | Choose simple solutions, avoid unnecessary complexity |
| **Modularity** | Clear separation of concerns |
| **Maintainability** | Code easy to understand and modify |
| **Testability** | >80% code coverage required |
| **Documentation** | Keep docs synchronized with code |
| **Performance** | Run on common notebooks (8GB+ RAM) |
| **Extensibility** | Support multiple AI providers |

### Success Criteria

- ✅ Application runs on 8GB+ RAM systems
- ✅ All core features fully functional
- ✅ >80% code coverage
- ✅ Comprehensive documentation
- ✅ Multiple AI provider support
- ✅ Professional export formats
- ✅ Full-text search working
- ✅ Clean, maintainable codebase

### Getting Started

1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Configure `.env` file
5. Initialize database: `python main.py --init-db`
6. Run tests: `pytest`
7. Start application: `python main.py`
8. Visit `http://localhost:8000`

### Support & Documentation

- **Architecture**: See `docs/01_ARCHITECTURE.md`
- **Database**: See `docs/02_DATABASE.md`
- **API**: See `docs/03_API.md`
- **Frontend**: See `docs/04_FRONTEND.md`
- **AI Pipeline**: See `docs/05_AI_PIPELINE.md`
- **Deployment**: See `docs/08_DEPLOYMENT.md`
- **Contributing**: See `docs/09_CONTRIBUTING.md`

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
