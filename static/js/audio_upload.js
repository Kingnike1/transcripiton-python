(() => {
  const root = document.querySelector('main[data-meeting-id]');
  const form = document.getElementById('audioForm');
  const input = document.getElementById('audioFile');
  const info = document.getElementById('audioInfo');
  const notice = document.getElementById('notice');
  if (!root || !form || !input || !info || !notice) return;

  const meetingId = Number(root.dataset.meetingId);
  let policy = null;
  let replaceMode = false;

  const button = form.querySelector('button[type="submit"]');
  const helper = document.createElement('div');
  helper.className = 'small text-secondary mb-3';
  input.insertAdjacentElement('afterend', helper);

  const dropZone = document.createElement('div');
  dropZone.className = 'border border-2 border-dashed rounded p-3 mb-3 text-center bg-light';
  dropZone.innerHTML = '<strong>Arraste o áudio aqui</strong><div class="small text-secondary">ou selecione o arquivo abaixo</div>';
  form.insertBefore(dropZone, input);

  const progressWrap = document.createElement('div');
  progressWrap.className = 'd-none mb-3';
  progressWrap.innerHTML = '<div class="d-flex justify-content-between small mb-1"><span id="uploadState">Enviando áudio</span><strong id="uploadPercent">0%</strong></div><div class="progress" role="progressbar" aria-label="Progresso do upload" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div id="uploadProgress" class="progress-bar" style="width:0%"></div></div>';
  form.insertBefore(progressWrap, button);

  const replaceButton = document.createElement('button');
  replaceButton.type = 'button';
  replaceButton.className = 'btn btn-sm btn-outline-primary mt-2 d-none';
  replaceButton.textContent = 'Substituir áudio';
  info.insertAdjacentElement('afterend', replaceButton);

  function publicError(data, fallback) {
    if (data && typeof data.detail === 'string') return data.detail;
    return fallback;
  }

  function setNotice(message, kind) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${kind}`;
    alert.textContent = message;
    notice.replaceChildren(alert);
  }

  function updatePolicyHelp() {
    if (!policy) return;
    const formats = (policy.allowed_extensions || []).join(', ');
    helper.textContent = `Formatos: ${formats}. Limite: ${policy.max_size_mb} MB.`;
    replaceButton.classList.toggle('d-none', !policy.can_replace);
    if (policy.has_audio && !policy.can_replace && policy.replace_reason) {
      replaceButton.title = policy.replace_reason;
    }
  }

  function validateFile(file) {
    if (!file) return 'Selecione um arquivo de áudio.';
    if (policy && file.size > policy.max_size_bytes) return `O arquivo excede o limite de ${policy.max_size_mb} MB.`;
    if (policy) {
      const dot = file.name.lastIndexOf('.');
      const extension = dot >= 0 ? file.name.slice(dot).toLowerCase() : '';
      if (!(policy.allowed_extensions || []).includes(extension)) return `Formato ${extension || 'sem extensão'} não suportado.`;
    }
    return null;
  }

  function chooseFile(file) {
    if (!file) return;
    try {
      const transfer = new DataTransfer();
      transfer.items.add(file);
      input.files = transfer.files;
    } catch (_error) {
      return;
    }
    const problem = validateFile(file);
    if (problem) setNotice(problem, 'warning');
    else helper.textContent = `${file.name} • ${(file.size / 1024 / 1024).toFixed(2)} MB`;
  }

  async function refreshPolicy() {
    try {
      const response = await fetch(`/api/meetings/${meetingId}/audio/policy`);
      if (!response.ok) return;
      policy = await response.json();
      updatePolicyHelp();
    } catch (_error) {
      helper.textContent = 'Não foi possível carregar as regras do upload. A validação do servidor continua ativa.';
    }
  }

  function setProgress(percent, label = 'Enviando áudio') {
    const value = Math.max(0, Math.min(100, percent));
    progressWrap.classList.remove('d-none');
    progressWrap.querySelector('#uploadState').textContent = label;
    progressWrap.querySelector('#uploadPercent').textContent = `${value}%`;
    const bar = progressWrap.querySelector('#uploadProgress');
    bar.style.width = `${value}%`;
    bar.parentElement.setAttribute('aria-valuenow', String(value));
  }

  function upload(file) {
    const problem = validateFile(file);
    if (problem) {
      setNotice(problem, 'warning');
      return;
    }
    const body = new FormData();
    body.append('file', file);
    const xhr = new XMLHttpRequest();
    const suffix = replaceMode ? '?replace=true' : '';
    xhr.open('POST', `/api/meetings/${meetingId}/audio${suffix}`);
    button.disabled = true;
    input.disabled = true;
    setProgress(0);
    xhr.upload.addEventListener('progress', event => {
      if (event.lengthComputable) setProgress(Math.round((event.loaded / event.total) * 100));
    });
    xhr.addEventListener('load', () => {
      button.disabled = false;
      input.disabled = false;
      let data = {};
      try { data = JSON.parse(xhr.responseText || '{}'); } catch (_error) {}
      if (xhr.status >= 200 && xhr.status < 300) {
        setProgress(100, replaceMode ? 'Áudio substituído' : 'Upload concluído');
        setNotice(replaceMode ? 'Áudio substituído com segurança.' : 'Áudio enviado. Agora você pode iniciar a transcrição.', 'success');
        window.setTimeout(() => window.location.reload(), 500);
        return;
      }
      progressWrap.classList.add('d-none');
      setNotice(publicError(data, 'Não foi possível enviar o áudio.'), xhr.status === 503 ? 'warning' : 'danger');
      refreshPolicy();
    });
    xhr.addEventListener('error', () => {
      button.disabled = false;
      input.disabled = false;
      progressWrap.classList.add('d-none');
      setNotice('A conexão foi interrompida durante o upload. O arquivo não foi processado; tente novamente.', 'danger');
    });
    xhr.send(body);
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    event.stopImmediatePropagation();
    upload(input.files && input.files[0]);
  }, true);

  dropZone.addEventListener('dragover', event => { event.preventDefault(); dropZone.classList.add('border-primary'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-primary'));
  dropZone.addEventListener('drop', event => {
    event.preventDefault();
    dropZone.classList.remove('border-primary');
    chooseFile(event.dataTransfer && event.dataTransfer.files[0]);
  });
  input.addEventListener('change', () => chooseFile(input.files && input.files[0]));
  replaceButton.addEventListener('click', () => {
    replaceMode = true;
    form.classList.remove('d-none');
    button.textContent = 'Substituir áudio';
    helper.textContent = 'Escolha o novo arquivo. O áudio atual só será removido após o novo upload ser validado e salvo.';
    input.focus();
  });

  refreshPolicy();
})();
