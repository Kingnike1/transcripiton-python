# 01_ARCHITECTURE.md

## System Architecture

### Architectural Philosophy

The AMIP follows a **clean monolithic architecture** with clear separation of concerns:

- **Single deployable unit**: One application, not microservices
- **Layered design**: Presentation → API → Services → Database
- **Dependency injection**: Loose coupling between components
- **Testable**: Each layer can be tested independently
- **Maintainable**: Easy to understand and modify

### High-Level Architecture

```
┌──────────────────────────────────────────────────────┐
│              Presentation Layer                      │
│  (HTML/Bootstrap/HTMX/Vanilla JS)                    │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP
┌────────────────────▼─────────────────────────────────┐
│              API Layer (FastAPI)                     │
│  ├── Meeting Routes                                  │
│  ├── Audio Routes                                    │
│  ├── Search Routes                                   │
│  └── Export Routes                                   │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              Service Layer                           │
│  ├── Meeting Service                                 │
│  ├── Audio Service                                   │
│  ├── Transcription Service                           │
│  ├── Speaker ID Service                              │
│  ├── AI Service                                      │
│  └── Search Service                                  │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              Data Layer                              │
│  ├── Database Session                                │
│  ├── Models (SQLAlchemy)                             │
│  └── Repositories                                    │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              External Services                       │
│  ├── Whisper (Transcription)                         │
│  ├── pyannote (Speaker ID)                           │
│  ├── OpenAI API (Summaries, Analysis)                │
│  └── Ollama (Local LLM)                              │
└──────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Presentation Layer

**Responsibility**: Render user interface

**Components**:
- HTML templates (Jinja2)
- Bootstrap CSS framework
- HTMX for dynamic updates
- Vanilla JavaScript for interactions

**Rules**:
- Server-side rendering preferred
- No business logic
- Minimal JavaScript
- Accessibility first

#### API Layer (FastAPI)

**Responsibility**: Handle HTTP requests and route to services

**Components**:
- Route handlers
- Request/response validation (Pydantic)
- Error handling
- Authentication/authorization

**Rules**:
- No business logic in routes
- No database queries in routes
- Use dependency injection
- Validate all inputs
- Return appropriate status codes

**Example Route**:
```python
@router.post("/meetings")
async def create_meeting(
    request: CreateMeetingRequest,
    service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Create a new meeting."""
    meeting = await service.create(request)
    return MeetingResponse.from_model(meeting)
```

#### Service Layer

**Responsibility**: Implement business logic

**Components**:
- Meeting service
- Audio service
- Transcription service
- Speaker identification service
- AI analysis service
- Search service

**Rules**:
- All business logic lives here
- Use dependency injection
- No HTTP details
- Testable in isolation
- Handle errors gracefully

**Example Service**:
```python
class MeetingService:
    def __init__(self, db: Session, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service
    
    async def create(self, request: CreateMeetingRequest) -> Meeting:
        """Create a new meeting."""
        meeting = Meeting(**request.dict())
        self.db.add(meeting)
        self.db.commit()
        return meeting
```

#### Data Layer

**Responsibility**: Manage data persistence

**Components**:
- SQLAlchemy ORM models
- Database session management
- Query builders
- Migrations (Alembic)

**Rules**:
- Use ORM, not raw SQL
- Define constraints at database level
- Use migrations for schema changes
- Implement soft deletes where appropriate

**Example Model**:
```python
class Meeting(Base):
    __tablename__ = "meetings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

#### External Services Layer

**Responsibility**: Integrate with external AI/ML services

**Components**:
- Whisper integration
- pyannote integration
- OpenAI API client
- Ollama client

**Rules**:
- Abstract behind interfaces
- Support multiple providers
- Handle rate limiting
- Implement retry logic
- Cache results when appropriate

### Module Organization

```
app/
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # Dependency injection
│   ├── meetings.py          # Meeting routes
│   ├── audio.py             # Audio routes
│   ├── search.py            # Search routes
│   └── export.py            # Export routes
│
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── logging.py           # Logging setup
│   ├── enums.py             # ProcessingStatus, JobStatus, JobType
│   └── exceptions.py        # Custom exceptions
│
├── database/
│   ├── __init__.py
│   ├── session.py           # DB session
│   ├── base.py              # Base model
│   ├── repository.py        # BaseRepository ABC
│   ├── meeting_repository.py # MeetingRepository
│   └── migrations/          # Alembic migrations
│
├── models/
│   ├── __init__.py
│   ├── meeting.py           # Meeting model
│   ├── audio.py             # Audio model
│   ├── transcription.py     # Transcription model
│   └── speaker.py           # Speaker model
│
├── schemas/
│   ├── __init__.py
│   ├── meeting.py           # Meeting schemas
│   ├── audio.py             # Audio schemas
│   └── search.py            # Search schemas
│
├── services/
│   ├── __init__.py
│   ├── meeting_service.py   # Meeting logic
│   ├── processing_service.py # Pipeline orchestration & status
│   ├── pipeline_service.py  # Pipeline execution
│   ├── interfaces.py        # ITranscriber, ISpeakerIdentifier, IAISummarizer, IExporter
│   ├── storage_service.py   # File management
│   ├── job_service.py       # Async job queue
│   ├── audio_service.py     # Audio logic
│   ├── search_service.py    # Search logic
│   └── export_service.py    # Export logic
│
└── templates/
    ├── base.html            # Base template
    ├── index.html           # Home page
    ├── meetings/
    │   ├── list.html
    │   ├── detail.html
    │   └── create.html
    └── components/
        ├── navbar.html
        └── footer.html
```

### Data Flow

#### Meeting Creation Flow

```
1. User submits form
   ↓
2. POST /api/meetings
   ↓
3. FastAPI validates request (Pydantic)
   ↓
4. Route calls MeetingService.create()
   ↓
5. Service creates Meeting model
   ↓
6. Service saves to database
   ↓
7. Service returns Meeting object
   ↓
8. Route returns JSON response
   ↓
9. Frontend updates UI
```

#### Transcription Flow

```
1. User uploads audio
   ↓
2. POST /api/audio/upload
   ↓
3. AudioService saves file to storage
   ↓
4. AudioService creates Audio record
   ↓
5. Background task starts transcription
   ↓
6. TranscriptionService calls Whisper
   ↓
7. Whisper returns transcribed text
   ↓
8. TranscriptionService saves to database
   ↓
9. Frontend polls for completion
   ↓
10. Frontend displays transcription
```

#### AI Analysis Flow

```
1. Transcription complete
   ↓
2. Background task starts AI analysis
   ↓
3. AIService calls OpenAI/Ollama
   ↓
4. AI returns summary, action items, etc.
   ↓
5. AIService saves results to database
   ↓
6. Frontend displays analysis
```

### Dependency Injection

**Pattern**: Constructor injection with FastAPI Depends

```python
# Define dependency
def get_meeting_service(db: Session = Depends(get_db)) -> MeetingService:
    return MeetingService(db)

# Use in route
@router.get("/meetings/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    meeting = service.get(meeting_id)
    return MeetingResponse.from_model(meeting)
```

### Error Handling

**Strategy**: Consistent error responses

```python
class APIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(APIException)
async def api_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### Configuration Management

**Strategy**: Environment variables with defaults

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    OPENAI_API_KEY: str
    OLLAMA_URL: str = "http://localhost:11434"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Testing Architecture

**Strategy**: Test each layer independently

```
tests/
├── test_models.py           # Model tests
├── test_services.py         # Service tests (mocked DB)
├── test_api.py              # API tests (mocked services)
├── test_database.py         # Database tests
└── conftest.py              # Fixtures
```

### Performance Considerations

1. **Database Indexing**: Index frequently searched columns
2. **Query Optimization**: Use eager loading for related data
3. **Caching**: Cache AI results to avoid re-processing
4. **Background Tasks**: Heavy operations run asynchronously
5. **Pagination**: Limit results in list endpoints

### Security Considerations

1. **Input Validation**: Validate all user inputs
2. **SQL Injection**: Use ORM, never raw SQL
3. **Authentication**: Implement user authentication
4. **Authorization**: Check permissions before operations
5. **API Keys**: Never hardcode, use environment variables
6. **CORS**: Configure appropriately for frontend

### Scalability Considerations

**Current**: Single-server monolithic application

**Future**: Consider when scaling needed:
- Database: Migrate to PostgreSQL
- Caching: Add Redis for session/result caching
- Task Queue: Add Celery for background jobs
- Load Balancing: Add reverse proxy (nginx)
- Monitoring: Add logging and metrics

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
