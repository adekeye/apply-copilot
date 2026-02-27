const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export type Job = {
  id: number;
  source: string;
  title: string;
  company: string;
  url?: string;
  extracted: {
    responsibilities: string[];
    must_have_skills: string[];
    nice_to_have_skills: string[];
    location: string;
    seniority: string;
    compensation?: string;
  };
  score?: number;
  score_explanation?: Record<string, unknown>;
  status: string;
  created_at: string;
};

function authHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem("copilot_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

export async function uploadResume(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/resume/upload`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: form
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function importJobs(jobs: Array<Record<string, unknown>>) {
  const res = await fetch(`${API_BASE}/jobs/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ jobs })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listJobs(status?: string, minScore?: number) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (typeof minScore === "number") params.set("min_score", String(minScore));
  const res = await fetch(`${API_BASE}/jobs?${params.toString()}`, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJob(id: string) {
  const res = await fetch(`${API_BASE}/jobs/${id}`, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function scoreJob(id: string) {
  const res = await fetch(`${API_BASE}/jobs/${id}/score`, { method: "POST", headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateForJob(id: string) {
  const res = await fetch(`${API_BASE}/jobs/${id}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ include_cover_letter: true, include_answers: true })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateStatus(id: string, status: string) {
  const res = await fetch(`${API_BASE}/jobs/${id}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
