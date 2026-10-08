(function() {
  // In-memory state storage (cleared on page refresh or logout)
  let state = {
    token: null,
    tenant_id: null,
    user_id: null,
    role: null,
    username: null,
    activeRunId: null,
    requiredSafetyStepIds: []
  };

  // Tab Navigation
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Login Form
  const loginForm = document.getElementById('login-form');
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const tenant = document.getElementById('tenant-select').value;
    const username = document.getElementById('username-input').value.trim();
    const password = document.getElementById('password-input').value;
    const errDiv = document.getElementById('login-error');
    errDiv.textContent = '';

    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: tenant, username, password })
      });

      if (!res.ok) {
        const errData = await res.json();
        errDiv.textContent = errData.detail || 'Login failed';
        return;
      }

      const data = await res.json();
      state.token = data.access_token;
      state.tenant_id = data.tenant_id;
      state.user_id = data.user_id;
      state.role = data.role;
      state.username = data.username;

      updateUserUI();
    } catch (err) {
      errDiv.textContent = 'Network error during login';
    }
  });

  // Logout
  document.getElementById('logout-btn').addEventListener('click', () => {
    state.token = null;
    state.tenant_id = null;
    state.user_id = null;
    state.role = null;
    state.username = null;
    state.activeRunId = null;
    state.requiredSafetyStepIds = [];
    updateUserUI();
  });

  function updateUserUI() {
    const userInfo = document.getElementById('user-info-text');
    const logoutBtn = document.getElementById('logout-btn');
    const supervisorTabs = document.querySelectorAll('.supervisor-only');

    if (state.token) {
      userInfo.textContent = `${state.username} (${state.role} - ${state.tenant_id})`;
      logoutBtn.style.display = 'inline-block';
      supervisorTabs.forEach(el => {
        el.style.display = (state.role === 'supervisor') ? 'inline-block' : 'none';
      });
    } else {
      userInfo.textContent = 'Not logged in';
      logoutBtn.style.display = 'none';
      supervisorTabs.forEach(el => el.style.display = 'none');
    }
  }

  // Ask Question
  document.getElementById('ask-submit-btn').addEventListener('click', async () => {
    if (!state.token) {
      alert('Please login first');
      return;
    }
    const question = document.getElementById('ask-input').value.trim();
    const output = document.getElementById('ask-output');
    if (!question) {
      output.textContent = 'Enter a question to search the manuals.';
      return;
    }
    output.replaceChildren();
    output.className = 'output-panel';
    const status = document.createElement('div');
    status.className = 'answer-status';
    const dot = document.createElement('span');
    dot.className = 'loading-dot';
    dot.setAttribute('aria-hidden', 'true');
    const statusText = document.createElement('span');
    statusText.textContent = 'Searching the manuals…';
    status.append(dot, statusText);
    output.appendChild(status);

    try {
      const res = await fetch('/ask/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${state.token}`
        },
        body: JSON.stringify({ question })
      });

      if (!res.ok) {
        let detail = `Request failed (${res.status})`;
        try { detail = (await res.json()).detail || detail; } catch (_) {}
        output.textContent = detail;
        return;
      }
      if (!res.body) throw new Error('The server did not return a response stream.');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop();
        for (const eventText of events) {
          const dataLine = eventText.split('\n').find(line => line.startsWith('data: '));
          if (!dataLine) continue;
          const eventData = JSON.parse(dataLine.slice(6));
          if (eventData.event === 'progress') {
            statusText.textContent = 'Evidence found. Preparing a concise answer…';
          } else if (eventData.event === 'done') {
            renderAskResult(output, eventData);
          } else if (eventData.event === 'error') {
            output.textContent = eventData.detail || 'Unable to answer right now.';
          }
        }
      }
    } catch (err) {
      output.textContent = 'Could not reach the service. Please try again.';
    }
  });

  function cleanAnswerText(rawText) {
    let text = String(rawText || '')
      .replace(/\\([*_`#])/g, '$1')
      .replace(/\u00a0/g, ' ')
      .replace(/\s*\[(?:rev(?:ision)?\s+[^\]]+)\]\s*/gi, ' ')
      .replace(/\s*\[chunk:\d+\]\s*([.,;:]?)/gi, '$1')
      .replace(/([.!?])(?:[ \t]*[.!?])+/g, '$1');
    const visibleLines = [];
    for (const line of text.split(/\r?\n/)) {
      if (/^\s{0,3}(?:#{1,6}\s*)?(?:citations?|sources?)\s*:?[ \t]*$/i.test(line)) break;
      if (/^\s*[-*]\s*(?:chunk\s+\d+|.*\[chunk:\d+\])/i.test(line)) continue;
      visibleLines.push(line.replace(/^\s{0,3}#{1,6}\s+/, '').replace(/^\s*[-*]\s+/, '').trim());
    }
    return visibleLines.join('\n').replace(/[ \t]{2,}/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
  }
  function appendSafeFormattedText(parent, text) {
    const pattern = /\*\*(.+?)\*\*|__(.+?)__|\*([^*\n]+)\*/g;
    let cursor = 0;
    let match;
    while ((match = pattern.exec(text)) !== null) {
      parent.appendChild(document.createTextNode(text.slice(cursor, match.index)));
      const formatted = document.createElement(match[1] || match[2] ? 'strong' : 'em');
      formatted.textContent = match[1] || match[2] || match[3];
      parent.appendChild(formatted);
      cursor = pattern.lastIndex;
    }
    parent.appendChild(document.createTextNode(text.slice(cursor)));
  }

  function renderAskResult(output, data) {
    output.replaceChildren();
    output.className = 'output-panel answer-card';
    const answerText = cleanAnswerText(data.text);
    const answer = document.createElement('div');
    answer.className = 'answer-copy';
    answerText.split(/\n\s*\n/).filter(Boolean).forEach(paragraphText => {
      const paragraph = document.createElement('p');
      appendSafeFormattedText(paragraph, paragraphText.replace(/\n/g, ' '));
      answer.appendChild(paragraph);
    });
    output.appendChild(answer);

    const citations = Array.isArray(data.citations) ? data.citations : [];
    const uniqueSources = new Map();
    citations.forEach(citation => {
      const key = [citation.doc_id, citation.section, citation.revision, citation.page].join('|');
      if (!uniqueSources.has(key)) uniqueSources.set(key, citation);
    });
    if (uniqueSources.size) {
      const sources = document.createElement('section');
      sources.className = 'answer-sources';
      const heading = document.createElement('h3');
      heading.textContent = 'Sources';
      const list = document.createElement('ul');
      list.className = 'source-list';
      uniqueSources.forEach(citation => {
        const item = document.createElement('li');
        const parts = [citation.doc_id, citation.section, citation.revision]
          .filter(value => value && String(value).trim());
        if (citation.page) parts.push(`p. ${citation.page}`);
        item.textContent = parts.join(' · ');
        list.appendChild(item);
      });
      sources.append(heading, list);
      output.appendChild(sources);
    }
  }
  document.getElementById('refresh-asks-btn').addEventListener('click', async () => {
    const panel = document.getElementById('ask-history');
    if (!state.token) { panel.textContent = 'Please login first'; return; }
    const response = await fetch('/asks', { headers: { 'Authorization': `Bearer ${state.token}` } });
    if (!response.ok) { panel.textContent = `Could not load history (${response.status})`; return; }
    const rows = await response.json();
    panel.textContent = '';
    rows.forEach(row => {
      const article = document.createElement('article');
      const question = document.createElement('p');
      question.textContent = `Question: ${row.question}`;
      const answer = document.createElement('p');
      answer.textContent = row.answer_text;
      article.append(question, answer);
      panel.appendChild(article);
    });
  });

  // Workflow Run Phase 1: Start
  document.getElementById('start-run-btn').addEventListener('click', async () => {
    if (!state.token) { alert('Please login first'); return; }
    const symptoms = document.getElementById('symptoms-input').value;
    const rev = document.getElementById('revision-input').value;
    const prog = document.getElementById('run-progress');
    prog.textContent = 'Starting workflow...';

    try {
      const res = await fetch('/runs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${state.token}`
        },
        body: JSON.stringify({ symptoms, installed_revision: rev || null })
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (!dataStr) continue;
            try {
              const eventData = JSON.parse(dataStr);
              if (eventData.run_id) {
                state.activeRunId = eventData.run_id;
                document.getElementById('cancel-run-btn').disabled = false;
              }

              const div = document.createElement('div');
              div.textContent = `[${eventData.event}] ${eventData.summary || eventData.status || ''}`;
              prog.appendChild(div);

              if (eventData.event === 'done') {
                state.requiredSafetyStepIds = eventData.required_safety_step_ids || [];
                renderSafetyChecklist(state.requiredSafetyStepIds);
                document.getElementById('cancel-run-btn').disabled = true;
              }
            } catch (e) {}
          }
        }
      }
    } catch (err) {
      prog.textContent = 'Error starting run: ' + err.message;
    }
  });

  document.getElementById('cancel-run-btn').addEventListener('click', async () => {
    if (!state.activeRunId || !state.token) return;
    const response = await fetch(`/runs/${state.activeRunId}/cancel`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (response.ok) {
      document.getElementById('run-progress').textContent += '\nRun cancellation requested.';
      document.getElementById('cancel-run-btn').disabled = true;
    }
  });

  function renderSafetyChecklist(ids) {
    const panel = document.getElementById('safety-gate-panel');
    const container = document.getElementById('safety-checklist');
    container.textContent = '';
    panel.style.display = 'block';

    if (!ids || ids.length === 0) {
      const p = document.createElement('p');
      p.textContent = 'No required safety steps. Click submit to proceed.';
      container.appendChild(p);
      return;
    }

    ids.forEach(id => {
      const label = document.createElement('label');
      label.style.display = 'block';
      const chk = document.createElement('input');
      chk.type = 'checkbox';
      chk.value = id;
      chk.classList.add('safety-chk');
      label.appendChild(chk);
      label.appendChild(document.createTextNode(` Acknowledge Safety Step ID: ${id}`));
      container.appendChild(label);
    });
  }

  // Acknowledge Safety Checklist
  document.getElementById('acknowledge-btn').addEventListener('click', async () => {
    if (!state.activeRunId) { alert('No active run'); return; }
    const checkboxes = document.querySelectorAll('.safety-chk:checked');
    const stepIds = Array.from(checkboxes).map(c => parseInt(c.value, 10));

    const resultPanel = document.getElementById('work-order-result');
    resultPanel.textContent = 'Generating work order...';

    try {
      const res = await fetch(`/runs/${state.activeRunId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${state.token}`
        },
        body: JSON.stringify({ step_ids: stepIds })
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (!dataStr) continue;
            try {
              const eventData = JSON.parse(dataStr);
              if (eventData.event === 'work_order' || eventData.event === 'done') {
                const wo = eventData.work_order || eventData.content;
                if (wo) {
                  resultPanel.textContent = '';
                  const h3 = document.createElement('h3');
                  h3.textContent = wo.title || 'Work Order Draft';
                  resultPanel.appendChild(h3);

                  const p = document.createElement('p');
                  p.textContent = wo.summary || '';
                  resultPanel.appendChild(p);
                }
              }
            } catch (e) {}
          }
        }
      }
    } catch (err) {
      resultPanel.textContent = 'Error: ' + err.message;
    }
  });
})();
