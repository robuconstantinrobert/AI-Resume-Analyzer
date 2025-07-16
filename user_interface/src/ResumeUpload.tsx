import React, { useState } from "react";
import { uploadResumes, getUploadStatus } from "./api";

type UploadTask = {
  filename: string;
  task_id: string;
  status: string;
  result?: any;
};

export default function ResumeUpload() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [tasks, setTasks] = useState<UploadTask[]>([]);
  const [polling, setPolling] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files) return;
    const res = await uploadResumes(files);
    setTasks(res.submitted.map((t: any) => ({
      ...t,
      status: "PENDING",
      result: undefined
    })));
    setPolling(true);
  };

  React.useEffect(() => {
    if (!polling || tasks.length === 0) return;
      const interval = setInterval(() => {
        Promise.all(
          tasks.map(async (t) => {
            if (t.status === "SUCCESS" || t.status === "FAILURE") return t;
            const stat = await getUploadStatus(t.task_id);
            return { ...t, status: stat.status, result: stat.result };
          })
        ).then((updated) => setTasks(updated));
      }, 2000);

      return () => clearInterval(interval);
    }, [polling, tasks]);

  return (
    <div>
      <h2>Upload Resumes</h2>
      <input type="file" multiple onChange={handleChange} />
      <button onClick={handleUpload} disabled={!files}>Upload</button>
      {tasks.length > 0 && (
        <div>
          <h4>Processing status:</h4>
          {tasks.map((t, i) => (
            <div key={i} style={{marginBottom:8}}>
              <b>{t.filename}</b>: {t.status}
              {t.status === "SUCCESS" && t.result &&
                <pre style={{background:"#f7f7f7"}}>{JSON.stringify(t.result, null, 2)}</pre>
              }
              {t.status === "FAILURE" && <span style={{color:"red"}}>Failed</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
