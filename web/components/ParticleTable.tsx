import type { ReconstructedObject } from "@/lib/api";

const TYPE_STYLE: Record<string, { label: string; colour: string }> = {
  muon: { label: "μ", colour: "text-portal" },
  electron: { label: "e", colour: "text-toxic" },
  photon: { label: "γ", colour: "text-hazard" },
  jet: { label: "jet", colour: "text-muted" },
};

function chargeSign(charge: number | null | undefined) {
  if (charge == null) return "";
  return charge > 0 ? "+" : charge < 0 ? "−" : "0";
}

/**
 * Reconstructed objects as a table.
 *
 * This is the 2D fallback the 3D view sits beside, not a consolation prize:
 * SPEC section 37 requires a text alternative for critical event information,
 * and every number the viewer can show must be readable here.
 */
export function ParticleTable({
  objects,
  selectedId,
}: {
  objects: ReconstructedObject[];
  selectedId?: number;
}) {
  return (
    /* Wide content scrolls inside its own container; the page body must never
       scroll horizontally. */
    <div className="panel overflow-x-auto">
      <table className="w-full min-w-[30rem] text-sm">
        <caption className="sr-only">
          Reconstructed objects in this event, with momentum and angles
        </caption>
        <thead>
          <tr className="border-b border-ink text-left text-xs text-dim">
            <th scope="col" className="px-3 py-2 font-normal">Object</th>
            <th scope="col" className="px-3 py-2 text-right font-normal">pT (GeV)</th>
            <th scope="col" className="px-3 py-2 text-right font-normal">η</th>
            <th scope="col" className="px-3 py-2 text-right font-normal">φ</th>
            <th scope="col" className="px-3 py-2 text-right font-normal">E (GeV)</th>
          </tr>
        </thead>
        <tbody>
          {objects.map((o) => {
            const style = TYPE_STYLE[o.type] ?? TYPE_STYLE.jet;
            return (
              <tr
                key={o.id}
                className={[
                  "border-b border-ink-soft/50 last:border-0",
                  selectedId === o.id ? "bg-portal/10" : "",
                ].join(" ")}
              >
                <th scope="row" className="px-3 py-2 text-left font-normal">
                  <span className={`font-mono ${style.colour}`}>
                    {style.label}
                    <sup>{chargeSign(o.charge)}</sup>
                  </span>
                  <span className="ml-2 text-xs text-dim">{o.type}</span>
                </th>
                <td className="tabular px-3 py-2 text-right">{o.pt.toFixed(1)}</td>
                <td className="tabular px-3 py-2 text-right text-muted">
                  {o.eta.toFixed(2)}
                </td>
                <td className="tabular px-3 py-2 text-right text-muted">
                  {o.phi.toFixed(2)}
                </td>
                <td className="tabular px-3 py-2 text-right">{o.energy.toFixed(1)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
