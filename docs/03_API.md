# 03_API.md

## API Specification

### API Overview

The AMIP API is built with FastAPI and provides RESTful endpoints for managing meetings, audio, transcriptions, and analysis.

### Base URL

```
http://localhost:8000/api
```

### Response Format

All responses are JSON with consistent structure:

**Success Response**:
```json
{
  "status": "success",
  "data": { /* response data */ },
  "message": "Operation successful"
}
```

**Error Response**:
```json
{
  "status": "error",
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 500 | Server Error - Internal error |

### Authentication

Currently no authentication required. Future versions will implement JWT-based auth.

---

## Endpoints

### Meetings

#### List Meetings

```
GET /api/meetings
```

**Query Parameters**:
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 10)
- `search` (str): Search term for title/description

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Q3 Planning Meeting",
      "description": "Quarterly planning session",
      "created_at": "2026-08-03T10:00:00",
      "updated_at": "2026-08-03T10:00:00"
    }
  ],
  "total": 1
}
```

#### Get Meeting

```
GET /api/meetings/{meeting_id}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Q3 Planning Meeting",
    "description": "Quarterly planning session",
    "created_at": "2026-08-03T10:00:00",
    "updated_at": "2026-08-03T10:00:00",
    "audios": [
      {
        "id": 1,
        "filename": "meeting.mp3",
        "duration": 3600,
        "created_at": "2026-08-03T10:00:00"
      }
    ],
    "analysis": {
      "summary": "Meeting summary...",
      "action_items": ["Item 1", "Item 2"]
    }
  }
}
```

#### Create Meeting

```
POST /api/meetings
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Q3 Planning Meeting",
  "description": "Quarterly planning session"
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Q3 Planning Meeting",
    "description": "Quarterly planning session",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

#### Update Meeting

```
PUT /api/meetings/{meeting_id}
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Updated Title",
    "description": "Updated description",
    "updated_at": "2026-08-03T11:00:00"
  }
}
```

#### Delete Meeting

```
DELETE /api/meetings/{meeting_id}
```

**Response** (204 No Content):
```
No content
```

---

### Audio

#### Upload Audio

```
POST /api/audio/upload
Content-Type: multipart/form-data
```

**Form Parameters**:
- `meeting_id` (int): Meeting ID
- `file` (file): Audio file (mp3, wav, m4a, etc.)

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "meeting_id": 1,
    "filename": "meeting.mp3",
    "duration": 3600,
    "file_size": 45000000,
    "mime_type": "audio/mpeg",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

#### Get Audio

```
GET /api/audio/{audio_id}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "meeting_id": 1,
    "filename": "meeting.mp3",
    "duration": 3600,
    "file_size": 45000000,
    "mime_type": "audio/mpeg",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

#### Delete Audio

```
DELETE /api/audio/{audio_id}
```

**Response** (204 No Content):
```
No content
```

---

### Transcription

#### Start Transcription

```
POST /api/transcription/start
Content-Type: application/json
```

**Request Body**:
```json
{
  "audio_id": 1
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "audio_id": 1,
    "status": "processing",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

#### Get Transcription

```
GET /api/transcription/{transcription_id}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "audio_id": 1,
    "text": "Full transcribed text...",
    "language": "en",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

#### Get Transcription by Audio

```
GET /api/audio/{audio_id}/transcription
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "audio_id": 1,
    "text": "Full transcribed text...",
    "language": "en",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

---

### Speaker Identification

#### Get Speaker Segments

```
GET /api/transcription/{transcription_id}/speakers
```

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "speaker_label": "Speaker 1",
      "start_time": 0.0,
      "end_time": 15.5,
      "text": "Good morning everyone...",
      "confidence": 0.95
    },
    {
      "id": 2,
      "speaker_label": "Speaker 2",
      "start_time": 15.5,
      "end_time": 30.2,
      "text": "Thank you for joining...",
      "confidence": 0.92
    }
  ]
}
```

---

### AI Analysis

#### Start Analysis

```
POST /api/analysis/start
Content-Type: application/json
```

**Request Body**:
```json
{
  "meeting_id": 1
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "meeting_id": 1,
    "status": "processing",
    "created_at": "2026-08-03T10:00:00"
  }
}
```

#### Get Analysis

```
GET /api/analysis/{meeting_id}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "meeting_id": 1,
    "summary": "This meeting discussed Q3 objectives and resource allocation...",
    "action_items": [
      "Complete project proposal by Friday",
      "Schedule follow-up meeting with stakeholders",
      "Review budget allocation"
    ],
    "decisions": [
      "Approved Q3 budget increase",
      "Decided to hire 2 additional team members"
    ],
    "risks": [
      "Timeline may be tight for project delivery",
      "Resource constraints in Q4"
    ],
    "open_questions": [
      "How will we handle resource conflicts?",
      "What's the contingency plan if timeline slips?"
    ],
    "follow_up_tasks": [
      "Send meeting minutes to all attendees",
      "Update project timeline in system"
    ],
    "created_at": "2026-08-03T10:00:00"
  }
}
```

---

### Search

#### Search Meetings

```
GET /api/search/meetings
```

**Query Parameters**:
- `q` (str): Search query (searches title, description, transcription text)
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 10)

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Q3 Planning Meeting",
      "description": "Quarterly planning session",
      "created_at": "2026-08-03T10:00:00",
      "relevance_score": 0.95
    }
  ],
  "total": 1
}
```

#### Search Transcriptions

```
GET /api/search/transcriptions
```

**Query Parameters**:
- `q` (str): Search query
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 10)

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "audio_id": 1,
      "meeting_id": 1,
      "text": "...relevant text snippet...",
      "relevance_score": 0.92
    }
  ],
  "total": 1
}
```

---

### Export

#### Export Meeting

```
GET /api/export/meeting/{meeting_id}
```

**Query Parameters**:
- `format` (str): Export format (markdown, pdf, txt, docx)

**Response**:
- Format: Markdown - Returns markdown content
- Format: PDF - Returns PDF file
- Format: TXT - Returns text file
- Format: DOCX - Returns Word document

**Example Markdown Export**:
```markdown
# Q3 Planning Meeting

**Date**: 2026-08-03  
**Duration**: 1 hour

## Summary

This meeting discussed Q3 objectives...

## Action Items

- Complete project proposal by Friday
- Schedule follow-up meeting with stakeholders

## Decisions

- Approved Q3 budget increase
- Decided to hire 2 additional team members

## Risks

- Timeline may be tight for project delivery
```

---

## Error Handling

### Common Error Responses

#### Not Found

```json
{
  "status": "error",
  "detail": "Meeting not found",
  "code": "MEETING_NOT_FOUND"
}
```

#### Invalid Input

```json
{
  "status": "error",
  "detail": "Invalid meeting title: title must be at least 3 characters",
  "code": "INVALID_INPUT"
}
```

#### Processing Error

```json
{
  "status": "error",
  "detail": "Transcription failed: unable to process audio file",
  "code": "TRANSCRIPTION_ERROR"
}
```

---

## Rate Limiting

Currently no rate limiting. Future versions will implement:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Pagination

All list endpoints support pagination:

```
GET /api/meetings?skip=0&limit=10
```

**Response includes**:
- `data`: Array of records
- `total`: Total number of records
- `skip`: Number of records skipped
- `limit`: Limit used

---

## Filtering

Supported filters vary by endpoint:

**Meetings**:
- `search`: Search in title/description
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date

**Transcriptions**:
- `language`: Filter by language
- `meeting_id`: Filter by meeting

---

## Versioning

Current API version: **v1**

Future versions will be available at `/api/v2`, `/api/v3`, etc.

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
