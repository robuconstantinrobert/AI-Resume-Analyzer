import React, { useState } from "react";
import { searchResumes } from "./api";

export default function ResumeSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    const res = await searchResumes(query);
    setResults(res.results);
  };

  return (
    <div>
      <h2>Semantic Resume Search</h2>
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search by skill, job title, etc."
      />
      <button onClick={handleSearch}>Search</button>
      {results && results.map((r: any, i: number) => (
        <div key={i} style={{border: "1px solid #ccc", margin: 8, padding: 8}}>
          <b>File:</b> {r.filename}<br />
          <b>Chunk Index:</b> {r.chunk_index}<br />
          <b>Preview:</b> {r.chunk_text}
        </div>
      ))}
    </div>
  );
}
