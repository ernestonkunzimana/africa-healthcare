const API_BASE = window.AH_API_BASE || 'http://localhost:8000';
const state = {
  token: '',
  widgets: ['privacy', 'consent', 'triage', 'explainability'],
  queue: JSON.parse(localStorage.getItem('ah_offline_queue') || '[]')
};

const statusEl = document.getElementById('status');
const outputEl = document.getElementById('output');
const widgetsEl = document.getElementById('widgets');
const queueCountEl = document.getElementById('queueCount');

function setStatus(msg) {
  statusEl.textContent = `Status: ${msg}`;
}

function saveQueue() {
  localStorage.setItem('ah_offline_queue', JSON.stringify(state.queue));
  queueCountEl.textContent = String(state.queue.length);
}

async function api(path, method = 'GET', payload = null, auth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth && state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload ? JSON.stringify(payload) : undefined });
  return res.json();
}

function renderWidgets() {
  const available = [
    { id: 'privacy', label: 'Privacy & Residency' },
    { id: 'consent', label: 'Consent Manager' },
    { id: 'triage', label: 'Triage Panel' },
    { id: 'explainability', label: 'Explainability Panel' }
  ];
  widgetsEl.innerHTML = available.map((w) => `
    <label><input type="checkbox" data-widget="${w.id}" ${state.widgets.includes(w.id) ? 'checked' : ''}/> ${w.label}</label>
  `).join('');

  document.querySelectorAll('[data-widget]').forEach((el) => {
    el.addEventListener('change', async (e) => {
      const id = e.target.getAttribute('data-widget');
      if (e.target.checked) state.widgets.push(id); else state.widgets = state.widgets.filter((x) => x !== id);
      state.widgets = [...new Set(state.widgets)];
      await api('/api/preferences', 'POST', { user_id: 'clinician', widgets: state.widgets, language: 'en' });
      document.querySelectorAll('[data-panel]').forEach((p) => {
        p.style.display = state.widgets.includes(p.getAttribute('data-panel')) ? 'block' : 'none';
      });
    });
  });
}

async function syncQueue() {
  if (!navigator.onLine || !state.token || state.queue.length === 0) return;
  const remaining = [];
  for (const item of state.queue) {
    try {
      const result = await api('/api/triage', 'POST', item, true);
      outputEl.textContent = JSON.stringify({ source: 'synced-offline-request', result }, null, 2);
    } catch {
      remaining.push(item);
    }
  }
  state.queue = remaining;
  saveQueue();
}

document.getElementById('authBtn').addEventListener('click', async () => {
  setStatus('Authenticating secure session...');
  const data = await api('/auth/token', 'POST', { username: 'clinician', password: 'SecurePass123!' });
  state.token = data.access_token || '';

  const pref = await api('/api/preferences/clinician');
  if (pref.preferences?.widgets?.length) state.widgets = pref.preferences.widgets;
  renderWidgets();
  await syncQueue();
  setStatus(state.token ? 'Connected as clinician.' : 'Authentication failed.');
});

document.getElementById('privacyBtn').addEventListener('click', async () => {
  const data = await api('/api/privacy/policy');
  outputEl.textContent = JSON.stringify(data, null, 2);
  setStatus('Privacy and data residency policy loaded.');
});

document.getElementById('consentBtn').addEventListener('click', async () => {
  const data = await api('/api/consent', 'POST', {
    patient_id: document.getElementById('patientId').value,
    data_processing: document.getElementById('consentData').checked,
    ai_assistance: document.getElementById('consentAi').checked,
    emergency_override: document.getElementById('consentEmergency').checked
  });
  outputEl.textContent = JSON.stringify(data, null, 2);
  setStatus('Consent preferences saved.');
});

document.getElementById('triageBtn').addEventListener('click', async () => {
  const payload = {
    patient_id: document.getElementById('patientId').value,
    symptoms: document.getElementById('symptoms').value.split(',').map((s) => s.trim()).filter(Boolean),
    notes: document.getElementById('notes').value,
    language: 'en',
    country: document.getElementById('country').value,
    health_signal: {
      heart_rate: Number(document.getElementById('hr').value),
      spo2: Number(document.getElementById('spo2').value),
      systolic_bp: Number(document.getElementById('sbp').value),
      diastolic_bp: Number(document.getElementById('dbp').value)
    }
  };

  if (!navigator.onLine) {
    state.queue.push(payload);
    saveQueue();
    setStatus('Offline mode: triage request queued for safe sync.');
    return;
  }
  if (!state.token) {
    setStatus('Authenticate first.');
    return;
  }

  const data = await api('/api/triage', 'POST', payload, true);
  outputEl.textContent = JSON.stringify(data, null, 2);
  setStatus('Triage complete with explainability and guardrails.');
});

window.addEventListener('online', () => {
  setStatus('Network restored. Syncing offline queue...');
  syncQueue();
});
window.addEventListener('offline', () => setStatus('Offline mode enabled. Working safely with local queue.'));

queueCountEl.textContent = String(state.queue.length);
renderWidgets();
