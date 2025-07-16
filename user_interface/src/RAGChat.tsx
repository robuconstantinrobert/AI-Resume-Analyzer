import React, { useState } from "react";
import { ragChat } from "./api";

export default function RAGChat() {
  const [jobDesc, setJobDesc] = useState("");
  const [followup, setFollowup] = useState("");
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleChat = async () => {
    setLoading(true);
    const res = await ragChat(jobDesc, 6, followup);
    setChatHistory([
      ...chatHistory,
      { jobDesc, followup, answer: res.llm_answer, context: res.matched_chunks },
    ]);
    setFollowup("");
    setLoading(false);
  };

  return (
    <div>
      <h2>AI Resume Match Chatbot</h2>
      <textarea
        rows={4}
        placeholder="Paste job description here"
        value={jobDesc}
        onChange={e => setJobDesc(e.target.value)}
        style={{width: "100%"}}
      />
      <textarea
        rows={2}
        placeholder="(Optional) Ask a follow-up question"
        value={followup}
        onChange={e => setFollowup(e.target.value)}
        style={{width: "100%"}}
      />
      <button onClick={handleChat} disabled={loading || !jobDesc.trim()}>
        {loading ? "Thinking..." : "Get Candidate Match"}
      </button>
      <div>
        {chatHistory.map((c, i) => (
          <div key={i} style={{margin: 16, border: "1px solid #aaa", padding: 10}}>
            <b>Job Desc:</b> <pre>{c.jobDesc}</pre>
            {c.followup && <><b>Follow-up:</b> <pre>{c.followup}</pre></>}
            <b>AI Answer:</b> <pre>{c.answer}</pre>
            <details>
              <summary>Matched Resume Chunks</summary>
              {c.context.map((chunk: any, idx: number) => (
                <pre key={idx} style={{fontSize: 12}}>{chunk.chunk_text}</pre>
              ))}
            </details>
          </div>
        ))}
      </div>
    </div>
  );
}
