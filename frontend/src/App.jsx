import { useRef, useState } from "react";
import RadarDish from "./components/RadarDish.jsx";
import ScanForm from "./components/ScanForm.jsx";
import TelemetryFeed from "./components/TelemetryFeed.jsx";
import ReportCard from "./components/ReportCard.jsx";
import { streamReview } from "./lib/reviewStream.js";

const INTERNAL = new Set(["execution_guardrail", "tool_selection", "tool_execution", "analyze"]);

// Turn a node's output into a short human note shown next to the completed step.
function noteFor(node, data) {
  if (!data) return "";
  if (node === "orchestrator") {
    return data.guardrail?.orchestrator?.reasoning || (data.selected_agents ? `→ ${data.selected_agents.join(", ")}` : "");
  }
  if (node === "input_guardrail") {
    const g = data.guardrail?.input;
    return g ? (g.ok ? "passed" : `blocked — ${g.note}`) : "";
  }
  if (node === "output_guardrail") {
    const g = data.guardrail?.output;
    return g ? (g.ok ? "grounded" : `flagged — ${g.note}`) : "";
  }
  if (node === "execution_guardrail") {
    const g = data.guardrail || {};
    const v = g[Object.keys(g)[0]];
    return v ? (v.ok ? "cleared" : `flagged — ${v.note}`) : "";
  }
  if (node === "analyze") {
    const f = data.findings || {};
    const v = f[Object.keys(f)[0]];
    return v?.verdict ? `verdict: ${v.verdict}` : "";
  }
  if (node === "tool_execution") return "github read";
  if (node === "answer_evaluation") return data.evaluation?.score ? `${data.evaluation.score}/5` : "";
  return "";
}

function Placeholder({ phase }) {
  return (
    <section className="report report--ghost">
      <span className="panel-kicker">report card</span>
      <p className="ghost-msg">
        {phase === "scanning"
          ? "Agents are inspecting the repository. The report builds as findings land."
          : "Run a scan to generate a structure / README / tests report."}
      </p>
      <div className="tiles">
        {["Structure", "README", "Tests"].map((t) => (
          <div key={t} className="tile tile--ghost">
            <h3>{t}</h3>
            <div className="ghost-bar" />
            <div className="ghost-bar ghost-bar--short" />
          </div>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [phase, setPhase] = useState("idle");
  const [steps, setSteps] = useState([]);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const abortRef = useRef(null);

  function upsertStep(label, node, status, note) {
    const indent = INTERNAL.has(node);
    setSteps((prev) => {
      const i = prev.findIndex((s) => s.id === label);
      if (i === -1) return [...prev, { id: label, label, node, status, indent, note }];
      const next = [...prev];
      next[i] = { ...next[i], status, note: note ?? next[i].note };
      return next;
    });
  }

  async function handleScan({ repoUrl, question }) {
    setPhase("scanning");
    setSteps([]);
    setReport(null);
    setError("");
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      for await (const ev of streamReview({ repoUrl, question, signal: controller.signal })) {
        if (ev.type === "node") {
          if (ev.phase === "start") upsertStep(ev.label, ev.node, "pending");
          else if (ev.phase === "end") upsertStep(ev.label, ev.node, "done", noteFor(ev.node, ev.data));
        } else if (ev.type === "final") {
          setReport(ev.state);
        } else if (ev.type === "error") {
          setError(ev.message);
          setPhase("error");
        } else if (ev.type === "done") {
          setPhase((p) => (p === "error" ? p : "done"));
        }
      }
    } catch (e) {
      if (e.name !== "AbortError") {
        setError(e.message || "Stream failed");
        setPhase("error");
      }
    }
  }

  const busy = phase === "scanning";

  return (
    <div className="app">
      <div className="bg-grid" aria-hidden="true" />
      <div className="bg-glow" aria-hidden="true" />

      <header className="masthead">
        <div className="brand">
          <RadarDish active={busy} />
          <div>
            <h1>Repo<span>Radar</span></h1>
            <p className="tagline">
              Point it at a GitHub repo. Three agents scan structure, README &amp; tests — live.
            </p>
          </div>
        </div>
        <div className="byline">multi-agent · LangGraph · GitHub MCP</div>
      </header>

      <main className="layout">
        <div className="col col--left">
          <ScanForm onScan={handleScan} busy={busy} />
          <TelemetryFeed steps={steps} phase={phase} />
        </div>
        <div className="col col--right">
          {error && (
            <div className="error-card">
              <strong>Scan failed.</strong> {error}
            </div>
          )}
          {report ? <ReportCard state={report} /> : <Placeholder phase={phase} />}
        </div>
      </main>

      <footer className="foot">Agentic AI Builder Expert Bootcamp — Batch 4.0</footer>
    </div>
  );
}
