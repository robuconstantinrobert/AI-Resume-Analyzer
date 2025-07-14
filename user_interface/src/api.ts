export {};

const API_BASE = "https://ai-resume-analyzer-yhoq.onrender.com";

export async function uploadResumes(files: FileList) {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));
  const resp = await fetch(`${API_BASE}/upload/`, {
    method: "POST",
    body: formData,
  });
  return await resp.json();
}

export async function getUploadStatus(task_id: string) {
  const res = await fetch(`${API_BASE}/upload_status/${task_id}`);
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
