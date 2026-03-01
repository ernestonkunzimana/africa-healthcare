const API_BASE = window.AH_API_BASE || 'http://localhost:8000';
let token = '';
const statusEl = document.getElementById('status');
const outputEl = document.getElementById('output');

document.getElementById('authBtn').addEventListener('click', async () => {
  statusEl.textContent = 'Status: Authenticating secure session...';
  const res = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'clinician', password: 'SecurePass123!' })
  });
  const data = await res.json();
  token = data.access_token || '';
  statusEl.textContent = token ? 'Status: Connected as clinician.' : 'Status: Authentication failed.';
});

document.getElementById('triageBtn').addEventListener('click', async () => {
  if (!token) return (statusEl.textContent = 'Status: Authenticate first.');
  statusEl.textContent = 'Status: Running aligned clinical cognition model...';
  const res = await fetch(`${API_BASE}/api/triage`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      patient_id: 'P-DEMO-0001',
      symptoms: ['fatigue', 'headache', 'fever'],
      notes: 'Patient reports recurring discomfort and reduced appetite.',
      language: 'en',
      health_signal: { heart_rate: 95, spo2: 94, systolic_bp: 140, diastolic_bp: 88 }
    })
  });
  const data = await res.json();
  outputEl.textContent = JSON.stringify(data, null, 2);
  statusEl.textContent = 'Status: Triage complete with human-in-the-loop guardrails.';
});
