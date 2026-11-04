/* Visualização de páginas do agente (somente leitura; não controla mouse/teclado). */
(() => {
  const $v = (id) => document.getElementById(id);
  const panel = $v('browserViewer');
  const toggle = $v('peek');
  const status = $v('viewerStatus');
  const image = $v('viewerImage');
  const title = $v('viewerTitle');
  const address = $v('viewerAddress');
  const tabs = $v('viewerTabs');
  const agentButton = $v('followAgent');

  let socket = null;
  let wanted = false;
  let retry = null;
  let lastTabs = '';
  let lastAutoTask = null;
  let following = true;

  function wsUrl() {
    return (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/view';
  }

  function send(payload) {
    if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify(payload));
  }

  function drawTabs(items) {
    const signature = JSON.stringify(items.map((tab) => [tab.id, tab.title]));
    if (signature === lastTabs) return;
    lastTabs = signature;
    const current = tabs.value;
    tabs.replaceChildren();
    const auto = document.createElement('option');
    auto.value = '';
    auto.textContent = 'Aba do agente (automático)';
    tabs.append(auto);
    for (const tab of items) {
      const option = document.createElement('option');
      option.value = tab.id;
      option.textContent = tab.title || tab.url || 'Nova aba';
      option.title = tab.url || '';
      tabs.append(option);
    }
    if ([...tabs.options].some((opt) => opt.value === current)) tabs.value = current;
    else {
      tabs.value = '';
      following = true;
    }
  }

  function connect() {
    if (!wanted || socket) return;
    const ws = new WebSocket(wsUrl());
    socket = ws;
    status.textContent = 'Conectando à visualização privada…';

    ws.onmessage = (event) => {
      if (socket !== ws || !wanted) return;
      let data;
      try { data = JSON.parse(event.data); } catch { return; }
      if (data.type === 'status') {
        status.textContent = data.text || 'Aguardando imagem…';
      } else if (data.type === 'frame') {
        image.src = 'data:image/jpeg;base64,' + data.image;
        image.hidden = false;
        title.textContent = data.title || 'Página do navegador';
        address.textContent = data.url || '';
        address.title = data.url || '';
        drawTabs(data.tabs || []);
        following = Boolean(data.following);
        agentButton.disabled = following;
        status.textContent = following
          ? 'Ao vivo · acompanhando a aba do agente · somente leitura'
          : 'Ao vivo · aba selecionada · somente leitura';
      }
    };
    ws.onerror = () => { status.textContent = 'Falha na conexão de imagem.'; };
    ws.onclose = () => {
      if (socket !== ws) return;
      socket = null;
      if (wanted) {
        status.textContent = 'Reconectando ao navegador…';
        retry = setTimeout(async () => {
          retry = null;
          try { await fetch('/', { cache: 'no-store', credentials: 'same-origin' }); } catch {}
          connect();
        }, 2200);
      }
    };
  }

  function open() {
    if (wanted) return;
    wanted = true;
    panel.hidden = false;
    toggle.textContent = 'Ocultar visualização';
    connect();
  }

  function close() {
    wanted = false;
    if (retry) clearTimeout(retry);
    retry = null;
    const old = socket;
    socket = null;
    if (old) old.close();
    panel.hidden = true;
    image.removeAttribute('src');
    image.hidden = true;
    title.textContent = 'Navegador do agente';
    status.textContent = 'Visualização desligada';
    toggle.textContent = '◉ Ver ao vivo';
  }

  toggle.onclick = () => wanted ? close() : open();
  tabs.onchange = () => {
    following = !tabs.value;
    agentButton.disabled = following;
    send(tabs.value ? { type: 'select_tab', target_id: tabs.value } : { type: 'follow_agent' });
  };
  agentButton.onclick = () => {
    tabs.value = '';
    following = true;
    agentButton.disabled = true;
    send({ type: 'follow_agent' });
  };

  // Quando a conversa inicia uma tarefa nova, exibe a navegação sem exigir outro clique.
  window.autoOpenBrowserPreview = (taskId) => {
    if (taskId && taskId !== lastAutoTask) {
      lastAutoTask = taskId;
      open();
    }
  };

  window.addEventListener('pagehide', close);
})();
