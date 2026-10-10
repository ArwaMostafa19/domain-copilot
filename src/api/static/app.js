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
      clearUserContent();
      state.token = data.access_token;
      state.tenant_id = data.tenant_id;
      state.user_id = data.user_id;
      state.role = data.role;
      state.username = data.username;

      updateUserUI();
      loadUsage();
      showTab('login-tab');
    } catch (err) {
      errDiv.textContent = 'Network error during login';
    }
  });

  // Logout
  document.getElementById('logout-btn').addEventListener('click', () => {
    clearUserContent();
    state.token = null;
    state.tenant_id = null;
    state.user_id = null;
    state.role = null;
    state.username = null;
    state.activeRunId = null;
    state.requiredSafetyStepIds = [];
    updateUserUI();
    showTab('login-tab');
  });

  function showTab(targetId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === targetId);
    });
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.toggle('active', tab.id === targetId);
    });
  }

  function clearUserContent() {
    [
      'ask-input', 'ask-output', 'ask-history', 'symptoms-input', 'run-progress',
      'safety-checklist', 'work-order-result', 'run-trace-detail', 'runs-tbody',
      'docs-tbody', 'docs-status', 'login-error', 'username-input', 'password-input'
    ].forEach(id => {
      const element = document.getElementById(id);
      if (element) element.textContent = '';
    });
    ['safety-gate-panel', 'continue-workflow-btn'].forEach(id => {
      const element = document.getElementById(id);
      if (element) element.style.display = 'none';
    });
    document.getElementById('cancel-run-btn').disabled = true;
    ['login-usage-panel', 'ask-usage-panel'].forEach(id => {
      document.getElementById(id).textContent = 'Sign in to view usage.';
    });
  }

  function updateUserUI() {
    const userInfo = document.getElementById('user-info-text');
    const logoutBtn = document.getElementById('logout-btn');
    const supervisorTabs = document.querySelectorAll('.supervisor-only');

    if (state.token) {
      userInfo.textContent = state.username;
      logoutBtn.style.display = 'inline-block';
      supervisorTabs.forEach(el => {
        el.style.display = (state.role === 'supervisor') ? 'inline-block' : 'none';
      });
    } else {
      userInfo.textContent = 'Not logged in';
      logoutBtn.style.display = 'none';
      supervisorTabs.forEach(el => el.style.display = 'none');
      document.getElementById('login-usage-panel').textContent = 'Usage is available after login.';
      document.getElementById('ask-usage-panel').textContent = 'Sign in to view usage.';
    }
  }

  document.getElementById('refresh-usage-btn').addEventListener('click', loadUsage);

  async function loadUsage() {
    const loginPanel = document.getElementById('login-usage-panel');
    const askPanel = document.getElementById('ask-usage-panel');
    if (!state.token) {
      loginPanel.textContent = 'Usage is available after login.';
      askPanel.textContent = 'Sign in to view usage.';
      return;
    }
    loginPanel.textContent = 'Loading usage…';
    askPanel.textContent = 'Loading usage…';
    try {
      const response = await fetch('/usage', { headers: { 'Authorization': `Bearer ${state.token}` } });
      if (!response.ok) throw new Error(`Usage unavailable (${response.status})`);
      const data = await response.json();
      const asks = data.daily_asks || [];
      const runs = data.daily_runs || [];
      const askTokens = asks.reduce((sum, row) => sum + Number(row.prompt_tokens || 0) + Number(row.completion_tokens || 0), 0);
      const runTokens = runs.reduce((sum, row) => sum + Number(row.total_tokens || 0), 0);
      const summary = `${askTokens.toLocaleString()} question tokens · ${runTokens.toLocaleString()} workflow tokens · ${(asks.reduce((sum, row) => sum + Number(row.ask_count || 0), 0)).toLocaleString()} questions · ${(runs.reduce((sum, row) => sum + Number(row.run_count || 0), 0)).toLocaleString()} workflows`;
      loginPanel.textContent = summary;
      askPanel.textContent = summary;
    } catch (error) {
      loginPanel.textContent = error.message;
      askPanel.textContent = error.message;
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
            statusText.textContent = 'Related passages found. Checking whether they support an answer…';
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
    output.className = data.refused
      ? 'output-panel answer-card refusal-card'
      : 'output-panel answer-card';
    output.setAttribute('role', data.refused ? 'status' : 'region');
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
    const prog = document.getElementById('run-progress');
    state.activeRunId = null;
    state.requiredSafetyStepIds = [];
    document.getElementById('safety-gate-panel').style.display = 'none';
    document.getElementById('continue-workflow-btn').style.display = 'none';
    document.getElementById('safety-checklist').textContent = '';
    document.getElementById('work-order-result').textContent = '';
    document.getElementById('cancel-run-btn').disabled = true;
    prog.textContent = 'Starting workflow...';

    try {
      const res = await fetch('/runs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${state.token}`
        },
        body: JSON.stringify({ symptoms, installed_revision: null })
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

              if (eventData.event === 'error') {
                const error = document.createElement('p');
                error.textContent = eventData.detail || 'Workflow could not find supported equipment information.';
                prog.appendChild(error);
                document.getElementById('cancel-run-btn').disabled = true;
                document.getElementById('safety-gate-panel').style.display = 'none';
                document.getElementById('continue-workflow-btn').style.display = 'none';
                refreshRuns();
                continue;
              }

              const div = document.createElement('div');
              div.textContent = `[${eventData.event}] ${eventData.summary || eventData.status || ''}`;
              prog.appendChild(div);

              if (eventData.event === 'done') {
                renderSafetyChecklist(eventData.required_safety_steps || []);
                document.getElementById('cancel-run-btn').disabled = true;
                refreshRuns();
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

  function renderSafetyChecklist(steps) {
    const panel = document.getElementById('safety-gate-panel');
    const container = document.getElementById('safety-checklist');
    const continueButton = document.getElementById('continue-workflow-btn');
    container.textContent = '';
    panel.style.display = 'none';
    continueButton.style.display = 'none';
    const safetySteps = Array.isArray(steps) ? steps : [];
    state.requiredSafetyStepIds = safetySteps.map(step => Number(step.id));
    document.getElementById('safety-prereq-count').textContent =
      `Review and acknowledge all ${safetySteps.length} required safety steps before proceeding:`;

    if (state.requiredSafetyStepIds.length === 0) {
      continueButton.style.display = 'inline-block';
      return;
    }

    panel.style.display = 'block';
    safetySteps.forEach(step => {
      const label = document.createElement('label');
      label.style.display = 'block';
      const chk = document.createElement('input');
      chk.type = 'checkbox';
      chk.value = step.id;
      chk.classList.add('safety-chk');
      label.appendChild(chk);
      const description = document.createElement('span');
      description.className = 'safety-step-copy';
      description.textContent = ` ${step.doc_id} — step ${step.step_no}: ${step.text}`;
      label.appendChild(description);
      container.appendChild(label);
    });
  }

  // Acknowledge Safety Checklist
  async function submitAcknowledgements(stepIds) {
    if (!state.activeRunId) { alert('No active run'); return; }
    const safetyPanel = document.getElementById('safety-gate-panel');
    const continueButton = document.getElementById('continue-workflow-btn');
    safetyPanel.style.display = 'none';
    continueButton.style.display = 'none';
    const resultPanel = document.getElementById('work-order-result');
    const acknowledgeButton = document.getElementById('acknowledge-btn');
    acknowledgeButton.disabled = true;
    resultPanel.textContent = 'Generating work order...';
    let generationFailed = false;
    let generationSucceeded = false;

    try {
      const res = await fetch(`/runs/${state.activeRunId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${state.token}`
        },
        body: JSON.stringify({ step_ids: stepIds })
      });
      if (!res.ok) {
        let detail = `Request failed (${res.status})`;
        try { detail = (await res.json()).detail || detail; } catch (_) {}
        resultPanel.textContent = detail;
        if (state.requiredSafetyStepIds.length) safetyPanel.style.display = 'block';
        return;
      }

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
                  safetyPanel.style.display = 'none';
                  continueButton.style.display = 'none';
                  generationSucceeded = true;
                }
              }
              if (eventData.event === 'error') {
                resultPanel.textContent = eventData.detail || 'Work order generation failed.';
                generationFailed = true;
                if (eventData.detail === 'safety acknowledgement required') {
                  safetyPanel.style.display = 'block';
                }
              }
            } catch (e) {}
          }
        }
      }
    } catch (err) {
      resultPanel.textContent = 'Error: ' + err.message;
      generationFailed = true;
      if (state.requiredSafetyStepIds.length) safetyPanel.style.display = 'block';
    } finally {
      acknowledgeButton.disabled = false;
    }
    if (generationSucceeded || generationFailed) refreshRuns();
  }

  document.getElementById('acknowledge-btn').addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.safety-chk:checked');
    const stepIds = Array.from(checkboxes).map(c => parseInt(c.value, 10));
    submitAcknowledgements(stepIds);
  });

  document.getElementById('continue-workflow-btn').addEventListener('click', () => {
    submitAcknowledgements([]);
  });

  document.getElementById('refresh-runs-btn').addEventListener('click', refreshRuns);
  document.getElementById('refresh-docs-btn').addEventListener('click', refreshDocuments);

  async function refreshRuns() {
    const body = document.getElementById('runs-tbody');
    body.textContent = '';
    if (!state.token) {
      appendTableMessage(body, 4, 'Sign in to view workflow runs.');
      return;
    }
    try {
      const response = await fetch('/runs', {
        headers: { 'Authorization': `Bearer ${state.token}` }
      });
      if (!response.ok) throw new Error(`Could not load runs (${response.status})`);
      const runs = await response.json();
      if (!runs.length) {
        appendTableMessage(body, 4, 'No workflow runs yet.');
        return;
      }
      runs.forEach(run => {
        const row = document.createElement('tr');
        [run.id, run.question, run.status]
          .forEach(value => {
            const cell = document.createElement('td');
            cell.textContent = value == null ? '' : String(value);
            row.appendChild(cell);
          });
        const action = document.createElement('td');
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = 'View trace';
        button.addEventListener('click', () => loadRunTrace(run.id));
        action.appendChild(button);
        row.appendChild(action);
        body.appendChild(row);
      });
    } catch (error) {
      appendTableMessage(body, 4, error.message);
    }
  }

  async function loadRunTrace(runId) {
    const panel = document.getElementById('run-trace-detail');
    panel.textContent = 'Loading execution trace...';
    try {
      const response = await fetch(`/runs/${encodeURIComponent(runId)}`, {
        headers: { 'Authorization': `Bearer ${state.token}` }
      });
      if (!response.ok) throw new Error(`Could not load trace (${response.status})`);
      const run = await response.json();
      panel.textContent = '';
      const heading = document.createElement('h3');
      heading.textContent = `Run ${run.id} · ${run.status}`;
      panel.appendChild(heading);
      const question = document.createElement('p');
      question.textContent = run.question || '';
      panel.appendChild(question);
      (run.steps || []).forEach(step => {
        const item = document.createElement('p');
        item.textContent = `${step.ordinal}. ${step.agent} — ${step.summary || step.outcome}; ` +
          `tools: ${(step.tools_used || []).join(', ') || 'none'}; ` +
          `evidence chunks: ${(step.evidence_ids || []).join(', ') || 'none'}; ` +
          `tokens: ${Number(step.prompt_tokens || 0) + Number(step.completion_tokens || 0)}`;
        panel.appendChild(item);
      });
      if (run.work_order) {
        const status = document.createElement('p');
        status.textContent = `Work order: ${run.work_order.status}`;
        panel.appendChild(status);
      }
    } catch (error) {
      panel.textContent = error.message;
    }
  }

  async function refreshDocuments() {
    const body = document.getElementById('docs-tbody');
    const status = document.getElementById('docs-status');
    body.textContent = '';
    status.textContent = '';
    if (!state.token) {
      appendTableMessage(body, 6, 'Sign in to view tenant documents.');
      return;
    }
    try {
      const response = await fetch('/documents', {
        headers: { 'Authorization': `Bearer ${state.token}` }
      });
      if (!response.ok) throw new Error(`Could not load documents (${response.status})`);
      const documents = await response.json();
      if (!documents.length) {
        appendTableMessage(body, 6, 'No documents found for this tenant.');
        return;
      }
      documents.forEach(documentInfo => {
        const row = document.createElement('tr');
        [documentInfo.doc_id, documentInfo.title, documentInfo.equipment_id,
          documentInfo.revision, documentInfo.status, documentInfo.chunk_count]
          .forEach(value => {
            const cell = document.createElement('td');
            cell.textContent = value == null ? '' : String(value);
            row.appendChild(cell);
          });
        body.appendChild(row);
      });
    } catch (error) {
      appendTableMessage(body, 6, error.message);
    }
  }

  function appendTableMessage(body, columnCount, message) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = columnCount;
    cell.textContent = message;
    row.appendChild(cell);
    body.appendChild(row);
  }

  document.getElementById('ingest-btn').addEventListener('click', async () => {
    const status = document.getElementById('docs-status');
    if (!state.token || state.role !== 'supervisor') {
      status.textContent = 'Supervisor access is required to re-ingest documents.';
      return;
    }
    status.textContent = 'Re-ingesting this tenant’s corpus...';
    document.getElementById('ingest-btn').disabled = true;
    try {
      const response = await fetch('/ingest/corpus', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${state.token}` }
      });
      if (!response.ok) {
        let detail = `Ingestion failed (${response.status})`;
        try { detail = (await response.json()).detail || detail; } catch (_) {}
        throw new Error(detail);
      }
      if (!response.body) throw new Error('Ingestion response had no event stream.');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let completed = false;
      let ingested = 0;
      let skipped = 0;
      let failed = 0;
      const failures = [];
      while (true) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';
        for (const event of events) {
          const line = event.split('\n').find(part => part.startsWith('data: '));
          if (!line) continue;
          let data;
          try { data = JSON.parse(line.slice(6)); } catch (_) { continue; }
          if (data.event === 'document') {
            if (data.status === 'ingested') ingested += 1;
            else if (data.status === 'skipped') skipped += 1;
            else if (data.status === 'failed') {
              failed += 1;
              failures.push(`${data.path}: ${data.error || 'unknown error'}`);
            }
            status.textContent = `Re-ingesting… ${ingested} ingested, ${skipped} unchanged, ${failed} failed.`;
          } else if (data.event === 'error') {
            throw new Error(data.detail || 'Ingestion failed.');
          } else if (data.event === 'completed') {
            completed = true;
          }
        }
        if (done) break;
      }
      if (buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.slice(6));
          if (data.event === 'completed') completed = true;
        } catch (_) {}
      }
      status.textContent = completed
        ? `Re-ingest complete: ${ingested} ingested, ${skipped} unchanged, ${failed} failed.`
        : `Ingestion ended early: ${ingested} ingested, ${skipped} unchanged, ${failed} failed.`;
      if (failures.length) status.textContent += ` ${failures.join(' | ')}`;
      await refreshDocuments();
    } catch (error) {
      status.textContent = error.message;
    } finally {
      document.getElementById('ingest-btn').disabled = false;
    }
  });
})();
