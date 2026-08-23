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
  const modeInputs = Array.from(document.querySelectorAll('input[name="recordingMode"]'));
  const readinessBadge = document.getElementById('recordingReadinessBadge');
  const microphoneReadiness = document.getElementById('microphoneReadiness');
  const meetingAudioReadinessRow = document.getElementById('meetingAudioReadinessRow');
  const meetingAudioReadiness = document.getElementById('meetingAudioReadiness');
  const meetingAudioControls = document.getElementById('meetingAudioControls');
  const meetingAudioSelectBtn = document.getElementById('meetingAudioSelectBtn');
  const modeHelp = document.getElementById('recordModeHelp');

  let recorder = null;
  let stream = null;
  let meetingDisplayStream = null;
  let chunks = [];
  let recordedBlob = null;
  let recordedMimeType = '';
  let startedAt = null;
  let timerId = null;
  let previewUrl = null;
  let discardRequested = false;
  let recordingMode = 'room';

  function setStatus(message, kind = 'secondary') {
    status.className = `small text-${kind}`;
    status.textContent = message;
  }

  function setReadinessBadge(label, kind = 'secondary') {
    readinessBadge.className = `badge text-bg-${kind}`;
    readinessBadge.textContent = label;
  }

  function setModeInputsDisabled(disabled) {
    modeInputs.forEach(input => { input.disabled = disabled; });
  }

  function hasLiveMeetingAudio() {
    return Boolean(meetingDisplayStream?.getAudioTracks().some(track => track.readyState === 'live'));
  }

  function stopMeetingDisplayStream() {
    if (meetingDisplayStream) meetingDisplayStream.getTracks().forEach(track => track.stop());
    meetingDisplayStream = null;
  }

  function updateOnlineReadiness() {
    if (recordingMode !== 'online') return;
    const ready = hasLiveMeetingAudio();
    meetingAudioReadiness.textContent = ready ? 'Pronto' : 'Ainda não selecionado';
    meetingAudioReadiness.className = ready ? 'text-success' : 'text-warning';
    meetingAudioSelectBtn.textContent = ready ? 'Trocar aba da reunião' : 'Selecionar aba da reunião';
    startBtn.disabled = !ready;
    setReadinessBadge(ready ? 'Áudio remoto pronto' : 'Configuração incompleta', ready ? 'success' : 'warning');
  }

  function renderRecordingMode() {
    const selected = modeInputs.find(input => input.checked);
    const nextMode = selected?.value || 'room';
    if (recordingMode === 'online' && nextMode !== 'online') stopMeetingDisplayStream();
    recordingMode = nextMode;

    microphoneReadiness.textContent = 'Será solicitado ao iniciar';
    microphoneReadiness.className = 'text-secondary';

    if (recordingMode === 'online') {
      meetingAudioReadinessRow.classList.remove('d-none');
      meetingAudioControls.classList.remove('d-none');
      modeHelp.textContent = 'Modo online: selecione a aba da reunião com compartilhamento de áudio. O microfone local será solicitado ao iniciar a gravação.';
      updateOnlineReadiness();
      setStatus(hasLiveMeetingAudio() ? 'Áudio da reunião selecionado. Pronto para solicitar o microfone.' : 'Selecione a aba da reunião e habilite o compartilhamento de áudio.', hasLiveMeetingAudio() ? 'success' : 'warning');
      return;
    }

    meetingAudioReadinessRow.classList.add('d-none');
    meetingAudioControls.classList.add('d-none');
    setReadinessBadge('Pronto para solicitar microfone', 'secondary');
    modeHelp.textContent = 'Modo presencial: o navegador usará somente o microfone deste computador.';
    startBtn.disabled = false;
    setStatus('Nenhuma gravação em andamento.', 'secondary');
  }

  async function selectMeetingAudio() {
    if (!navigator.mediaDevices?.getDisplayMedia) {
      meetingAudioReadiness.textContent = 'Não suportado';
      meetingAudioReadiness.className = 'text-danger';
      setReadinessBadge('Navegador incompatível', 'danger');
      setStatus('Este navegador não permite capturar o áudio de uma aba. Use uma versão atual do Chrome ou Edge.', 'danger');
      return;
    }

    meetingAudioSelectBtn.disabled = true;
    setStatus('Escolha a aba da reunião e habilite o compartilhamento de áudio.', 'primary');
    try {
      const candidate = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
        preferCurrentTab: false,
        selfBrowserSurface: 'exclude',
        surfaceSwitching: 'exclude',
      });
      const audioTracks = candidate.getAudioTracks();
      if (!audioTracks.length) {
        candidate.getTracks().forEach(track => track.stop());
        stopMeetingDisplayStream();
        meetingAudioReadiness.textContent = 'Áudio não compartilhado';
        meetingAudioReadiness.className = 'text-danger';
        setReadinessBadge('Áudio remoto ausente', 'danger');
        startBtn.disabled = true;
        setStatus('A fonte selecionada não forneceu áudio. Selecione a aba da reunião e marque a opção de compartilhar áudio.', 'danger');
        return;
      }

      stopMeetingDisplayStream();
      meetingDisplayStream = candidate;
      const onCaptureEnded = () => {
        if (meetingDisplayStream !== candidate) return;
        stopMeetingDisplayStream();
        updateOnlineReadiness();
        setStatus('O compartilhamento da aba da reunião foi encerrado. Selecione a aba novamente.', 'warning');
      };
      candidate.getVideoTracks().forEach(track => track.addEventListener('ended', onCaptureEnded, {once: true}));
      audioTracks.forEach(track => track.addEventListener('ended', onCaptureEnded, {once: true}));
      updateOnlineReadiness();
      setStatus('Áudio da reunião detectado. O vídeo compartilhado não será gravado pelo AMIP.', 'success');
    } catch (error) {
      if (error?.name === 'NotAllowedError') {
        setStatus('Seleção da aba cancelada ou permissão de compartilhamento negada.', 'warning');
      } else {
        setStatus('Não foi possível acessar o áudio da reunião.', 'danger');
      }
      updateOnlineReadiness();
    } finally {
      meetingAudioSelectBtn.disabled = false;
    }
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

  function stopAllTracks() {
    stopTracks();
    stopMeetingDisplayStream();
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
    stopBtn.classList.add('d-none');
    stopBtn.disabled = false;
    uploadBtn.classList.add('d-none');
    uploadBtn.disabled = false;
    discardBtn.classList.add('d-none');
    discardBtn.disabled = false;
    timer.textContent = '00:00';
    setModeInputsDisabled(false);
    renderRecordingMode();
  }

  function extensionForMime(mime) {
    const base = mime.split(';', 1)[0].toLowerCase();
    if (base === 'audio/ogg' || base === 'application/ogg') return 'ogg';
    if (base === 'audio/mp4') return 'm4a';
    return 'webm';
  }

  function preferredMimeType() {
    const candidates = ['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4'];
    return candidates.find(type => MediaRecorder.isTypeSupported(type)) || '';
  }

  async function requestRoomAudio() {
    const rawAudioConstraints = {echoCancellation: false, noiseSuppression: false, autoGainControl: false};
    try {
      return await navigator.mediaDevices.getUserMedia({audio: rawAudioConstraints});
    } catch (error) {
      const unsupportedConstraints = error && (error.name === 'OverconstrainedError' || error.name === 'TypeError');
      if (!unsupportedConstraints) throw error;
      return navigator.mediaDevices.getUserMedia({audio: true});
    }
  }

  async function startRecording() {
    resetPreview();
    discardRequested = false;
    if (recordingMode === 'online') {
      if (!hasLiveMeetingAudio()) {
        updateOnlineReadiness();
        setStatus('Selecione uma aba da reunião com áudio antes de iniciar.', 'warning');
        return;
      }
      setStatus('Áudio remoto validado. A mistura com o microfone será habilitada na Sprint 3.', 'warning');
      return;
    }
    if (!window.isSecureContext) { setStatus('O microfone exige HTTPS ou localhost.', 'danger'); return; }
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') { setStatus('Este navegador não oferece gravação de microfone compatível.', 'danger'); return; }

    try {
      setModeInputsDisabled(true);
      setReadinessBadge('Solicitando microfone', 'primary');
      microphoneReadiness.textContent = 'Solicitando permissão...';
      microphoneReadiness.className = 'text-primary';
      stream = await requestRoomAudio();
      const audioTrack = stream.getAudioTracks()[0];
      if (!audioTrack) throw new Error('MicrophoneAudioTrackMissing');
      microphoneReadiness.textContent = 'Pronto';
      microphoneReadiness.className = 'text-success';
      setReadinessBadge('Pronto', 'success');
      const mimeType = preferredMimeType();
      recorder = mimeType ? new MediaRecorder(stream, {mimeType}) : new MediaRecorder(stream);
      recordedMimeType = recorder.mimeType || mimeType || 'audio/webm';
      chunks = [];
      recorder.addEventListener('dataavailable', event => { if (event.data && event.data.size > 0) chunks.push(event.data); });
      recorder.addEventListener('stop', () => {
        stopTracks(); stopTimer();
        if (discardRequested) { resetPreview(); resetControls(); recorder = null; discardRequested = false; return; }
        recordedBlob = new Blob(chunks, {type: recordedMimeType});
        if (!recordedBlob.size) { resetControls(); discardBtn.classList.remove('d-none'); setStatus('Nenhum áudio foi capturado. Tente novamente.', 'danger'); return; }
        previewUrl = URL.createObjectURL(recordedBlob); preview.src = previewUrl; preview.classList.remove('d-none');
        uploadBtn.classList.remove('d-none'); discardBtn.classList.remove('d-none'); startBtn.classList.add('d-none'); stopBtn.classList.add('d-none'); stopBtn.disabled = false; setModeInputsDisabled(false);
        setStatus(`Gravação pronta (${(recordedBlob.size / 1024 / 1024).toFixed(2)} MB). Revise antes de enviar.`, 'success');
      });
      recorder.start(1000); startedAt = Date.now(); timer.textContent = '00:00'; timerId = window.setInterval(() => { timer.textContent = formatDuration(Date.now() - startedAt); }, 500);
      startBtn.classList.add('d-none'); uploadBtn.classList.add('d-none'); discardBtn.classList.remove('d-none'); stopBtn.classList.remove('d-none'); stopBtn.disabled = false;
      setStatus('Gravando reunião presencial sem supressão de voz do navegador.', 'danger');
    } catch (error) {
      stopTracks(); setModeInputsDisabled(false); setReadinessBadge('Microfone indisponível', 'danger'); microphoneReadiness.textContent = 'Indisponível'; microphoneReadiness.className = 'text-danger'; startBtn.disabled = false;
      const denied = error && (error.name === 'NotAllowedError' || error.name === 'SecurityError');
      setStatus(denied ? 'Permissão de microfone negada pelo navegador.' : 'Não foi possível iniciar o microfone.', 'danger');
    }
  }

  function stopRecording() { if (recorder && recorder.state !== 'inactive') recorder.stop(); stopBtn.disabled = true; setStatus('Finalizando gravação...', 'secondary'); }
  function discardRecording() {
    if (recorder && recorder.state !== 'inactive') { discardRequested = true; recorder.stop(); stopTracks(); stopTimer(); setStatus('Descartando gravação...', 'secondary'); return; }
    resetPreview(); recorder = null; resetControls();
  }

  async function uploadRecording() {
    if (!recordedBlob) return;
    uploadBtn.disabled = true; discardBtn.disabled = true; setStatus('Enviando a gravação pelo pipeline seguro de áudio...', 'primary');
    const extension = extensionForMime(recordedMimeType); const filename = `recording-${new Date().toISOString().replace(/[:.]/g, '-')}.${extension}`; const file = new File([recordedBlob], filename, {type: recordedMimeType}); const body = new FormData(); body.append('file', file);
    try {
      const response = await fetch(`/api/meetings/${meetingId}/audio`, {method: 'POST', body}); const data = await response.json();
      if (!response.ok) { const detail = typeof data.detail === 'string' ? data.detail : 'Falha ao enviar a gravação.'; setStatus(detail, 'danger'); uploadBtn.disabled = false; discardBtn.disabled = false; return; }
      setStatus('Gravação enviada. Preparando a reunião para transcrição...', 'success'); window.setTimeout(() => window.location.reload(), 500);
    } catch (_error) { setStatus('Falha de rede ao enviar a gravação.', 'danger'); uploadBtn.disabled = false; discardBtn.disabled = false; }
  }

  modeInputs.forEach(input => input.addEventListener('change', renderRecordingMode));
  meetingAudioSelectBtn.addEventListener('click', selectMeetingAudio);
  startBtn.addEventListener('click', startRecording);
  stopBtn.addEventListener('click', stopRecording);
  discardBtn.addEventListener('click', discardRecording);
  uploadBtn.addEventListener('click', uploadRecording);
  window.addEventListener('beforeunload', stopAllTracks);
  renderRecordingMode();
})();
