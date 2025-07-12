export {};

const API_BASE = "http://127.0.0.1:8000";

export async function uploadResumes(files: FileList) {
  const data = new FormData();
  Array.from(files).forEach(file => data.append("files", file));
  const res = await fetch(`${API_BASE}/upload/`, {
    method: "POST",
    body: data,
  });
  return await res.json();
}

export async function searchResumes(query: string, top_k: number = 5) {
  const res = await fetch(`${API_BASE}/search/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k }),
  });
  return await res.json();
}

export async function ragChat(
  job_description: string,
  top_k: number = 6,
  followup: string = ""
) {
  const body: any = { job_description, top_k };
  if (followup) body.followup = followup;
  const res = await fetch(`${API_BASE}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return await res.json();
}
