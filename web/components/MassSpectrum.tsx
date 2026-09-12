"use client";

import { useId, useState } from "react";

/**
 * Stacked four-lepton mass spectrum.
 *
 * Drawn as plain SVG rather than with a charting library: it is one stacked
 * histogram with annotations, and a dependency would cost more bundle than the
 * hundred lines it replaces.
 *
 * Colours are validated for dark-mode categorical use -- lightness band,
 * chroma floor, CVD separation (ΔE 23 protan / 29 tritan), normal-vision
 * separation and contrast against the panel surface. Identity is never carried
 * by colour alone: both series are in the legend and in the table view.
 */
/**
 * Chart series steps, distinct from the brand accents.
 *
 * A brand colour and a chart colour do different jobs: the brand portal green
 * (#9bcf4f) sits at lightness 0.79, outside the 0.48-0.67 band a dark-mode
 * categorical palette needs, so the chart uses its own darker step of the same
 * hue. Validated: lightness band, chroma floor, CVD separation (delta-E 23
 * deutan / 12 tritan), normal-vision separation 27.8, contrast >= 3:1 against
 * the panel surface.
 *
 * Tritan separation at 12 is above the 8 floor but below the 15 comfort mark,
 * which is why both series are also in the legend and the table view -- colour
 * never carries identity alone here.
 */
const COLOURS = {
  background: "#8168B0",
  signal: "#77A634",
} as const;

export interface Series {
  id: string;
  label: string;
  values: number[];
  errors: number[];
  n_eff?: number[];
}

export interface Spectrum {
  quantity: string;
  unit: string;
  luminosity_pb: number;
  bin_width: number;
  edges: number[];
  centres: number[];
  series: Series[];
  annotations: { at: number; label: string; note: string }[];
  caveats: string[];
  totals: Record<string, number>;
}

const PAD = { top: 18, right: 18, bottom: 42, left: 54 };
const W = 720;
const H = 340;

export function MassSpectrum({ spectrum }: { spectrum: Spectrum }) {
  const [hover, setHover] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);
  // Log scale is offered because the single-Z background at 91 GeV is an order
  // of magnitude above everything else, and on a linear axis it flattens the
  // region the plot exists to show.
  const [logScale, setLogScale] = useState(false);
  const clipId = useId();

  const background = spectrum.series.find((s) => s.id === "background")!;
  const signal = spectrum.series.find((s) => s.id === "signal")!;

  const lo = spectrum.edges[0];
  const hi = spectrum.edges[spectrum.edges.length - 1];
  const stacked = background.values.map((b, i) => b + signal.values[i]);
  const yMax = Math.max(...stacked) * 1.12;

  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;
  const x = (v: number) => PAD.left + ((v - lo) / (hi - lo)) * plotW;

  // On a log axis a zero-height bin has no position, so the floor is a tenth
  // of an event -- below anything the simulation can resolve.
  const FLOOR = 0.1;
  const logMax = Math.log10(yMax);
  const logMin = Math.log10(FLOOR);
  const y = (v: number) => {
    if (!logScale) return PAD.top + plotH - (v / yMax) * plotH;
    const clamped = Math.max(v, FLOOR);
    const frac = (Math.log10(clamped) - logMin) / (logMax - logMin);
    return PAD.top + plotH - frac * plotH;
  };
  const binW = plotW / spectrum.centres.length;

  const yTicks = logScale
    ? [0.1, 1, 10, 100].filter((t) => t <= yMax)
    : [0, 0.25, 0.5, 0.75, 1].map((f) => f * yMax);
  const xTicks = [100, 150, 200, 250].filter((t) => t >= lo && t <= hi);

  return (
    <figure className="panel p-4">
      <figcaption className="mb-1">
        <h2 className="text-sm text-paper">Four-lepton invariant mass</h2>
        <p className="mt-1 text-xs text-dim">
          Simulation only, normalised to{" "}
          <span className="tabular">
            {(spectrum.luminosity_pb / 1000).toFixed(0)} fb⁻¹
          </span>
          . The classifier never saw this variable.
        </p>
      </figcaption>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap gap-4">
        {[signal, background].map((s) => (
          <span key={s.id} className="flex items-center gap-1.5">
            <span
              aria-hidden
              className="size-2.5 rounded-[2px]"
              style={{ background: COLOURS[s.id as keyof typeof COLOURS] }}
            />
            <span className="text-muted">{s.label}</span>
          </span>
        ))}
        </div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={logScale}
            onChange={(e) => setLogScale(e.target.checked)}
            className="switch"
          />
          <span className="text-muted">Log scale</span>
        </label>
      </div>

      <div className="mt-2 overflow-x-auto">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full min-w-[34rem]"
          role="img"
          aria-label={`Stacked histogram of four-lepton invariant mass from ${lo} to ${hi} GeV. ${signal.label} totals ${spectrum.totals.signal} events, ${background.label} totals ${spectrum.totals.background}.`}
        >
          <defs>
            <clipPath id={clipId}>
              <rect x={PAD.left} y={PAD.top} width={plotW} height={plotH} />
            </clipPath>
          </defs>

          {/* Recessive grid */}
          {yTicks.map((t) => (
            <line
              key={t}
              x1={PAD.left}
              x2={W - PAD.right}
              y1={y(t)}
              y2={y(t)}
              stroke="#2c4034"
              strokeWidth={1}
            />
          ))}

          {/* Stacked bars: background then signal, with a 2px surface gap so
              the two segments never read as one mark. */}
          <g clipPath={`url(#${clipId})`}>
            {spectrum.centres.map((c, i) => {
              const b = background.values[i];
              const s = signal.values[i];
              const isHover = hover === i;
              return (
                <g key={c} opacity={hover === null || isHover ? 1 : 0.55}>
                  <rect
                    x={x(spectrum.edges[i]) + 1}
                    y={y(b)}
                    width={binW - 2}
                    height={Math.max(0, y(logScale ? FLOOR : 0) - y(b))}
                    fill={COLOURS.background}
                  />
                  {s > 0 && (
                    <rect
                      x={x(spectrum.edges[i]) + 1}
                      y={y(b + s)}
                      width={binW - 2}
                      height={Math.max(0, y(b) - y(b + s) - 2)}
                      fill={COLOURS.signal}
                      rx={2}
                    />
                  )}
                </g>
              );
            })}
          </g>

          {/* Annotations */}
          {spectrum.annotations.map((a) => (
            <g key={a.label}>
              <line
                x1={x(a.at)}
                x2={x(a.at)}
                y1={PAD.top}
                y2={PAD.top + plotH}
                stroke="#93a894"
                strokeWidth={1}
                strokeDasharray="3 3"
                opacity={0.55}
              />
              <text
                x={x(a.at) + 4}
                y={PAD.top + 10}
                fill="#93a894"
                fontSize={9}
                fontFamily="var(--font-mono)"
              >
                {a.label}
              </text>
            </g>
          ))}

          {/* Axes */}
          <line
            x1={PAD.left}
            x2={W - PAD.right}
            y1={y(logScale ? FLOOR : 0)}
            y2={y(logScale ? FLOOR : 0)}
            stroke="#5d7563"
            strokeWidth={1}
          />
          {yTicks.map((t) => (
            <text
              key={t}
              x={PAD.left - 8}
              y={y(t) + 3}
              textAnchor="end"
              fill="#93a894"
              fontSize={10}
              fontFamily="var(--font-mono)"
            >
              {logScale ? (t < 1 ? t.toString() : t.toFixed(0)) : t.toFixed(0)}
            </text>
          ))}
          {xTicks.map((t) => (
            <text
              key={t}
              x={x(t)}
              y={H - PAD.bottom + 16}
              textAnchor="middle"
              fill="#93a894"
              fontSize={10}
              fontFamily="var(--font-mono)"
            >
              {t}
            </text>
          ))}
          <text
            x={PAD.left + plotW / 2}
            y={H - 6}
            textAnchor="middle"
            fill="#93a894"
            fontSize={10}
          >
            m₄ℓ [GeV]
          </text>
          <text
            x={14}
            y={PAD.top + plotH / 2}
            textAnchor="middle"
            fill="#93a894"
            fontSize={10}
            transform={`rotate(-90 14 ${PAD.top + plotH / 2})`}
          >
            events / {spectrum.bin_width.toFixed(0)} GeV
          </text>

          {/* Hover targets, wider than the marks */}
          {spectrum.centres.map((c, i) => (
            <rect
              key={c}
              x={x(spectrum.edges[i])}
              y={PAD.top}
              width={binW}
              height={plotH}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
          ))}
        </svg>
      </div>

      {hover !== null && (
        <div className="panel-hi mt-2 p-3 text-xs">
          <div className="tabular text-paper">
            {spectrum.edges[hover].toFixed(0)}–{spectrum.edges[hover + 1].toFixed(0)} GeV
          </div>
          <dl className="mt-1.5 space-y-1">
            {[signal, background].map((s) => (
              <div key={s.id} className="flex items-center justify-between gap-4">
                <dt className="flex items-center gap-1.5 text-dim">
                  <span
                    aria-hidden
                    className="size-2 rounded-[2px]"
                    style={{ background: COLOURS[s.id as keyof typeof COLOURS] }}
                  />
                  {s.id}
                </dt>
                <dd className="tabular text-muted">
                  {s.values[hover].toFixed(2)} ± {s.errors[hover].toFixed(2)}
                </dd>
              </div>
            ))}
            {background.n_eff && (
              <div className="flex justify-between gap-4 border-t border-ink pt-1">
                <dt className="text-dim">background N_eff</dt>
                <dd className="tabular text-muted">
                  {background.n_eff[hover].toFixed(1)}
                </dd>
              </div>
            )}
          </dl>
        </div>
      )}

      <button
        onClick={() => setShowTable((v) => !v)}
        className="mt-3 text-xs text-dim underline decoration-dotted hover:text-paper"
        aria-expanded={showTable}
      >
        {showTable ? "Hide" : "Show"} the numbers
      </button>

      {showTable && (
        <div className="mt-2 max-h-72 overflow-auto">
          <table className="w-full text-xs">
            <caption className="sr-only">
              Binned four-lepton mass values with statistical uncertainties
            </caption>
            <thead className="sticky top-0 bg-panel">
              <tr className="text-left text-dim">
                <th scope="col" className="py-1 pr-3 font-normal">Bin (GeV)</th>
                <th scope="col" className="py-1 pr-3 text-right font-normal">Signal</th>
                <th scope="col" className="py-1 pr-3 text-right font-normal">Background</th>
                <th scope="col" className="py-1 text-right font-normal">Bkg N_eff</th>
              </tr>
            </thead>
            <tbody>
              {spectrum.centres.map((c, i) => (
                <tr key={c} className="border-t border-ink-soft/50">
                  <td className="tabular py-1 pr-3">
                    {spectrum.edges[i].toFixed(0)}–{spectrum.edges[i + 1].toFixed(0)}
                  </td>
                  <td className="tabular py-1 pr-3 text-right">
                    {signal.values[i].toFixed(2)}
                  </td>
                  <td className="tabular py-1 pr-3 text-right">
                    {background.values[i].toFixed(2)}
                  </td>
                  <td className="tabular py-1 text-right text-dim">
                    {background.n_eff?.[i].toFixed(1) ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </figure>
  );
}
