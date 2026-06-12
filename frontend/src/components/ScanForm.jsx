import { useState } from "react";

const EXAMPLES = [
  "https://github.com/tiangolo/fastapi",
  "https://github.com/psf/requests",
  "https://github.com/pallets/click",
];

export default function ScanForm({ onScan, busy }) {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");

  function submit(e) {
    e.preventDefault();
    if (!repoUrl.trim() || busy) return;
    onScan({ repoUrl: repoUrl.trim(), question: question.trim() });
  }

  return (
    <form className="scan-form" onSubmit={submit}>
      <div className="field field--url">
        <label htmlFor="repo">Target repository</label>
        <input
          id="repo"
          type="text"
          inputMode="url"
          placeholder="https://github.com/owner/name"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          autoComplete="off"
          spellCheck="false"
        />
      </div>
      <div className="field field--q">
        <label htmlFor="q">Question <span className="opt">optional</span></label>
        <input
          id="q"
          type="text"
          placeholder="e.g. is this repo well tested?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          autoComplete="off"
        />
      </div>
      <button type="submit" className="scan-btn" disabled={busy || !repoUrl.trim()}>
        <span className="scan-btn__dot" />
        {busy ? "Scanning…" : "Run scan"}
      </button>

      <div className="examples">
        <span>try</span>
        {EXAMPLES.map((url) => (
          <button
            key={url}
            type="button"
            className="chip"
            disabled={busy}
            onClick={() => setRepoUrl(url)}
          >
            {url.replace("https://github.com/", "")}
          </button>
        ))}
      </div>
    </form>
  );
}
