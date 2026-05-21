const API_BASE = `http://${window.location.hostname}:8000/api`;

export async function fetchRobots() {
  const res = await fetch(`${API_BASE}/robots`);
  return res.json();
}

export async function fetchLogs(limit = 100) {
  const res = await fetch(`${API_BASE}/logs?limit=${limit}`);
  return res.json();
}
