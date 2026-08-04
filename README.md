# AI Meeting Intelligence Platform (AMIP)

A **AI Meeting Intelligence Platform** is a modular monolithic web application built with **Python (FastAPI)** that processes meeting audio recordings into intelligent insights. It transcribes speech, identifies speakers, and generates AI-powered summaries, action items, and meeting minutes.

## 🚀 Features

- **Audio Management**: Upload and store meeting audio recordings.
- **Transcription**: Convert audio to text using Whisper.
- **Speaker Identification**: Diarize audio to identify different speakers using pyannote.audio.
- **AI Analysis**: Generate summaries, action items, decisions, and risks using LLMs (OpenAI/Ollama).
- **Export**: Download meeting reports in Markdown, PDF, TXT, or DOCX formats.

## 🏗️ Architecture

The project follows a **clean monolithic architecture** with clear separation of concerns:

- **Presentation Layer**: HTML templates (Jinja2) with Bootstrap 5 and HTMX.
- **API Layer**: FastAPI for HTTP request handling and routing.
- **Service Layer**: Business logic encapsulated in services using the **Repository Pattern**.
- **Data Layer**: SQLAlchemy ORM with SQLite database.
- **Pipeline Orchestration**: Background tasks for processing audio through the AI pipeline.

For detailed architectural decisions, see [TECH_DECISIONS.md](TECH_DECISIONS.md).

## 📁 Project Structure

```
app/
├── api/          # FastAPI routes
├── core/         # Configuration, enums, exceptions
├── database/     # SQLAlchemy models and repositories
├── models/       # Database models
├── schemas/      # Pydantic schemas for validation
└── services/     # Business logic and pipeline orchestration
docs/             # Project documentation
storage/          # Local file storage (audio, transcripts, exports)
tests/            # Pytest test suite
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- Virtual environment tool (venv)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd transcripiton-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys (OpenAI, Ollama, etc.)

# Run the application
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

## 🧪 Testing

The project uses **pytest** for testing with a target coverage of 80%+.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📄 Documentation

- [Project Overview](docs/00_PROJECT_OVERVIEW.md)
- [Architecture](docs/01_ARCHITECTURE.md)
- [Database Design](docs/02_DATABASE.md)
- [API Specification](docs/03_API.md)
- [Frontend Architecture](docs/04_FRONTEND.md)
- [AI Pipeline](docs/05_AI_PIPELINE.md)
- [Product Backlog](docs/06_BACKLOG.md)
- [Deployment Guide](docs/08_DEPLOYMENT.md)
- [Contributing Guidelines](docs/09_CONTRIBUTING.md)

## 📝 Technical Decisions

Key architectural decisions are documented in [TECH_DECISIONS.md](TECH_DECISIONS.md).

## 🤝 Contributing

See [CONTRIBUTING.md](docs/09_CONTRIBUTING.md) for guidelines on how to contribute to this project.

## 📜 License

This project is licensed under the MIT License.

---

**Built with ❤️ by Manus AI**
