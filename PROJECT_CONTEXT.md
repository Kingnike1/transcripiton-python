# PROJECT_CONTEXT.md

## AI Meeting Intelligence Platform (AMIP)

### Vision

The **AI Meeting Intelligence Platform** is a comprehensive, user-friendly application designed to transform how organizations capture, process, and extract value from meetings. By combining modern AI technologies with a clean, maintainable architecture, AMIP enables users to focus on content while the platform handles transcription, analysis, and knowledge extraction.

### Problem Statement

Modern organizations conduct hundreds of meetings daily, yet most meeting insights are lost or difficult to retrieve. Participants struggle to:

- Capture accurate meeting records
- Identify key decisions and action items
- Track speaker contributions
- Search historical meetings efficiently
- Generate professional meeting documentation

### Solution Overview

AMIP solves these challenges through an integrated platform that:

1. **Records and uploads** meeting audio seamlessly
2. **Transcribes** audio with speaker identification
3. **Analyzes** content to extract summaries, action items, decisions, and risks
4. **Stores** meetings with full-text search capabilities
5. **Exports** professional reports in multiple formats

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| Meeting Management | Create, edit, delete, and organize meetings | Planned |
| Audio Recording | Capture audio directly from microphone | Planned |
| Audio Upload | Support for various audio formats | Planned |
| Transcription | Convert audio to text with timestamps | Planned |
| Speaker Identification | Identify and label different speakers | Planned |
| AI Analysis | Generate summaries, minutes, action items | Planned |
| Search | Full-text search with filters | Planned |
| Export | Export to Markdown, PDF, TXT, DOCX | Planned |

### Target Users

- **Business professionals** conducting regular meetings
- **Project managers** tracking action items and decisions
- **Teams** needing centralized meeting documentation
- **Organizations** requiring audit trails and compliance records

### Technical Philosophy

- **Simplicity**: Build a clean monolithic application, not a complex microservices platform
- **Maintainability**: Code that is easy to understand and modify
- **Performance**: Run efficiently on common notebooks and desktops
- **Modularity**: Well-organized, loosely coupled components
- **Extensibility**: Support multiple AI providers without core changes

### Success Criteria

1. Application runs on 8GB+ RAM systems
2. All core features fully functional and tested
3. Comprehensive documentation and code comments
4. Support for multiple AI providers (OpenAI, Ollama)
5. Clean, maintainable codebase following best practices
6. Professional export formats
7. Full-text search capabilities

### Timeline & Phases

The project is developed incrementally across 8 phases:

- **Phase 1**: Project foundation (structure, config, database, logging)
- **Phase 2**: Meeting management (CRUD operations)
- **Phase 3**: Audio handling (recording, upload, storage)
- **Phase 4**: Transcription (Whisper integration)
- **Phase 5**: Speaker identification (pyannote integration)
- **Phase 6**: AI processing (summaries, minutes, action items)
- **Phase 7**: Search functionality
- **Phase 8**: Export capabilities

### Stakeholders

- **Development Team**: Responsible for implementation
- **Users**: Provide feedback on usability and features
- **Project Owner**: Oversees vision and priorities

### Success Metrics

- Code coverage > 80%
- All tests passing
- Documentation up-to-date
- Application deployment successful
- User acceptance testing passed

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
