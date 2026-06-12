import { AGENT_ORDER, describeFinding } from "../lib/verdicts.js";
import ScoreMeter from "./ScoreMeter.jsx";

const STATUS_GLYPH = { pass: "●", warn: "▲", fail: "✕" };

function Tile({ agent, finding, index }) {
  const d = describeFinding(agent, finding);
  return (
    <article
      className={`tile tile--${d.status}`}
      style={{ animationDelay: `${index * 90}ms` }}
    >
      <div className="tile-top">
        <div>
          <h3>{d.title}</h3>
          <p className="tile-blurb">{d.blurb}</p>
        </div>
        <span className={`badge badge--${d.status}`}>
          <span className="badge-glyph">{STATUS_GLYPH[d.status]}</span>
          {d.label}
        </span>
      </div>

      {d.reasons.length > 0 && (
        <ul className="tile-reasons">
          {d.reasons.slice(0, 4).map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      )}

      {d.evidence.length > 0 && (
        <div className="tile-evidence">
          {d.evidence.slice(0, 5).map((e, i) => (
            <code key={i}>{e}</code>
          ))}
        </div>
      )}
    </article>
  );
}

function GuardChip({ label, guard }) {
  if (!guard) return null;
  const ok = guard.ok !== false;
  return (
    <span className={`guard-chip ${ok ? "guard-chip--ok" : "guard-chip--flag"}`}>
      {ok ? "✓" : "!"} {label}
    </span>
  );
}

export default function ReportCard({ state }) {
  const { findings = {}, final_answer, summary, evaluation = {}, guardrail = {}, selected_agents = [] } = state;
  const agents = AGENT_ORDER.filter((a) => selected_agents.includes(a) || findings[a]);

  return (
    <section className="report">
      <header className="panel-head">
        <span className="panel-kicker">report card</span>
        <div className="guard-strip">
          <GuardChip label="input" guard={guardrail.input} />
          <GuardChip label="output" guard={guardrail.output} />
        </div>
      </header>

      <div className="tiles">
        {agents.map((agent, i) => (
          <Tile key={agent} agent={agent} finding={findings[agent]} index={i} />
        ))}
      </div>

      <div className="summary-card">
        <span className="panel-kicker">summary</span>
        <p className="summary-text">{final_answer || summary || "No summary produced."}</p>
      </div>

      <ScoreMeter score={evaluation.score} justification={evaluation.justification} />
    </section>
  );
}
