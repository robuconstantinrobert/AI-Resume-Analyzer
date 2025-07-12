import React, { useState } from "react";
import { uploadResumes } from "./api";

export default function ResumeUpload() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files) return;
    const res = await uploadResumes(files);
    setResult(res);
  };

  return (
    <div>
      <h2>Upload Resumes</h2>
      <input type="file" multiple onChange={handleChange} />
      <button onClick={handleUpload} disabled={!files}>Upload</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
