from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECORDER_JS = PROJECT_ROOT / "static" / "js" / "meeting_recording.js"
MEETING_TEMPLATE = PROJECT_ROOT / "templates" / "meeting_detail.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_online_mode_exposes_remote_audio_selection_ui():
    html = _read(MEETING_TEMPLATE)

    assert 'value="online"' in html
    assert 'id="meetingAudioSelectBtn"' in html
    assert 'id="meetingAudioReadiness"' in html
    assert 'id="meetingLevelBar"' in html
    assert 'id="microphoneLevelBar"' in html


def test_remote_capture_requires_browser_tab_audio():
    javascript = _read(RECORDER_JS)

    assert "getDisplayMedia" in javascript
    assert "getAudioTracks()" in javascript
    assert "Áudio não compartilhado" in javascript
    assert "Selecione uma aba da reunião" in javascript


def test_online_recording_uses_web_audio_mixer():
    javascript = _read(RECORDER_JS)

    assert "AudioContext" in javascript
    assert "createMediaStreamDestination" in javascript
    assert "createMediaStreamSource(microphoneStream)" in javascript
    assert "createMediaStreamSource(meetingDisplayStream)" in javascript
    assert "microphoneSource.connect(mixedDestination)" in javascript
    assert "meetingSource.connect(mixedDestination)" in javascript


def test_remote_video_is_not_added_to_recorded_stream():
    javascript = _read(RECORDER_JS)

    # The shared display stream is only used as an audio source for Web Audio.
    # The MediaRecorder must receive the mixer destination, not the display stream.
    assert "return mixedDestination.stream" in javascript
    assert "beginRecorder(mixedStream" in javascript
    assert "beginRecorder(meetingDisplayStream" not in javascript


def test_source_loss_protection_is_present():
    javascript = _read(RECORDER_JS)

    assert "stopBecauseSourceEnded" in javascript
    assert "O microfone foi desconectado" in javascript
    assert "O áudio da reunião foi interrompido" in javascript
    assert "track.addEventListener('ended'" in javascript


def test_audio_source_monitoring_is_present():
    javascript = _read(RECORDER_JS)

    assert "createAnalyser" in javascript
    assert "requestAnimationFrame" in javascript
    assert "getByteTimeDomainData" in javascript
    assert "Recebendo áudio" in javascript
    assert "Silêncio" in javascript


def test_room_mode_keeps_raw_microphone_constraints():
    javascript = _read(RECORDER_JS)

    assert "echoCancellation: false" in javascript
    assert "noiseSuppression: false" in javascript
    assert "autoGainControl: false" in javascript
