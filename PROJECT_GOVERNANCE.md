# PROJECT_GOVERNANCE.md

## Project Governance & Development Guidelines

### Decision-Making Framework

#### Architecture Decisions

1. **Principle**: Always choose the simplest solution that solves the problem well
2. **Approach**: Monolithic application with clear module separation
3. **Review**: All architectural changes must be documented in `docs/01_ARCHITECTURE.md`
4. **Approval**: Changes affecting core structure require documentation update

#### Technology Stack Decisions

- **Backend**: Python 3.12+ with FastAPI
- **Frontend**: HTML5, Bootstrap 5, HTMX, Vanilla JavaScript
- **Database**: SQLite (default), PostgreSQL (future)
- **AI**: Whisper, pyannote.audio, OpenAI API, Ollama
- **Testing**: pytest
- **Infrastructure**: Native Python, Docker (optional)

**Rule**: Technology changes must be justified and documented before implementation.

### Development Workflow

#### Phase Completion Checklist

Before moving to the next phase, ensure:

- ✅ All code follows style guidelines
- ✅ Type hints are present on all functions
- ✅ Docstrings document all public methods
- ✅ Unit tests pass (>80% coverage)
- ✅ Application starts without errors
- ✅ Documentation is updated
- ✅ `PROJECT_STATE.MD` is updated
- ✅ Backlog is updated with next steps

#### Code Review Standards

1. **Type Safety**: All functions must have type hints
2. **Documentation**: Public methods must have docstrings
3. **Testing**: New features must include tests
4. **Naming**: Use clear, meaningful variable and function names
5. **Modularity**: Keep functions small and focused
6. **No Duplication**: Extract common logic into reusable functions
7. **Separation of Concerns**: No business logic in routes, no SQL in routes

#### Commit Message Format

```
[PHASE-N] Feature: Brief description

Detailed explanation of changes:
- Change 1
- Change 2

Related to: docs/XX_DOCUMENT.md
```

### Code Organization Rules

#### Backend Rules

- **Type Hints**: Required on all functions
- **Docstrings**: Required for all public methods
- **Function Size**: Keep functions small and focused
- **Naming**: Use clear, descriptive names
- **Dependency Injection**: Use when appropriate
- **No Duplication**: Extract common patterns
- **No Business Logic in Routes**: Use services layer
- **No SQL in Routes**: Use database layer

#### Frontend Rules

- **Server-Side Rendering**: Preferred over SPA
- **Bootstrap**: Use for styling
- **HTMX**: Use for dynamic interactions
- **JavaScript**: Keep minimal, vanilla only
- **Usability**: Focus on functionality over visual effects
- **Accessibility**: Ensure keyboard navigation works

#### Database Rules

- **ORM**: Use SQLAlchemy
- **Migrations**: Use Alembic
- **Soft Delete**: Prefer soft delete over hard delete
- **Data Integrity**: Never delete data automatically
- **Constraints**: Define at database level

### AI Provider Integration Rules

#### Interchangeability

All AI providers must be interchangeable:

1. **OpenAI**: Primary provider
2. **Ollama**: Local/alternative provider
3. **Future Providers**: Should not require core changes

#### Implementation Pattern

```python
class AIProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass

    @abstractmethod
    def summarize(self, text: str) -> str:
        pass
```

#### Configuration

- Never hardcode API keys
- Use environment variables via `.env`
- Support provider switching via configuration

### Documentation Standards

#### When to Update Documentation

1. **After implementing a feature**: Update relevant docs/ file
2. **After architectural decision**: Document in `docs/01_ARCHITECTURE.md`
3. **After database schema change**: Update `docs/02_DATABASE.md`
4. **After API change**: Update `docs/03_API.md`
5. **After UI change**: Update `docs/04_FRONTEND.md`
6. **After AI pipeline change**: Update `docs/05_AI_PIPELINE.md`

#### Documentation Structure

- **Markdown Format**: All documentation in Markdown
- **Clear Sections**: Use headers for organization
- **Examples**: Include code examples where relevant
- **Diagrams**: Use ASCII art or Mermaid for complex concepts
- **Links**: Cross-reference related documents

### Testing Standards

#### Test Coverage

- Minimum 80% code coverage
- All public methods should have tests
- Integration tests for critical paths
- No test duplication

#### Test Organization

```
tests/
  test_models.py
  test_services.py
  test_api.py
  test_database.py
  conftest.py
```

#### Running Tests

```bash
pytest --cov=app tests/
```

### Performance Requirements

#### Target Systems

- **8 GB RAM notebooks**: Minimum supported
- **16 GB RAM notebooks**: Recommended
- **High-end workstations**: Optimal

#### Performance Guidelines

- Heavy tasks run in background
- UI remains responsive during processing
- Database queries optimized
- Memory usage monitored

### Release & Deployment

#### Version Numbering

- **Major.Minor.Patch** format (e.g., 1.0.0)
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

#### Deployment Checklist

- ✅ All tests passing
- ✅ Documentation updated
- ✅ Version number updated
- ✅ Changelog updated
- ✅ Docker image built (if applicable)
- ✅ Deployment verified

### Communication & Escalation

#### Status Updates

- Document progress in `PROJECT_STATE.MD`
- Update backlog with completed items
- Flag blockers immediately

#### Escalation Path

1. **Technical Issues**: Document in issue tracker
2. **Architectural Concerns**: Discuss and document decision
3. **Timeline Issues**: Update project timeline

### Roles & Responsibilities

| Role | Responsibilities |
|------|-----------------|
| **Developer** | Implement features, write tests, update docs |
| **Architect** | Review design, approve major changes |
| **QA** | Test features, verify requirements |
| **Product Owner** | Prioritize features, approve releases |

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
