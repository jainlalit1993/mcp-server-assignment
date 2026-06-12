// A 5-segment quality meter for the LLM-as-judge score.
export default function ScoreMeter({ score = 0, justification = "" }) {
  const tone = score >= 4 ? "pass" : score >= 3 ? "warn" : "fail";
  return (
    <div className="score">
      <div className="score-head">
        <span className="panel-kicker">quality score</span>
        <span className={`score-num score-num--${tone}`}>
          {score}<small>/5</small>
        </span>
      </div>
      <div className="score-bars">
        {[1, 2, 3, 4, 5].map((n) => (
          <span
            key={n}
            className={`score-bar ${n <= score ? `score-bar--on score-bar--${tone}` : ""}`}
            style={{ animationDelay: `${n * 70}ms` }}
          />
        ))}
      </div>
      {justification && <p className="score-just">{justification}</p>}
    </div>
  );
}
