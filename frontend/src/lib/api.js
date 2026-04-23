const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function checkSingleUrl(url) {
  const res = await fetch(`${API_BASE}/check-page`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error('Single URL check failed');
  return res.json();
}

export async function checkBulk(urls) {
  const res = await fetch(`${API_BASE}/check-bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls }),
  });
  if (!res.ok) throw new Error('Bulk check failed');
  return res.json();
}

export async function getJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error('Failed to get job status');
  return res.json();
}

export const getCsvUrl = (jobId) => `${API_BASE}/jobs/${jobId}/summary.csv`;
