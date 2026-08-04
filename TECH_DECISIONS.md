# Technical Decisions (ADR)

This document records significant technical decisions made during the development of the AI Meeting Intelligence Platform (AMIP).

---

## Decision ID

TD-001

### Title

Arquitetura Monolítica Modular

### Status

Accepted

### Date

2026-08-03

### Context

The project needed a scalable architecture that could support complex AI pipelines without the overhead of distributed systems during early development.

### Decision

We adopted a **clean monolithic architecture** with clear separation of concerns (Presentation → API → Services → Data). Each module (e.g., Audio, Transcription, AI) is developed as an independent service layer within the monolith.

### Consequences

**Advantages:**
- Simplified deployment and debugging.
- Faster development iteration in early stages.
- Easy to test individual components in isolation.

**Limitations:**
- May require refactoring into microservices if the AI processing load becomes too heavy for a single server.

### Future

This decision will be reviewed if the application needs to scale horizontally to handle thousands of concurrent processing jobs.

---

## Decision ID

TD-002

### Title

FastAPI como framework principal

### Status

Accepted

### Date

2026-08-03

### Context

The backend needed a high-performance, modern Python web framework that supports asynchronous processing and automatic API documentation.

### Decision

**FastAPI** was chosen as the primary web framework due to its high performance, built-in data validation via Pydantic, and automatic OpenAPI (Swagger) documentation generation.

### Consequences

**Advantages:**
- Asynchronous request handling (async/await).
- Type-safe request/response models.
- Zero boilerplate for API documentation.

**Limitations:**
- Requires a modern ASGI server (e.g., Uvicorn).

### Future

FastAPI is an industry standard and is expected to remain the primary framework.

---

## Decision ID

TD-003

### Title

SQLite como banco padrão

### Status

Accepted

### Date

2026-08-03

### Context

The initial deployment needs a lightweight, zero-configuration database that can store meeting metadata and transcription results.

### Decision

**SQLite** was selected as the default database engine. It requires no external setup and is ideal for single-server deployments.

### Consequences

**Advantages:**
- Zero configuration; file-based storage.
- High read performance.
- Easy to backup and transfer.

**Limitations:**
- Limited concurrent write capabilities.
- Not suitable for highly scalable, multi-node deployments.

### Future

This decision will be reviewed when migrating to a production environment with multiple concurrent users; PostgreSQL or MySQL may be adopted.

---

## Decision ID

TD-004

### Title

Jinja2 + HTMX em vez de React

### Status

Accepted

### Date

2026-08-03

### Context

The frontend needed to provide dynamic, interactive UI experiences without the complexity and build tooling of a full Single Page Application (SPA) like React.

### Decision

We use server-side rendering with **Jinja2 templates** enhanced by **HTMX** for dynamic updates (e.g., polling job status, form submissions).

### Consequences

**Advantages:**
- No frontend build process (npm, webpack).
- Reduced complexity for the Python backend team.
- Faster initial page loads.

**Limitations:**
- Complex UI interactions (e.g., drag-and-drop) may require additional JavaScript.

### Future

If the UI becomes highly interactive, a React/Vue frontend communicating via REST/GraphQL may be considered.

---

## Decision ID

TD-005

### Title

Bootstrap 5 como framework CSS

### Status

Accepted

### Date

2026-08-03

### Context

The project required a responsive, accessible, and clean UI with minimal custom CSS development.

### Decision

**Bootstrap 5** was chosen as the CSS framework to provide responsive grid layouts, pre-built components (cards, modals), and accessibility features out of the box.

### Consequences

**Advantages:**
- Rapid UI development.
- Consistent design language.
- No dependency on jQuery.

**Limitations:**
- Generic "Bootstrap look" unless heavily customized.

### Future

Bootstrap 5 is stable and will likely remain the standard UI framework.

---

## Decision ID

TD-006

### Title

Whisper como mecanismo padrão de transcrição

### Status

Accepted

### Date

2026-08-03

### Context

The AI pipeline requires a highly accurate speech-to-text engine capable of handling various languages and audio qualities.

### Decision

OpenAI's **Whisper** model is the default transcription engine due to its state-of-the-art accuracy and robustness against background noise.

### Consequences

**Advantages:**
- High accuracy across multiple languages.
- Resilient to varying audio quality.
- Generates precise timestamps.

**Limitations:**
- High computational requirements (GPU recommended).
- Processing time scales linearly with audio length.

### Future

Whisper is the standard; alternatives like Google STT or AWS Transcribe may be added as optional providers.

---

## Decision ID

TD-007

### Title

pyannote.audio para diarização

### Status

Accepted

### Date

2026-08-03

### Context

The application needs to identify and separate different speakers within a single audio recording (Speaker Diarization).

### Decision

**pyannote.audio** is used as the default diarization engine. It is an open-source toolkit built on PyTorch specifically designed for speaker diarization.

### Consequences

**Advantages:**
- Open-source and highly customizable.
- State-of-the-art performance on meeting audio.

**Limitations:**
- Model downloading requires internet access.
- Requires PyTorch as a heavy dependency.

### Future

NVIDIA NeMo or proprietary cloud APIs may be evaluated if higher accuracy is needed.

---

## Decision ID

TD-008

### Title

Repository Pattern

### Status

Accepted

### Date

2026-08-03

### Context

The data access layer needed to be decoupled from the business logic to facilitate testing and future database migrations.

### Decision

The **Repository Pattern** was implemented. All database queries are encapsulated within Repository classes (e.g., `MeetingRepository`), and Services interact only with Repositories, never directly with SQLAlchemy.

### Consequences

**Advantages:**
- Clear separation of concerns.
- Easy to mock database interactions in unit tests.
- Facilitates switching ORM or database engines.

**Limitations:**
- Slight increase in boilerplate code for simple queries.

### Future

This pattern is a core architectural standard and will remain.

---

## Decision ID

TD-009

### Title

Service Layer

### Status

Accepted

### Date

2026-08-03

### Context

Business logic was previously mixed with API routes, leading to bloated controllers and poor testability.

### Decision

A dedicated **Service Layer** was introduced. API routes only validate HTTP requests and delegate all business logic to Services (e.g., `MeetingService`, `ProcessingService`).

### Consequences

**Advantages:**
- API routes remain thin and readable.
- Business logic is fully testable in isolation.
- Easier to reuse logic across different endpoints.

**Limitations:**
- Additional layer of abstraction.

### Future

The Service Layer will be maintained as the core of the business logic.

---

## Decision ID

TD-010

### Title

Uso de Interfaces para provedores de IA

### Status

Accepted

### Date

2026-08-03

### Context

The AI pipeline relies on multiple external providers (Whisper, OpenAI, Ollama, pyannote). Hardcoding these providers would create vendor lock-in.

### Decision

Abstract interfaces (e.g., `ITranscriber`, `IAISummarizer`, `ISpeakerIdentifier`) were defined. Concrete implementations are injected at runtime, allowing providers to be swapped easily.

### Consequences

**Advantages:**
- Zero vendor lock-in.
- Easy to add new AI providers without modifying core logic.
- Highly testable using mock implementations.

**Limitations:**
- Requires defining stable contracts (dataclasses) for inputs/outputs.

### Future

This is the core of the AI pipeline's flexibility and will be strictly enforced.

---

## Decision ID

TD-011

### Title

BackgroundTasks em vez de Celery

### Status

Accepted

### Date

2026-08-03

### Context

The system needs to process audio asynchronously. Introducing a message broker (RabbitMQ/Redis) and Celery adds significant infrastructure complexity.

### Decision

FastAPI's built-in **BackgroundTasks** (and a custom `JobService` queue) will be used for asynchronous processing. This avoids the need for external message brokers.

### Consequences

**Advantages:**
- No external infrastructure dependencies (no Redis/RabbitMQ).
- Simpler deployment and configuration.

**Limitations:**
- Tasks run within the same application process.
- Not suitable for heavy, distributed task processing at scale.

### Future

If task processing bottlenecks occur, the system will be migrated to Celery or Dramatiq.

---

## Decision ID

TD-012

### Title

Armazenamento local em vez de MinIO

### Status

Accepted

### Date

2026-08-03

### Context

Audio files and transcripts need persistent storage. Setting up MinIO or AWS S3 introduces additional infrastructure management.

### Decision

A local file system storage strategy is implemented via the `StorageService`. Files are organized in a structured directory hierarchy (`storage/audio`, `storage/transcripts`, etc.).

### Consequences

**Advantages:**
- No external object storage server required.
- Fast local I/O operations.
- Simplified deployment.

**Limitations:**
- Difficult to scale horizontally across multiple servers.
- Requires manual backup solutions.

### Future

An abstraction for S3/MinIO will be added if the application is deployed in a multi-node environment.

---

## Decision ID

TD-013

### Title

Arquitetura preparada para múltiplos provedores de IA

### Status

Accepted

### Date

2026-08-03

### Context

Different use cases may require different AI models (e.g., local inference via Ollama vs. cloud API via OpenAI).

### Decision

The system is designed to support multiple AI providers simultaneously. The `PipelineService` orchestrates the flow, and specific providers are injected based on configuration.

### Consequences

**Advantages:**
- Flexibility to choose between cost (local) and quality (cloud).
- Fallback mechanisms can be implemented.

**Limitations:**
- Requires maintaining multiple implementation classes for each interface.

### Future

A dynamic provider selection mechanism (e.g., fallback chains) will be implemented in later phases.

---

## Decision ID

TD-014

### Title

Priorizar simplicidade sobre complexidade

### Status

Accepted

### Date

2026-08-03

### Context

Early-stage projects often suffer from over-engineering, leading to slow development and high maintenance costs.

### Decision

We prioritize the **KISS (Keep It Simple, Stupid)** and **YAGNI (You Ain't Gonna Need It)** principles. Features and architectural components are only added when explicitly required by the current phase's goals.

### Consequences

**Advantages:**
- Faster development cycles.
- Lower barrier to entry for new developers.
- Easier debugging.

**Limitations:**
- May require refactoring if scaling requirements grow rapidly.

### Future

This principle guides all phase planning and code reviews.

---

## Decision ID

TD-015

### Title

Desenvolvimento incremental por fases

### Status

Accepted

### Date

2026-08-03

### Context

The AI Meeting Intelligence Platform is a complex system with many moving parts. Developing everything at once risks integration failures and missed requirements.

### Decision

The project is broken down into distinct, sequential **phases** (e.g., Phase 1: Foundation, Phase 2: Core Architecture). Each phase must be fully functional, tested, and documented before moving to the next.

### Consequences

**Advantages:**
- Predictable progress tracking.
- High-quality deliverables at each milestone.
- Easier to adapt to changing requirements.

**Limitations:**
- Slower overall time-to-market compared to a "big bang" release.

### Future

This methodology (Agile/Iterative) will govern the entire product lifecycle.
