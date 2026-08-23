(() => {
  const root = document.querySelector('main[data-meeting-id]');
  const area = document.getElementById('microphoneRecorder');
  if (!root || !area) return;

  const meetingId = Number(root.dataset.meetingId);
  const startBtn = document.getElementById('recordStartBtn');
  const stopBtn = document.getElementById('recordStopBtn');
  const discardBtn = document.getElementById('recordDiscardBtn');
  const uploadBtn = document.getElementById('recordUploadBtn');
  const status = document.getElementById('recordStatus');
  const timer = document.getElementById('recordTimer');
  const preview = document.getElementById('recordPreview');

  let recorder = null;
  let stream = null;
  let chunks = [];
  let recordedBlob = null;
  let recordedMimeType = '';
  let startedAt = null;
  let timerId = null;
  let previewUrl = null;
  let discardRequested = false;

  function setStatus(message, kind = 'secondary') {
    status.className = `small text-${kind}`;
    status.textContent = message;
  }

  function formatDuration(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const seconds = String(totalSeconds % 60).padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  function stopTracks() {
    if (stream) stream.getTracks().forEach(track => track.stop());
    stream = null;
  }

  function stopTimer() {
    if (timerId) window.clearInterval(timerId);
    timerId = null;
  }

  function resetPreview() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    preview.removeAttribute('src');
    preview.classList.add('d-none');
    recordedBlob = null;
    recordedMimeType = '';
    chunks = [];
  }

  function resetControls() {
    startBtn.classList.remove('d-none');
    startBtn.disabled = false;
    stopBtn.classList.add('d-none');
    stopBtn.disabled = false;
    uploadBtn.classList.add('d-none');
    uploadBtn.disabled = false;
    discardBtn.classList.add('d-none');
    discardBtn.disabled = false;
    timer.textContent = '00:00';
  }

  function extensionForMime(mime) {
    const base = mime.split(';', 1)[0].toLowerCase();
    if (base === 'audio/ogg' || base === 'application/ogg') return 'ogg';
    if (base === 'audio/mp4') return 'm4a';
    return 'webm';
  }

  function preferredMimeType() {
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
    ];
    return candidates.find(type => MediaRecorder.isTypeSupported(type)) || '';
  }

  async function requestRoomAudio() {
    const rawAudioConstraints = {
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    };

    try {
      return await navigator.mediaDevices.getUserMedia({audio: rawAudioConstraints});
    } catch (error) {
      const unsupportedConstraints =
        error && (error.name === 'OverconstrainedError' || error.name === 'TypeError');
      if (!unsupportedConstraints) throw error;

      // Older/limited browsers may reject one of the optional processing flags.
      // Fall back to the default microphone capture instead of blocking recording.
      return navigator.mediaDevices.getUserMedia({audio: true});
    }
  }

  async function startRecording() {
    resetPreview();
    discardRequested = false;
    if (!window.isSecureContext) {
      setStatus('O microfone exige HTTPS ou localhost.', 'danger');
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setStatus('Este navegador não oferece gravação de microfone compatível.', 'danger');
      return;
    }

    try {
      stream = await requestRoomAudio();
      const mimeType = preferredMimeType();
      recorder = mimeType ? new MediaRecorder(stream, {mimeType}) : new MediaRecorder(stream);
      recordedMimeType = recorder.mimeType || mimeType || 'audio/webm';
      chunks = [];
      recorder.addEventListener('dataavailable', event => {
        if (event.data && event.data.size > 0) chunks.push(event.data);
      });
      recorder.addEventListener('stop', () => {
        stopTracks();
        stopTimer();
        if (discardRequested) {
          resetPreview();
          resetControls();
          recorder = null;
          discardRequested = false;
          setStatus('Nenhuma gravação em andamento.', 'secondary');
          return;
        }
        recordedBlob = new Blob(chunks, {type: recordedMimeType});
        if (!recordedBlob.size) {
          resetControls();
          discardBtn.classList.remove('d-none');
          setStatus('Nenhum áudio foi capturado. Tente novamente.', 'danger');
          return;
        }
        previewUrl = URL.createObjectURL(recordedBlob);
        preview.src = previewUrl;
        preview.classList.remove('d-none');
        uploadBtn.classList.remove('d-none');
        discardBtn.classList.remove('d-none');
        startBtn.classList.add('d-none');
        stopBtn.classList.add('d-none');
        stopBtn.disabled = false;
        setStatus(`Gravação pronta (${(recordedBlob.size / 1024 / 1024).toFixed(2)} MB). Revise antes de enviar.`, 'success');
      });
      recorder.start(1000);
      startedAt = Date.now();
      timer.textContent = '00:00';
      timerId = window.setInterval(() => {
        timer.textContent = formatDuration(Date.now() - startedAt);
      }, 500);
      startBtn.classList.add('d-none');
      uploadBtn.classList.add('d-none');
      discardBtn.classList.remove('d-none');
      stopBtn.classList.remove('d-none');
      stopBtn.disabled = false;
      setStatus('Gravando o ambiente sem supressão de voz do navegador.', 'danger');
    } catch (error) {
      stopTracks();
      resetControls();
      const denied = error && (error.name === 'NotAllowedError' || error.name === 'SecurityError');
      setStatus(denied ? 'Permissão de microfone negada pelo navegador.' : 'Não foi possível iniciar o microfone.', 'danger');
    }
  }

  function stopRecording() {
    if (recorder && recorder.state !== 'inactive') recorder.stop();
    stopBtn.disabled = true;
    setStatus('Finalizando gravação...', 'secondary');
  }

  function discardRecording() {
    if (recorder && recorder.state !== 'inactive') {
      discardRequested = true;
      recorder.stop();
      stopTracks();
      stopTimer();
      setStatus('Descartando gravação...', 'secondary');
      return;
    }
    resetPreview();
    recorder = null;
    resetControls();
    setStatus('Nenhuma gravação em andamento.', 'secondary');
  }

  async function uploadRecording() {
    if (!recordedBlob) return;
    uploadBtn.disabled = true;
    discardBtn.disabled = true;
    setStatus('Enviando a gravação pelo pipeline seguro de áudio...', 'primary');
    const extension = extensionForMime(recordedMimeType);
    const filename = `recording-${new Date().toISOString().replace(/[:.]/g, '-')}.${extension}`;
    const file = new File([recordedBlob], filename, {type: recordedMimeType});
    const body = new FormData();
    body.append('file', file);
    try {
      const response = await fetch(`/api/meetings/${meetingId}/audio`, {method: 'POST', body});
      const data = await response.json();
      if (!response.ok) {
        const detail = typeof data.detail === 'string' ? data.detail : 'Falha ao enviar a gravação.';
        setStatus(detail, 'danger');
        uploadBtn.disabled = false;
        discardBtn.disabled = false;
        return;
      }
      setStatus('Gravação enviada. Preparando a reunião para transcrição...', 'success');
      window.setTimeout(() => window.location.reload(), 500);
    } catch (_error) {
      setStatus('Falha de rede ao enviar a gravação.', 'danger');
      uploadBtn.disabled = false;
      discardBtn.disabled = false;
    }
  }

  startBtn.addEventListener('click', startRecording);
  stopBtn.addEventListener('click', stopRecording);
  discardBtn.addEventListener('click', discardRecording);
  uploadBtn.addEventListener('click', uploadRecording);
  window.addEventListener('beforeunload', stopTracks);
})();
