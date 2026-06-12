// The little sweeping radar dish in the header. Pure SVG + CSS animation.
export default function RadarDish({ active }) {
  return (
    <div className={`radar ${active ? "radar--active" : ""}`} aria-hidden="true">
      <svg viewBox="0 0 120 120" width="120" height="120">
        <defs>
          <radialGradient id="sweepFade" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.55" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </radialGradient>
        </defs>
        {[48, 34, 20].map((r) => (
          <circle key={r} cx="60" cy="60" r={r} className="radar-ring" />
        ))}
        <line x1="12" y1="60" x2="108" y2="60" className="radar-cross" />
        <line x1="60" y1="12" x2="60" y2="108" className="radar-cross" />
        <g className="radar-sweep">
          <path d="M60 60 L60 12 A48 48 0 0 1 108 60 Z" fill="url(#sweepFade)" />
        </g>
        <circle cx="92" cy="40" r="2.5" className="radar-blip radar-blip--1" />
        <circle cx="44" cy="80" r="2.5" className="radar-blip radar-blip--2" />
        <circle cx="74" cy="86" r="2.5" className="radar-blip radar-blip--3" />
        <circle cx="60" cy="60" r="3" className="radar-core" />
      </svg>
    </div>
  );
}
