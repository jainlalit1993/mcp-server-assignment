// The live feed. Each pipeline step appears the moment the backend reports it,
// pending -> done, with agent sub-steps indented.
import { useEffect, useRef } from "react";

function StepIcon({ status }) {
  if (status === "done") {
    return (
      <span className="step-icon step-icon--done">
        <svg viewBox="0 0 16 16" width="11" height="11">
          <path d="M3 8.5l3.2 3.2L13 5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    );
  }
  return <span className="step-icon step-icon--pending" />;
}

export default function TelemetryFeed({ steps, phase }) {
  const feedRef = useRef(null);

  useEffect(() => {
    const el = feedRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [steps]);

  return (
    <section className="feed-panel">
      <header className="panel-head">
        <span className="panel-kicker">live telemetry</span>
        <span className={`status-pill status-pill--${phase}`}>
          {phase === "scanning" && "scanning"}
          {phase === "done" && "complete"}
          {phase === "error" && "error"}
          {phase === "idle" && "standby"}
        </span>
      </header>

      <ol className="feed" ref={feedRef}>
        {steps.length === 0 && (
          <li className="feed-empty">Awaiting target. Enter a repository and run a scan.</li>
        )}
        {steps.map((step) => (
          <li
            key={step.id}
            className={`step ${step.indent ? "step--sub" : ""} step--${step.status}`}
          >
            <StepIcon status={step.status} />
            <span className="step-label">{step.label}</span>
            {step.note && <span className="step-note">{step.note}</span>}
          </li>
        ))}
      </ol>
    </section>
  );
}
