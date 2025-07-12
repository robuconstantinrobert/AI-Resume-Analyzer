import React from "react";
import ResumeUpload from "./ResumeUpload";
import ResumeSearch from "./ResumeSearch";
import RAGChat from "./RAGChat";

function App() {
  return (
    <div style={{maxWidth: 800, margin: "0 auto", fontFamily: "sans-serif"}}>
      <h1>Resume Analyzer & RAG Chatbot</h1>
      <ResumeUpload />
      <hr />
      <ResumeSearch />
      <hr />
      <RAGChat />
    </div>
  );
}

export default App;
