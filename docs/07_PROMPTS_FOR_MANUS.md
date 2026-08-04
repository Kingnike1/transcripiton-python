# 07_PROMPTS_FOR_MANUS.md

## Prompts for Manus AI Agent

This document contains prompts and instructions for working with the Manus AI agent to continue development of the AMIP project.

### General Context Prompt

Use this prompt when starting a new session with Manus:

```
You are developing the AI Meeting Intelligence Platform (AMIP), a Python application 
for transcribing, analyzing, and archiving meetings.

The project is located at: /home/ubuntu/transcripiton-python

MANDATORY FIRST STEPS:
1. Read PROJECT_CONTEXT.md
2. Read PROJECT_GOVERNANCE.md
3. Read PROJECT_STATE.MD
4. Read docs/00_PROJECT_OVERVIEW.md
5. Read docs/01_ARCHITECTURE.md
6. Read docs/02_DATABASE.md
7. Read docs/03_API.md
8. Read docs/04_FRONTEND.md
9. Read docs/05_AI_PIPELINE.md
10. Read docs/06_BACKLOG.md

DEVELOPMENT PHILOSOPHY:
- Build a clean, modular monolithic application
- Choose simple solutions, avoid unnecessary complexity
- Application must run on 8GB+ RAM notebooks
- Keep code maintainable and easy to understand
- All code must have type hints and docstrings
- Minimum 80% test coverage required
- Documentation must stay synchronized with code

CURRENT PHASE: 1 - Foundation
NEXT TASKS:
- Complete environment configuration
- Set up database with SQLAlchemy
- Implement logging system
- Create basic FastAPI application
- Build basic UI with Bootstrap

After completing each task:
1. Run tests
2. Verify application starts correctly
3. Update documentation
4. Update PROJECT_STATE.MD
5. Register completed work
6. Suggest next logical step
```

### Phase-Specific Prompts

#### Phase 1: Foundation

```
Continue development of AMIP Phase 1: Foundation

Current Status: In Progress

Completed:
- Project structure created
- Documentation framework created

Next Tasks:
1. Create .env.example file with all required environment variables
2. Set up requirements.txt with all dependencies
3. Create app/__init__.py with application initialization
4. Create app/core/config.py with configuration management
5. Create app/core/logging.py with logging setup
6. Create app/database/session.py with database session management
7. Create app/database/base.py with SQLAlchemy base model
8. Create app/models/__init__.py
9. Create main.py with FastAPI application
10. Create basic HTML templates with Bootstrap

After each file created:
- Add type hints
- Add docstrings
- Create corresponding tests
- Update PROJECT_STATE.MD

Requirements:
- Python 3.12+
- FastAPI for web framework
- SQLAlchemy for ORM
- SQLite for database
- Bootstrap 5 for frontend
- pytest for testing
```

#### Phase 2: Meeting Management

```
Continue development of AMIP Phase 2: Meeting Management

Prerequisites: Phase 1 must be complete

Tasks:
1. Create app/models/meeting.py with Meeting model
2. Create app/schemas/meeting.py with Pydantic schemas
3. Create app/services/meeting_service.py with business logic
4. Create app/api/meetings.py with FastAPI routes
5. Create templates/meetings/list.html
6. Create templates/meetings/detail.html
7. Create templates/meetings/create.html
8. Create tests for meeting operations

Requirements:
- Meeting model with id, title, description, created_at, updated_at, deleted_at
- CRUD operations (Create, Read, Update, Delete)
- Soft delete support
- Full test coverage
```

#### Phase 3: Audio Module

```
Continue development of AMIP Phase 3: Audio Module

Prerequisites: Phase 2 must be complete

Tasks:
1. Create app/models/audio.py with Audio model
2. Create app/schemas/audio.py with Pydantic schemas
3. Create app/services/audio_service.py with file handling
4. Create app/api/audio.py with FastAPI routes
5. Create storage/ directory for audio files
6. Create templates/audio/upload.html
7. Create templates/audio/player.html
8. Create tests for audio operations

Requirements:
- Audio model with meeting_id, filename, file_path, duration, file_size, mime_type
- File upload handling
- Audio metadata extraction
- File storage management
- Support for mp3, wav, m4a formats
```

#### Phase 4: Transcription

```
Continue development of AMIP Phase 4: Transcription

Prerequisites: Phase 3 must be complete

Tasks:
1. Create app/models/transcription.py with Transcription model
2. Create app/schemas/transcription.py with Pydantic schemas
3. Create app/services/transcription_service.py with Whisper integration
4. Create app/api/transcription.py with FastAPI routes
5. Create templates/transcription/view.html
6. Create tests for transcription operations

Requirements:
- Transcription model with audio_id, text, language, created_at, updated_at
- Whisper API integration
- Chunk processing for large files
- Timestamp generation
- Language detection
- Background task support
```

#### Phase 5: Speaker Identification

```
Continue development of AMIP Phase 5: Speaker Identification

Prerequisites: Phase 4 must be complete

Tasks:
1. Create app/models/speaker.py with SpeakerSegment model
2. Create app/schemas/speaker.py with Pydantic schemas
3. Create app/services/speaker_service.py with pyannote integration
4. Create app/api/speaker.py with FastAPI routes
5. Create templates/transcription/speaker_segments.html
6. Create tests for speaker identification

Requirements:
- SpeakerSegment model with transcription_id, speaker_label, start_time, end_time, text, confidence
- pyannote.audio integration
- Speaker segmentation
- Speaker labeling
- Confidence scoring
```

#### Phase 6: AI Processing

```
Continue development of AMIP Phase 6: AI Processing

Prerequisites: Phase 5 must be complete

Tasks:
1. Create app/models/analysis.py with MeetingAnalysis model
2. Create app/schemas/analysis.py with Pydantic schemas
3. Create app/services/ai_service.py with AI provider abstraction
4. Create app/services/openai_provider.py with OpenAI integration
5. Create app/services/ollama_provider.py with Ollama integration
6. Create app/api/analysis.py with FastAPI routes
7. Create templates/analysis/summary.html
8. Create templates/analysis/action_items.html
9. Create tests for AI analysis

Requirements:
- MeetingAnalysis model with meeting_id, summary, action_items, decisions, risks, open_questions, follow_up_tasks
- AI provider abstraction (support OpenAI and Ollama)
- Summary generation
- Action items extraction
- Decision extraction
- Risk identification
- Open questions extraction
- Follow-up tasks generation
```

#### Phase 7: Search

```
Continue development of AMIP Phase 7: Search

Prerequisites: Phase 6 must be complete

Tasks:
1. Create app/services/search_service.py with full-text search
2. Create app/api/search.py with FastAPI routes
3. Create templates/search/search.html
4. Create templates/search/results.html
5. Create tests for search functionality

Requirements:
- Full-text search across meetings, transcriptions, analysis
- Search filters (date range, language, speaker)
- Relevance scoring
- Pagination
- Performance optimization with indexing
```

#### Phase 8: Export

```
Continue development of AMIP Phase 8: Export

Prerequisites: Phase 7 must be complete

Tasks:
1. Create app/services/export_service.py with export functionality
2. Create app/api/export.py with FastAPI routes
3. Create templates/export/export.html
4. Create export templates (markdown, pdf, txt, docx)
5. Create tests for export functionality

Requirements:
- Markdown export
- PDF export
- TXT export
- DOCX export
- Professional formatting
- Customizable templates
```

### Code Review Prompt

```
Review the following code for the AMIP project:

Checklist:
- [ ] Type hints present on all functions
- [ ] Docstrings on all public methods
- [ ] No business logic in routes
- [ ] No SQL in routes
- [ ] Proper error handling
- [ ] Tests included
- [ ] >80% code coverage
- [ ] Follows project naming conventions
- [ ] No code duplication
- [ ] Proper use of dependency injection

Code:
[CODE HERE]

Feedback:
```

### Documentation Update Prompt

```
Update the following documentation for AMIP:

Document: docs/XX_DOCUMENT.md
Changes Made: [DESCRIBE CHANGES]
New Features: [LIST NEW FEATURES]
Breaking Changes: [LIST BREAKING CHANGES]
Dependencies Added: [LIST NEW DEPENDENCIES]

Please update the documentation to reflect these changes and maintain consistency 
with the rest of the project documentation.
```

### Testing Prompt

```
Create comprehensive tests for the following component:

Component: [COMPONENT NAME]
Location: [FILE PATH]
Functionality: [DESCRIBE FUNCTIONALITY]

Requirements:
- Unit tests for all public methods
- Integration tests for critical paths
- Mocked external dependencies
- >80% code coverage
- Use pytest fixtures
- Clear test names and descriptions

Test file location: tests/test_[component].py
```

### Bug Fix Prompt

```
Fix the following bug in the AMIP project:

Bug Description: [DESCRIBE BUG]
Location: [FILE PATH]
Severity: [CRITICAL/HIGH/MEDIUM/LOW]
Steps to Reproduce: [STEPS]
Expected Behavior: [EXPECTED]
Actual Behavior: [ACTUAL]

Requirements:
- Fix the root cause
- Add tests to prevent regression
- Update documentation if needed
- Update PROJECT_STATE.MD
```

### Performance Optimization Prompt

```
Optimize the following component for performance:

Component: [COMPONENT NAME]
Location: [FILE PATH]
Current Performance: [DESCRIBE CURRENT PERFORMANCE]
Target Performance: [DESCRIBE TARGET]
Constraints: [LIST CONSTRAINTS]

Optimization Strategies:
- Database query optimization
- Caching implementation
- Async processing
- Chunking/pagination
- Index optimization

Requirements:
- Benchmark before and after
- Add performance tests
- Document optimization strategy
- Update PROJECT_STATE.MD
```

### Integration Prompt

```
Integrate [EXTERNAL_SERVICE] with the AMIP project:

Service: [SERVICE NAME]
Purpose: [PURPOSE]
API Documentation: [URL]
Authentication: [AUTH METHOD]
Rate Limits: [LIMITS]

Requirements:
- Create service wrapper in app/services/
- Add configuration in app/core/config.py
- Add error handling
- Add tests
- Add documentation
- Support provider switching if applicable
```

### Deployment Prompt

```
Prepare AMIP for deployment:

Target Environment: [DEVELOPMENT/STAGING/PRODUCTION]
Platform: [DOCKER/HEROKU/AWS/AZURE/OTHER]
Requirements:
- Dockerfile creation
- Environment configuration
- Database migration
- Static file handling
- Error logging
- Monitoring setup

Deliverables:
- Deployment guide
- Configuration templates
- Health check endpoints
- Rollback procedures
```

---

## Usage Guidelines

1. **Copy the relevant prompt** for your task
2. **Replace placeholders** with specific information
3. **Provide context** about the current state
4. **Be specific** about requirements
5. **Include examples** if helpful
6. **Ask for clarification** if needed

## Example Usage

```
[Copy Phase 1 Foundation Prompt]

Additional Context:
- Already have Python 3.12 installed
- Using SQLite for development
- Need Bootstrap 5 for styling
- Want HTMX for dynamic interactions

Please start with creating the .env.example file and requirements.txt
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
