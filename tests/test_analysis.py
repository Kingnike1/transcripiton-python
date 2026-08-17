"""Tests for Stack 12 structured LLM intelligence."""

from app.core.enums import ProcessingStatus
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.schemas.analysis import EvidenceRef, IntelligenceItem, StructuredAnalysis
from app.services.analysis_service import AnalysisService
from app.services.diarization_service import DiarizationService
from app.services.interfaces import DiarizationResult, SpeakerSegment, TranscriptResult, TranscriptSegment
from app.services.participant_service import ParticipantService
from app.services.transcription_service import TranscriptionService


class FakeLLM:
    model = "fake-qwen"

    def analyze(self, transcript: str) -> StructuredAnalysis:
        assert "Pablo (SPEAKER_00)" in transcript
        return StructuredAnalysis(
            summary="Reunião sobre entrega.",
            action_items=[
                IntelligenceItem(
                    text="Preparar a entrega",
                    owner="Pablo",
                    evidence=[
                        EvidenceRef(
                            speaker_label="SPEAKER_00",
                            participant_name="Pablo",
                            start_time=0.0,
                            end_time=1.0,
                            quote="Vou preparar a entrega",
                        )
                    ],
                )
            ],
            decisions=[],
            risks=[],
            open_questions=[],
            follow_up_tasks=[],
        )


def _diarized_meeting(db_session):
    meeting = Meeting(title="LLM", status=ProcessingStatus.TRANSCRIBING.value)
    db_session.add(meeting)
    db_session.flush()
    audio = Audio(
        meeting_id=meeting.id,
        filename="sample.wav",
        file_path="audio/sample.wav",
        file_size=8,
        mime_type="audio/wav",
    )
    db_session.add(audio)
    db_session.commit()
    transcript = TranscriptionService(db_session).persist_result(
        meeting.id,
        audio.id,
        TranscriptResult(
            id="t",
            audio_path=audio.file_path,
            text="Vou preparar a entrega",
            language="pt",
            segments=[TranscriptSegment("Vou preparar a entrega", 0.0, 1.0)],
        ),
    )
    meeting.status = ProcessingStatus.DIARIZING.value
    db_session.commit()
    DiarizationService(db_session).persist_result(
        meeting.id,
        transcript,
        DiarizationResult(
            id="d",
            audio_path=audio.file_path,
            num_speakers=1,
            segments=[SpeakerSegment(0.0, 1.0, "SPEAKER_00")],
        ),
    )
    ParticipantService(db_session).update_identity(
        meeting.id,
        "SPEAKER_00",
        display_name="Pablo",
        confirmed=True,
    )
    return meeting


def test_analysis_persists_structured_grounded_result(db_session):
    meeting = _diarized_meeting(db_session)
    row = AnalysisService(db_session).analyze_and_persist(meeting.id, FakeLLM())

    assert row.summary == "Reunião sobre entrega."
    assert row.provider == "ollama"
    assert row.model_name == "fake-qwen"
    assert db_session.get(Meeting, meeting.id).status == ProcessingStatus.COMPLETED.value

    response = AnalysisService(db_session).to_response(row)
    assert response.action_items[0].owner == "Pablo"
    assert response.action_items[0].evidence[0].speaker_label == "SPEAKER_00"


def test_analysis_api_returns_persisted_result(client, db_session):
    meeting = _diarized_meeting(db_session)
    AnalysisService(db_session).analyze_and_persist(meeting.id, FakeLLM())

    response = client.get(f"/api/meetings/{meeting.id}/analysis")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == "Reunião sobre entrega."
    assert payload["model_name"] == "fake-qwen"


def test_analysis_job_requires_diarized_meeting(client, db_session):
    meeting = Meeting(title="Not ready", status=ProcessingStatus.TRANSCRIBED.value)
    db_session.add(meeting)
    db_session.commit()

    response = client.post(f"/api/meetings/{meeting.id}/jobs/analysis")
    assert response.status_code == 409
