const LABELS: Record<string, { name: string; unit: string; note?: string }> = {
  m_mumu: { name: "Dimuon mass", unit: "GeV" },
  m_4l: { name: "Four-lepton mass", unit: "GeV", note: "Withheld from the model" },
  m_z1: { name: "Z₁ candidate", unit: "GeV", note: "On-shell pair" },
  m_z2: { name: "Z₂ candidate", unit: "GeV", note: "Off-shell for a 125 GeV parent" },
};

/**
 * Quantities computed from the event's four-vectors.
 *
 * Rendered only from what the payload contains. A quantity that is absent is
 * absent -- SPEC section 36 is explicit that the UI reports missing
 * measurements rather than inventing them.
 */
export function DerivedQuantities({ derived }: { derived: Record<string, number> }) {
  const entries = Object.entries(derived ?? {});
  if (entries.length === 0) {
    return (
      <section className="panel p-4">
        <h2 className="text-xs uppercase tracking-wider text-dim">Derived</h2>
        <p className="mt-3 text-sm text-muted">
          No derived quantities available for this event.
        </p>
      </section>
    );
  }

  return (
    <section className="panel p-4">
      <h2 className="text-xs uppercase tracking-wider text-dim">Derived</h2>
      <dl className="mt-3 space-y-3">
        {entries.map(([key, value]) => {
          const meta = LABELS[key] ?? { name: key.replace(/_/g, " "), unit: "GeV" };
          return (
            <div key={key}>
              <div className="flex items-baseline justify-between gap-3">
                <dt className="text-sm text-muted">{meta.name}</dt>
                <dd className="tabular text-lg text-paper">
                  {value.toFixed(2)}
                  <span className="ml-1 text-xs text-dim">{meta.unit}</span>
                </dd>
              </div>
              {meta.note && <p className="mt-0.5 text-xs text-dim">{meta.note}</p>}
            </div>
          );
        })}
      </dl>
    </section>
  );
}
