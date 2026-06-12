// Maps each agent's verdict to a status (pass / warn / fail) and display label.

const MAP = {
  structure: {
    title: "Structure",
    blurb: "Layout & separation of concerns",
    verdicts: {
      good: { status: "pass", label: "Clean" },
      needs_work: { status: "warn", label: "Needs work" },
    },
  },
  readme: {
    title: "README",
    blurb: "Clarity & completeness",
    verdicts: {
      clear: { status: "pass", label: "Clear" },
      unclear: { status: "warn", label: "Unclear" },
      missing: { status: "fail", label: "Missing" },
    },
  },
  test: {
    title: "Tests",
    blurb: "Unit tests & CI",
    verdicts: {
      present: { status: "pass", label: "Present" },
      partial: { status: "warn", label: "Partial" },
      missing: { status: "fail", label: "Missing" },
    },
  },
};

export const AGENT_ORDER = ["structure", "readme", "test"];

export function describeFinding(agent, finding) {
  const meta = MAP[agent] ?? { title: agent, blurb: "", verdicts: {} };
  const verdict = finding?.verdict;
  const status = meta.verdicts[verdict] ?? { status: "warn", label: verdict ?? "—" };
  return {
    title: meta.title,
    blurb: meta.blurb,
    status: status.status,
    label: status.label,
    reasons: finding?.reasons ?? [],
    evidence: finding?.evidence ?? [],
  };
}
