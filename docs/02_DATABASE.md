# 02_DATABASE.md

## Database Design & Schema

### Database Strategy

- **Default**: SQLite for development and small deployments
- **Production**: PostgreSQL recommended
- **ORM**: SQLAlchemy for database abstraction
- **Migrations**: Alembic for schema versioning
- **Soft Deletes**: Preserve data integrity

### Entity Relationship Diagram

```
┌─────────────────────┐
│     meetings        │
├─────────────────────┤
│ id (PK)             │
│ title               │
│ description         │
│ created_at          │
│ updated_at          │
│ deleted_at (soft)   │
└──────┬──────────────┘
       │ 1:N
       │
       ├─────────────────────────────────┐
       │                                 │
       ▼                                 ▼
┌─────────────────────┐         ┌──────────────────┐
│      audios         │         │ transcriptions   │
├─────────────────────┤         ├──────────────────┤
│ id (PK)             │         │ id (PK)          │
│ meeting_id (FK)     │         │ audio_id (FK)    │
│ filename            │         │ text             │
│ file_path           │         │ language         │
│ duration            │         │ created_at       │
│ file_size           │         │ updated_at       │
│ mime_type           │         │ deleted_at       │
│ created_at          │         └──────────────────┘
│ updated_at          │
│ deleted_at          │
└─────────────────────┘

┌──────────────────────┐
│  speaker_segments    │
├──────────────────────┤
│ id (PK)              │
│ transcription_id(FK) │
│ speaker_label        │
│ start_time           │
│ end_time             │
│ text                 │
│ confidence           │
│ created_at           │
└──────────────────────┘

┌──────────────────────┐
│   meeting_analysis   │
├──────────────────────┤
│ id (PK)              │
│ meeting_id (FK)      │
│ summary              │
│ action_items         │
│ decisions            │
│ risks                │
│ open_questions       │
│ follow_up_tasks      │
│ created_at           │
│ updated_at           │
└──────────────────────┘
```

### Core Tables

#### meetings

Represents a meeting event.

```sql
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_created_at (created_at),
    INDEX idx_deleted_at (deleted_at)
);
```

**Columns**:
- `id`: Unique identifier
- `title`: Meeting title
- `description`: Optional meeting description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `deleted_at`: Soft delete timestamp (NULL if active)

**Indexes**:
- `created_at`: For chronological queries
- `deleted_at`: For filtering active meetings

#### audios

Represents audio files associated with meetings.

```sql
CREATE TABLE audios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    duration INTEGER,
    file_size INTEGER,
    mime_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id),
    INDEX idx_meeting_id (meeting_id),
    INDEX idx_deleted_at (deleted_at)
);
```

**Columns**:
- `id`: Unique identifier
- `meeting_id`: Reference to meeting
- `filename`: Original filename
- `file_path`: Storage path
- `duration`: Audio duration in seconds
- `file_size`: File size in bytes
- `mime_type`: Audio format (audio/mp3, audio/wav, etc.)
- `created_at`: Upload timestamp
- `updated_at`: Last update timestamp
- `deleted_at`: Soft delete timestamp

#### transcriptions

Represents transcribed text from audio.

```sql
CREATE TABLE transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audio_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    language VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (audio_id) REFERENCES audios(id),
    INDEX idx_audio_id (audio_id),
    INDEX idx_deleted_at (deleted_at)
);
```

**Columns**:
- `id`: Unique identifier
- `audio_id`: Reference to audio file
- `text`: Full transcribed text
- `language`: Detected language code (en, pt, etc.)
- `created_at`: Transcription timestamp
- `updated_at`: Last update timestamp
- `deleted_at`: Soft delete timestamp

#### speaker_segments

Represents speaker-identified segments of transcription.

```sql
CREATE TABLE speaker_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcription_id INTEGER NOT NULL,
    speaker_label VARCHAR(50),
    start_time FLOAT,
    end_time FLOAT,
    text TEXT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id),
    INDEX idx_transcription_id (transcription_id),
    INDEX idx_speaker_label (speaker_label)
);
```

**Columns**:
- `id`: Unique identifier
- `transcription_id`: Reference to transcription
- `speaker_label`: Speaker identifier (Speaker 1, Speaker 2, etc.)
- `start_time`: Segment start time in seconds
- `end_time`: Segment end time in seconds
- `text`: Segment text
- `confidence`: Speaker identification confidence (0-1)

#### meeting_analysis

Represents AI-generated analysis of meetings.

```sql
CREATE TABLE meeting_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL UNIQUE,
    summary TEXT,
    action_items TEXT,
    decisions TEXT,
    risks TEXT,
    open_questions TEXT,
    follow_up_tasks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id),
    INDEX idx_meeting_id (meeting_id)
);
```

**Columns**:
- `id`: Unique identifier
- `meeting_id`: Reference to meeting (one-to-one)
- `summary`: AI-generated summary
- `action_items`: Extracted action items (JSON)
- `decisions`: Identified decisions (JSON)
- `risks`: Identified risks (JSON)
- `open_questions`: Open questions (JSON)
- `follow_up_tasks`: Follow-up tasks (JSON)
- `created_at`: Analysis timestamp
- `updated_at`: Last update timestamp

### SQLAlchemy Models

#### Meeting Model

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class Meeting(Base):
    __tablename__ = "meetings"
    
    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: datetime = Column(DateTime, nullable=True)
    
    # Relationships
    audios = relationship("Audio", back_populates="meeting")
    analysis = relationship("MeetingAnalysis", back_populates="meeting", uselist=False)
    
    def is_active(self) -> bool:
        """Check if meeting is not soft-deleted."""
        return self.deleted_at is None
    
    def soft_delete(self):
        """Soft delete the meeting."""
        self.deleted_at = datetime.utcnow()
```

#### Audio Model

```python
class Audio(Base):
    __tablename__ = "audios"
    
    id: int = Column(Integer, primary_key=True, index=True)
    meeting_id: int = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    filename: str = Column(String(255), nullable=False)
    file_path: str = Column(String(512), nullable=False)
    duration: int = Column(Integer, nullable=True)
    file_size: int = Column(Integer, nullable=True)
    mime_type: str = Column(String(50), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: datetime = Column(DateTime, nullable=True)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="audios")
    transcription = relationship("Transcription", back_populates="audio", uselist=False)
```

### Database Initialization

```python
# app/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
```

### Database Migrations

**Using Alembic**:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add meetings table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Query Patterns

#### Get Active Meetings

```python
def get_active_meetings(db: Session) -> List[Meeting]:
    return db.query(Meeting).filter(Meeting.deleted_at.is_(None)).all()
```

#### Get Meeting with Audio and Transcription

```python
def get_meeting_full(db: Session, meeting_id: int) -> Meeting:
    return db.query(Meeting)\
        .filter(Meeting.id == meeting_id)\
        .filter(Meeting.deleted_at.is_(None))\
        .first()
```

#### Search Meetings by Title

```python
def search_meetings(db: Session, query: str) -> List[Meeting]:
    return db.query(Meeting)\
        .filter(Meeting.title.ilike(f"%{query}%"))\
        .filter(Meeting.deleted_at.is_(None))\
        .all()
```

#### Get Speaker Segments for Meeting

```python
def get_speaker_segments(db: Session, meeting_id: int) -> List[SpeakerSegment]:
    return db.query(SpeakerSegment)\
        .join(Transcription)\
        .join(Audio)\
        .filter(Audio.meeting_id == meeting_id)\
        .order_by(SpeakerSegment.start_time)\
        .all()
```

### Performance Optimization

#### Indexing Strategy

```python
# Index frequently searched columns
Index('idx_meeting_created_at', Meeting.created_at)
Index('idx_audio_meeting_id', Audio.meeting_id)
Index('idx_speaker_label', SpeakerSegment.speaker_label)
```

#### Query Optimization

```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload

meetings = db.query(Meeting)\
    .options(joinedload(Meeting.audios))\
    .filter(Meeting.deleted_at.is_(None))\
    .all()
```

#### Pagination

```python
def get_meetings_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[Meeting]:
    return db.query(Meeting)\
        .filter(Meeting.deleted_at.is_(None))\
        .offset(skip)\
        .limit(limit)\
        .all()
```

### Backup & Recovery

```bash
# Backup SQLite database
cp app.db app.db.backup

# Restore from backup
cp app.db.backup app.db
```

### Database Monitoring

```python
# Log slow queries
from sqlalchemy import event
import logging

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    if total_time > 0.5:  # Log queries taking > 500ms
        logger.warning(f"Slow query ({total_time:.2f}s): {statement}")
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
