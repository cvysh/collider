/**
 * The detector, viewed straight down the beam pipe.
 *
 * Looking along z, the barrel layers are concentric circles and the tracks
 * radiate from the interaction point. The result reads as a vortex — but it is
 * not decoration: the radii are the real inner-detector layers and the track
 * angles are the measured φ of an actual event.
 *
 * Static SVG on purpose. SPEC 6.1 and 21.2 forbid the 3D bundle on a page that
 * renders no event, and this costs nothing.
 */

/** Measured φ and pT from mc-signal-118662, a simulated H→ZZ→4ℓ event. */
const TRACKS = [
  { phi: 3.0573, pt: 48.0, charge: +1, kind: "electron" },
  { phi: -0.313, pt: 31.3, charge: -1, kind: "electron" },
  { phi: 1.4822, pt: 16.1, charge: -1, kind: "muon" },
  { phi: -0.9519, pt: 15.2, charge: +1, kind: "muon" },
] as const;

const COLOUR = { muon: "#9bcf4f", electron: "#3fbfb0" } as const;

/** Real inner-detector barrel radii, metres, mapped to SVG units. */
const LAYERS = [0.45, 0.75, 1.1];
const SCALE = 150; // px per metre
const R = 200;

export function BeamPipeHero() {
  return (
    <svg
      viewBox={`0 0 ${R * 2} ${R * 2}`}
      className="h-full w-full"
      role="img"
      aria-label="The ATLAS inner detector seen along the beam axis: three concentric barrel layers with four particle tracks radiating from the collision point."
    >
      <defs>
        <radialGradient id="core">
          <stop offset="0%" stopColor="#e9ffd0" stopOpacity="1" />
          <stop offset="35%" stopColor="#9bcf4f" stopOpacity="0.85" />
          <stop offset="100%" stopColor="#9bcf4f" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="haze">
          <stop offset="55%" stopColor="#3fbfb0" stopOpacity="0" />
          <stop offset="100%" stopColor="#7b5ea7" stopOpacity="0.22" />
        </radialGradient>
      </defs>

      <circle cx={R} cy={R} r={R - 4} fill="url(#haze)" />

      {/* Barrel layers. Segmented rather than solid: real detectors are built
          from discrete modules, and the gaps read as machined. */}
      {LAYERS.map((metres, li) => {
        const r = metres * SCALE;
        const segments = 24 + li * 12;
        return (
          <g key={metres}>
            <circle
              cx={R}
              cy={R}
              r={r}
              fill="none"
              stroke="#2c4034"
              strokeWidth={2}
              strokeDasharray={`${(2 * Math.PI * r) / segments - 3} 3`}
            />
            <circle
              cx={R}
              cy={R}
              r={r}
              fill="none"
              stroke="#050a07"
              strokeWidth={0.7}
              opacity={0.55}
            />
          </g>
        );
      })}

      {/* Spokes: the module supports. */}
      {Array.from({ length: 16 }, (_, i) => {
        const a = (i / 16) * Math.PI * 2;
        return (
          <line
            key={i}
            x1={R + Math.cos(a) * 0.45 * SCALE}
            y1={R + Math.sin(a) * 0.45 * SCALE}
            x2={R + Math.cos(a) * 1.1 * SCALE}
            y2={R + Math.sin(a) * 1.1 * SCALE}
            stroke="#2c4034"
            strokeWidth={1}
            opacity={0.35}
          />
        );
      })}

      {/* Tracks. Curvature is the true helix projected onto this plane: at
          these momenta the bend is under a degree, so they read straight —
          which is the honest picture. */}
      {TRACKS.map((t) => {
        const len = 1.1 * SCALE;
        // r = pt / (0.3 q B), B = 2 T. Sagitta over the layer is tiny, so a
        // quadratic through the true endpoint is exact to well under a pixel.
        const radius = t.pt / (0.299792458 * 2);
        const bend = -t.charge * (radius * (1 - Math.cos(1.1 / radius))) * SCALE;
        const ex = R + Math.cos(t.phi) * len;
        const ey = R + Math.sin(t.phi) * len;
        const nx = -Math.sin(t.phi);
        const ny = Math.cos(t.phi);
        const cx = R + Math.cos(t.phi) * len * 0.5 + nx * bend * 0.5;
        const cy = R + Math.sin(t.phi) * len * 0.5 + ny * bend * 0.5;
        return (
          <g key={t.phi}>
            <path
              d={`M ${R} ${R} Q ${cx} ${cy} ${ex + nx * bend} ${ey + ny * bend}`}
              fill="none"
              stroke={COLOUR[t.kind]}
              strokeWidth={2.5}
              strokeLinecap="round"
              opacity={0.95}
            />
            <circle
              cx={ex + nx * bend}
              cy={ey + ny * bend}
              r={3 + Math.sqrt(t.pt) * 0.45}
              fill={COLOUR[t.kind]}
              stroke="#050a07"
              strokeWidth={1.5}
            />
          </g>
        );
      })}

      <circle cx={R} cy={R} r={46} fill="url(#core)" />
      <circle cx={R} cy={R} r={5} fill="#ede6d3" stroke="#050a07" strokeWidth={1.5} />
    </svg>
  );
}
