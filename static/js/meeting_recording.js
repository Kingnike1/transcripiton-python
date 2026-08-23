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
  const sourceMonitor = document.getElementById('sourceMonitor');
  const microphoneLevelBar = document.getElementById('microphoneLevelBar');
  const microphoneLevelLabel = document.getElementById('microphoneLevelLabel');
  const meetingLevelGroup = document.getElementById('meetingLevelGroup');
  const meetingLevelBar = document.getElementById('meetingLevelBar');
  const meetingLevelLabel = document.getElementById('meetingLevelLabel');

  let recorder = null;
  let stream = null;
  let microphoneStream = null;
  let meetingDisplayStream = null;
  let audioContext = null;
  let mixedDestination = null;
  let microphoneSource = null;
  let meetingSource = null;
  let microphoneAnalyser = null;
  let meetingAnalyser = null;
  let monitorFrameId = null;
  let chunks = [];
  let recordedBlob = null;
  let recordedMimeType = '';
  let startedAt = null;
  let timerId = null;
  let previewUrl = null;
  let discardRequested = false;
  let recordingMode = 'room';
  let sourceFailureMessage = '';

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

  function stopMicrophoneStream() {
    if (microphoneStream) microphoneStream.getTracks().forEach(track => track.stop());
    microphoneStream = null;
  }

  function stopLevelMonitoring() {
    if (monitorFrameId) cancelAnimationFrame(monitorFrameId);
    monitorFrameId = null;
    microphoneAnalyser = null;
    meetingAnalyser = null;
    microphoneLevelBar.style.width = '0%';
    microphoneLevelLabel.textContent = 'Aguardando';
    meetingLevelBar.style.width = '0%';
    meetingLevelLabel.textContent = 'Aguardando';
    sourceMonitor.classList.add('d-none');
  }

  function levelFromAnalyser(analyser) {
    if (!analyser) return 0;
    const data = new Uint8Array(analyser.fftSize);
    analyser.getByteTimeDomainData(data);
    let sum = 0;
    for (const value of data) {
      const normalized = (value - 128) / 128;
      sum += normalized * normalized;
    }
    const rms = Math.sqrt(sum / data.length);
    return Math.min(100, Math.round(rms * 320));
  }

  function renderLevel(bar, label, analyser, track) {
    if (!track || track.readyState !== 'live') {
      bar.style.width = '0%';
      label.textContent = 'Desconectado';
      return;
    }
    const level = levelFromAnalyser(analyser);
    bar.style.width = `${level}%`;
    label.textContent = level > 2 ? 'Recebendo áudio' : 'Silêncio';
  }

  function startLevelMonitoring() {
    sourceMonitor.classList.remove('d-none');
    meetingLevelGroup.classList.toggle('d-none', recordingMode !== 'online');
    const tick = () => {
      const micTrack = microphoneStream?.getAudioTracks()[0];
      const meetingTrack = meetingDisplayStream?.getAudioTracks()[0];
      renderLevel(microphoneLevelBar, microphoneLevelLabel, microphoneAnalyser, micTrack);
      if (recordingMode === 'online') renderLevel(meetingLevelBar, meetingLevelLabel, meetingAnalyser, meetingTrack);
      monitorFrameId = requestAnimationFrame(tick);
    };
    tick();
  }

  async function closeAudioMixer() {
    stopLevelMonitoring();
    microphoneSource = null;
    meetingSource = null;
    mixedDestination = null;
    if (audioContext) {
      const context = audioContext;
      audioContext = null;
      if (context.state !== 'closed') {
        try { await context.close(); } catch (_error) { /* cleanup best effort */ }
      }
    }
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
    meetingLevelGroup.classList.toggle('d-none', recordingMode !== 'online');

    if (recordingMode === 'online') {
      meetingAudioReadinessRow.classList.remove('d-none');
      meetingAudioControls.classList.remove('d-none');
      modeHelp.textContent = 'Modo online: selecione a aba da reunião com compartilhamento de áudio. Ao iniciar, o AMIP combinará esse áudio com o microfone local.';
      updateOnlineReadiness();
      setStatus(hasLiveMeetingAudio() ? 'Áudio da reunião selecionado. Pronto para solicitar o microfone e iniciar.' : 'Selecione a aba da reunião e habilite o compartilhamento de áudio.', hasLiveMeetingAudio() ? 'success' : 'warning');
      return;
    }

    meetingAudioReadinessRow.classList.add('d-none');
    meetingAudioControls.classList.add('d-none');
    setReadinessBadge('Pronto para solicitar microfone', 'secondary');
    modeHelp.textContent = 'Modo presencial: o navegador usará somente o microfone deste computador.';
    startBtn.disabled = false;
    setStatus('Nenhuma gravação em andamento.', 'secondary');
  }

  function stopBecauseSourceEnded(message) {
    if (!recorder || recorder.state === 'inactive') return;
    sourceFailureMessage = message;
    setReadinessBadge('Fonte desconectada', 'danger');
    setStatus(`${message} A gravação foi encerrada para evitar um arquivo incompleto.`, 'danger');
    recorder.stop();
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
      const candidate = await navigator.mediaDevices.getDisplayMedia({video: true, audio: true, preferCurrentTab: false, selfBrowserSurface: 'exclude', surfaceSwitching: 'exclude'});
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
        if (recorder && recorder.state !== 'inactive') {
          stopBecauseSourceEnded('O áudio da reunião foi interrompido.');
          return;
        }
        stopMeetingDisplayStream();
        updateOnlineReadiness();
        setStatus('O compartilhamento da aba da reunião foi encerrado. Selecione a aba novamente.', 'warning');
      };
      candidate.getVideoTracks().forEach(track => track.addEventListener('ended', onCaptureEnded, {once: true}));
      audioTracks.forEach(track => track.addEventListener('ended', onCaptureEnded, {once: true}));
      updateOnlineReadiness();
      setStatus('Áudio da reunião detectado. O vídeo compartilhado não será gravado pelo AMIP.', 'success');
    } catch (error) {
      setStatus(error?.name === 'NotAllowedError' ? 'Seleção da aba cancelada ou permissão de compartilhamento negada.' : 'Não foi possível acessar o áudio da reunião.', error?.name === 'NotAllowedError' ? 'warning' : 'danger');
      updateOnlineReadiness();
    } finally {
      meetingAudioSelectBtn.disabled = false;
    }
  }

  function formatDuration(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    return `${String(Math.floor(totalSeconds / 60)).padStart(2, '0')}:${String(totalSeconds % 60).padStart(2, '0')}`;
  }

  function stopRecorderStream() {
    if (stream && stream !== microphoneStream) stream.getTracks().forEach(track => track.stop());
    stream = null;
  }

  async function stopCaptureResources({stopMeeting = true} = {}) {
    stopRecorderStream();
    stopMicrophoneStream();
    if (stopMeeting) stopMeetingDisplayStream();
    await closeAudioMixer();
  }

  function stopTimer() { if (timerId) window.clearInterval(timerId); timerId = null; }

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
    sourceFailureMessage = '';
    renderRecordingMode();
  }

  function extensionForMime(mime) {
    const base = mime.split(';', 1)[0].toLowerCase();
    if (base === 'audio/ogg' || base === 'application/ogg') return 'ogg';
    if (base === 'audio/mp4') return 'm4a';
    return 'webm';
  }

  function preferredMimeType() {
    return ['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4'].find(type => MediaRecorder.isTypeSupported(type)) || '';
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

  function createAnalyser(sourceNode) {
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    sourceNode.connect(analyser);
    return analyser;
  }

  function attachMicrophoneEndedHandler() {
    const track = microphoneStream?.getAudioTracks()[0];
    if (!track) return;
    track.addEventListener('ended', () => stopBecauseSourceEnded('O microfone foi desconectado.'), {once: true});
  }

  async function buildOnlineMixedStream() {
    if (!hasLiveMeetingAudio()) throw new Error('MeetingAudioTrackMissing');
    microphoneStream = await requestRoomAudio();
    const microphoneTrack = microphoneStream.getAudioTracks()[0];
    if (!microphoneTrack) throw new Error('MicrophoneAudioTrackMissing');

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) throw new Error('WebAudioUnavailable');
    audioContext = new AudioContextClass();
    if (audioContext.state === 'suspended') await audioContext.resume();

    mixedDestination = audioContext.createMediaStreamDestination();
    microphoneSource = audioContext.createMediaStreamSource(microphoneStream);
    meetingSource = audioContext.createMediaStreamSource(meetingDisplayStream);
    microphoneAnalyser = createAnalyser(microphoneSource);
    meetingAnalyser = createAnalyser(meetingSource);
    microphoneSource.connect(mixedDestination);
    meetingSource.connect(mixedDestination);
    attachMicrophoneEndedHandler();

    if (!mixedDestination.stream.getAudioTracks().length) throw new Error('MixedAudioTrackMissing');
    return mixedDestination.stream;
  }

  function attachRecorderHandlers() {
    chunks = [];
    recorder.addEventListener('dataavailable', event => { if (event.data && event.data.size > 0) chunks.push(event.data); });
    recorder.addEventListener('stop', async () => {
      await stopCaptureResources();
      stopTimer();
      const failure = sourceFailureMessage;
      sourceFailureMessage = '';
      if (discardRequested) {
        resetPreview(); resetControls(); recorder = null; discardRequested = false; return;
      }
      recordedBlob = new Blob(chunks, {type: recordedMimeType});
      if (!recordedBlob.size) {
        resetControls(); discardBtn.classList.remove('d-none'); setStatus('Nenhum áudio foi capturado. Tente novamente.', 'danger'); return;
      }
      previewUrl = URL.createObjectURL(recordedBlob);
      preview.src = previewUrl;
      preview.classList.remove('d-none');
      uploadBtn.classList.remove('d-none');
      discardBtn.classList.remove('d-none');
      startBtn.classList.add('d-none');
      stopBtn.classList.add('d-none');
      stopBtn.disabled = false;
      setModeInputsDisabled(false);
      if (failure) {
        setReadinessBadge('Gravação interrompida', 'danger');
        setStatus(`${failure} O trecho gravado foi preservado para revisão, mas recomendamos descartar e gravar novamente.`, 'danger');
      } else {
        setStatus(`Gravação pronta (${(recordedBlob.size / 1024 / 1024).toFixed(2)} MB). Revise as vozes antes de enviar.`, 'success');
      }
    });
  }

  function beginRecorder(recordingStream, message) {
    stream = recordingStream;
    const mimeType = preferredMimeType();
    recorder = mimeType ? new MediaRecorder(stream, {mimeType}) : new MediaRecorder(stream);
    recordedMimeType = recorder.mimeType || mimeType || 'audio/webm';
    attachRecorderHandlers();
    recorder.start(1000);
    startedAt = Date.now();
    timer.textContent = '00:00';
    timerId = window.setInterval(() => { timer.textContent = formatDuration(Date.now() - startedAt); }, 500);
    startBtn.classList.add('d-none');
    uploadBtn.classList.add('d-none');
    discardBtn.classList.remove('d-none');
    stopBtn.classList.remove('d-none');
    stopBtn.disabled = false;
    startLevelMonitoring();
    setStatus(message, 'danger');
  }

  async function startRecording() {
    resetPreview();
    discardRequested = false;
    sourceFailureMessage = '';
    if (!window.isSecureContext) { setStatus('O microfone exige HTTPS ou localhost.', 'danger'); return; }
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') { setStatus('Este navegador não oferece gravação de áudio compatível.', 'danger'); return; }
    if (recordingMode === 'online' && !hasLiveMeetingAudio()) {
      updateOnlineReadiness(); setStatus('Selecione uma aba da reunião com áudio antes de iniciar.', 'warning'); return;
    }

    try {
      setModeInputsDisabled(true);
      meetingAudioSelectBtn.disabled = true;
      setReadinessBadge('Solicitando microfone', 'primary');
      microphoneReadiness.textContent = 'Solicitando permissão...';
      microphoneReadiness.className = 'text-primary';

      if (recordingMode === 'online') {
        const mixedStream = await buildOnlineMixedStream();
        microphoneReadiness.textContent = 'Pronto'; microphoneReadiness.className = 'text-success';
        meetingAudioReadiness.textContent = 'Pronto'; meetingAudioReadiness.className = 'text-success';
        setReadinessBadge('Microfone + reunião prontos', 'success');
        beginRecorder(mixedStream, 'Gravando microfone local + áudio da reunião. Monitore os dois níveis abaixo.');
        return;
      }

      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      microphoneStream = await requestRoomAudio();
      const audioTrack = microphoneStream.getAudioTracks()[0];
      if (!audioTrack) throw new Error('MicrophoneAudioTrackMissing');
      if (AudioContextClass) {
        audioContext = new AudioContextClass();
        if (audioContext.state === 'suspended') await audioContext.resume();
        microphoneSource = audioContext.createMediaStreamSource(microphoneStream);
        microphoneAnalyser = createAnalyser(microphoneSource);
      }
      attachMicrophoneEndedHandler();
      microphoneReadiness.textContent = 'Pronto'; microphoneReadiness.className = 'text-success'; setReadinessBadge('Pronto', 'success');
      beginRecorder(microphoneStream, 'Gravando reunião presencial. Monitore o nível do microfone abaixo.');
    } catch (error) {
      await stopCaptureResources({stopMeeting: recordingMode !== 'online'});
      setModeInputsDisabled(false);
      meetingAudioSelectBtn.disabled = false;
      setReadinessBadge('Captura indisponível', 'danger');
      microphoneReadiness.textContent = 'Indisponível'; microphoneReadiness.className = 'text-danger';
      if (recordingMode === 'online') updateOnlineReadiness();
      startBtn.disabled = recordingMode === 'online' ? !hasLiveMeetingAudio() : false;
      const denied = error && (error.name === 'NotAllowedError' || error.name === 'SecurityError');
      if (denied) setStatus('Permissão de microfone negada pelo navegador.', 'danger');
      else if (error?.message === 'WebAudioUnavailable') setStatus('Este navegador não oferece o mixer de áudio necessário para reuniões online.', 'danger');
      else setStatus('Não foi possível preparar a gravação. Verifique o microfone e o áudio da reunião.', 'danger');
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
      stopTimer();
      setStatus('Descartando gravação...', 'secondary');
      return;
    }
    void stopCaptureResources();
    resetPreview();
    recorder = null;
    resetControls();
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
        setStatus(detail, 'danger'); uploadBtn.disabled = false; discardBtn.disabled = false; return;
      }
      setStatus('Gravação enviada. Preparando a reunião para transcrição...', 'success');
      window.setTimeout(() => window.location.reload(), 500);
    } catch (_error) {
      setStatus('Falha de rede ao enviar a gravação.', 'danger'); uploadBtn.disabled = false; discardBtn.disabled = false;
    }
  }

  modeInputs.forEach(input => input.addEventListener('change', renderRecordingMode));
  meetingAudioSelectBtn.addEventListener('click', selectMeetingAudio);
  startBtn.addEventListener('click', startRecording);
  stopBtn.addEventListener('click', stopRecording);
  discardBtn.addEventListener('click', discardRecording);
  uploadBtn.addEventListener('click', uploadRecording);
  window.addEventListener('beforeunload', () => { void stopCaptureResources(); });
  renderRecordingMode();
})();
