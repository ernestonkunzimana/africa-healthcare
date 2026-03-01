import { useMemo, useState } from 'react';
import { HoloCard } from '../components/HoloCard';

type TriageResponse = {
  recommendation: string;
  urgency: string;
  actions: string[];
  alignment: {
    risk_level: string;
    confidence: number;
    safety_checks: string[];
  };
  generated_at: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

export function App() {
  const [token, setToken] = useState<string>('');
  const [result, setResult] = useState<TriageResponse | null>(null);
  const [status, setStatus] = useState('Idle');

  const payload = useMemo(
    () => ({
      patient_id: 'P-DEMO-0001',
      symptoms: ['fatigue', 'headache', 'fever'],
      notes: 'Patient reports recurring discomfort and reduced appetite.',
      language: 'en',
      health_signal: {
        heart_rate: 95,
        spo2: 94,
        systolic_bp: 140,
        diastolic_bp: 88
      }
    }),
    []
  );

  const login = async () => {
    setStatus('Authenticating secure session...');
    const response = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'clinician', password: 'SecurePass123!' })
    });
    const data = await response.json();
    setToken(data.access_token);
    setStatus('Connected as clinician.');
  };

  const runTriage = async () => {
    if (!token) {
      setStatus('Authenticate first.');
      return;
    }

    setStatus('Running aligned clinical cognition model...');
    const response = await fetch(`${API_BASE}/api/triage`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = (await response.json()) as TriageResponse;
    setResult(data);
    setStatus('Triage complete with human-in-the-loop guardrails.');
  };

  return (
    <main className="app-shell">
      <h1>Africa Healthcare Nexus • 2032 Ready</h1>
      <p className="subtitle">
        Secure-by-design AI triage, cognitive emulation UX, and safety-governed clinical workflows.
      </p>

      <div className="grid">
        <HoloCard title="Command Center">
          <button onClick={login}>1) Authenticate Clinician</button>
          <button onClick={runTriage}>2) Run AI Triage</button>
          <p className="status">Status: {status}</p>
        </HoloCard>

        <HoloCard title="Live Recommendation">
          {!result ? (
            <p>No recommendation yet.</p>
          ) : (
            <>
              <p><strong>Urgency:</strong> {result.urgency}</p>
              <p>{result.recommendation}</p>
              <p>
                <strong>Alignment:</strong> {result.alignment.risk_level} ({Math.round(result.alignment.confidence * 100)}%)
              </p>
              <ul>
                {result.actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ul>
            </>
          )}
        </HoloCard>
      </div>
    </main>
  );
}
