/**
 * Headline figures under the hero.
 *
 * Every value is one this project measured and can point at. The prototype
 * this pattern came from ran 13.6 TeV (Run 3, not our data) and 5.2 sigma (the
 * 2012 ATLAS/CMS discovery figure, not ours) — a ribbon of impressive numbers
 * belonging to someone else. These are ours, and each links to where it was
 * derived.
 */
const STATS: { value: string; label: string; note: string }[] = [
  { value: "13 TeV", label: "collision energy", note: "ATLAS Run 2, 2015–2016" },
  { value: "4", label: "resonances found", note: "J/ψ, ψ(2S), Υ, Z — from raw data" },
  { value: "0.9882", label: "classifier AUC", note: "test split, weighted" },
  { value: "826 B", label: "per-event payload", note: "gzipped" },
];

export function StatRibbon() {
  return (
    <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {STATS.map((s, i) => (
        <div
          key={s.label}
          className={`panel grain p-4 ${i % 2 === 1 ? "askew-b" : "askew-a"}`}
        >
          <dt className="tabular text-2xl leading-none text-portal">{s.value}</dt>
          <dd className="mt-1.5">
            <span className="stencil">{s.label}</span>
            <span className="mt-1 block text-[10px] leading-relaxed text-dim">
              {s.note}
            </span>
          </dd>
        </div>
      ))}
    </dl>
  );
}
