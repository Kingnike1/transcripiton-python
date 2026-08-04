# 09_CONTRIBUTING.md

## Contributing Guidelines

### Welcome!

Thank you for your interest in contributing to the AI Meeting Intelligence Platform (AMIP). This document provides guidelines for contributing to the project.

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. We expect all contributors to:

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Respect others' time and effort

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing opinions
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- Virtual environment (venv or conda)
- Familiarity with FastAPI and SQLAlchemy

### Development Setup

```bash
# Clone repository
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Initialize database
python main.py --init-db

# Run tests
pytest

# Start development server
python main.py
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-name
```

### 2. Make Changes

- Follow coding standards (see below)
- Write tests for new features
- Update documentation
- Keep commits small and focused

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "[PHASE-N] Feature: Brief description

Detailed explanation of changes:
- Change 1
- Change 2

Related to: docs/XX_DOCUMENT.md"
```

### 4. Push and Create Pull Request

```bash
# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill in PR template with:
# - Description of changes
# - Related issues
# - Testing performed
# - Screenshots (if applicable)
```

### 5. Code Review

- Address review comments
- Update code as needed
- Re-request review when ready

### 6. Merge

- Ensure all checks pass
- Squash commits if needed
- Merge to main branch

---

## Coding Standards

### Python Style

Follow PEP 8 with these guidelines:

```python
# Type hints required
def create_meeting(title: str, description: str) -> Meeting:
    """Create a new meeting.
    
    Args:
        title: Meeting title
        description: Meeting description
    
    Returns:
        Created Meeting object
    """
    pass
```

### Code Organization

```python
# Imports (organized)
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import Meeting
from app.schemas import MeetingCreate
from app.services import MeetingService

# Constants
DEFAULT_LIMIT = 10

# Classes/Functions
class MeetingAPI:
    pass

async def get_meetings() -> List[Meeting]:
    pass
```

### Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Functions | snake_case | `create_meeting()` |
| Classes | PascalCase | `MeetingService` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_LIMIT` |
| Variables | snake_case | `meeting_id` |
| Private | _leading_underscore | `_internal_method()` |

### Docstring Format

```python
def process_audio(audio_path: str, language: str = "auto") -> dict:
    """Process audio file for transcription.
    
    Transcribes audio using Whisper and identifies speakers.
    
    Args:
        audio_path: Path to audio file
        language: Language code (default: auto-detect)
    
    Returns:
        Dictionary containing:
        - text: Transcribed text
        - language: Detected language
        - segments: List of transcription segments
    
    Raises:
        FileNotFoundError: If audio file not found
        TranscriptionError: If transcription fails
    
    Example:
        >>> result = process_audio("meeting.mp3")
        >>> print(result["text"])
    """
    pass
```

### Error Handling

```python
# Define custom exceptions
class TranscriptionError(Exception):
    """Raised when transcription fails."""
    pass

# Use in code
try:
    result = transcribe(audio_path)
except TranscriptionError as e:
    logger.error(f"Transcription failed: {e}")
    raise
```

---

## Testing Guidelines

### Test Structure

```python
# tests/test_meeting_service.py
import pytest
from app.services import MeetingService
from app.models import Meeting

class TestMeetingService:
    """Tests for MeetingService."""
    
    @pytest.fixture
    def service(self, db_session):
        """Create service instance."""
        return MeetingService(db_session)
    
    def test_create_meeting(self, service):
        """Test creating a new meeting."""
        # Arrange
        title = "Test Meeting"
        description = "Test Description"
        
        # Act
        meeting = service.create(title, description)
        
        # Assert
        assert meeting.id is not None
        assert meeting.title == title
        assert meeting.description == description
    
    def test_get_meeting(self, service):
        """Test retrieving a meeting."""
        # Arrange
        meeting = service.create("Test", "Description")
        
        # Act
        retrieved = service.get(meeting.id)
        
        # Assert
        assert retrieved.id == meeting.id
```

### Test Coverage

- Minimum 80% code coverage required
- Test all public methods
- Test error cases
- Test edge cases

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_meeting_service.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_meeting_service.py::TestMeetingService::test_create_meeting
```

---

## Documentation Standards

### When to Update Documentation

1. **After implementing a feature**: Update relevant docs/ file
2. **After architectural decision**: Document in docs/01_ARCHITECTURE.md
3. **After database schema change**: Update docs/02_DATABASE.md
4. **After API change**: Update docs/03_API.md
5. **After UI change**: Update docs/04_FRONTEND.md
6. **After AI pipeline change**: Update docs/05_AI_PIPELINE.md

### Documentation Format

- Use Markdown (.md files)
- Clear section headers
- Code examples where helpful
- Links to related documents
- Keep documentation synchronized with code

### Example Documentation

```markdown
# Feature Name

## Overview

Brief description of the feature.

## Usage

How to use the feature.

### Example

\`\`\`python
# Code example
result = function()
\`\`\`

## Configuration

Configuration options.

## Related Documents

- [Related Doc](./related.md)
```

---

## Pull Request Process

### PR Title Format

```
[PHASE-N] Feature: Brief description
```

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Documentation
- [ ] Documentation updated
- [ ] PROJECT_STATE.MD updated
- [ ] Backlog updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Tests pass
- [ ] No new warnings
- [ ] Documentation updated
```

### Review Checklist

Reviewers should verify:

- [ ] Code follows project standards
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Tests included and passing
- [ ] No code duplication
- [ ] Error handling appropriate
- [ ] Documentation updated
- [ ] No breaking changes without discussion

---

## Commit Message Format

### Format

```
[PHASE-N] Type: Brief description

Detailed explanation of changes:
- Change 1
- Change 2

Related to: docs/XX_DOCUMENT.md
```

### Types

- **Feature**: New feature
- **Fix**: Bug fix
- **Docs**: Documentation update
- **Test**: Test addition/update
- **Refactor**: Code refactoring
- **Perf**: Performance improvement

### Examples

```
[PHASE-1] Feature: Add logging configuration

Implemented structured logging with file and console handlers.
Supports different log levels and rotation.

Related to: docs/00_PROJECT_OVERVIEW.md

[PHASE-2] Fix: Fix meeting deletion bug

Soft delete now properly sets deleted_at timestamp.
Added test to prevent regression.

Related to: docs/02_DATABASE.md
```

---

## Issue Reporting

### Bug Report Template

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- Python version: 3.12
- OS: Ubuntu 24.04
- Branch: main

## Logs
```
Error logs here
```
```

### Feature Request Template

```markdown
## Description
Clear description of the feature.

## Use Case
Why this feature is needed.

## Proposed Solution
How the feature should work.

## Alternative Solutions
Other possible approaches.

## Related Issues
Links to related issues.
```

---

## Development Tips

### Useful Commands

```bash
# Format code with Black
black app/

# Lint with Flake8
flake8 app/

# Type checking with mypy
mypy app/

# Run all checks
pre-commit run --all-files

# Update dependencies
pip install -U -r requirements.txt

# Create migration
alembic revision --autogenerate -m "Description"
```

### Debugging

```python
# Use print for quick debugging
print(f"Debug: {variable}")

# Use pdb for interactive debugging
import pdb; pdb.set_trace()

# Use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Performance Profiling

```bash
# Profile with cProfile
python -m cProfile -s cumtime main.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler main.py
```

---

## Resources

### Documentation

- [Project Overview](./00_PROJECT_OVERVIEW.md)
- [Architecture](./01_ARCHITECTURE.md)
- [Database](./02_DATABASE.md)
- [API](./03_API.md)
- [Frontend](./04_FRONTEND.md)
- [AI Pipeline](./05_AI_PIPELINE.md)

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://pep8.org/)

---

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue with bug report template
- **Features**: Create an issue with feature request template
- **Code Review**: Request review in PR

---

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

Thank you for contributing to AMIP!

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
