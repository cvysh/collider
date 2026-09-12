# Theme: garage laboratory

Replaces the earlier "clean dark sci-fi" treatment. Recorded here so the
reasoning survives the CSS.

## The governing idea

> **The chrome is chaotic. The data is pristine.**

Outlines wobble, panels sit askew, hazard tape holds things together — and
every number is monospaced, tabular and dead straight. The contrast *is* the
aesthetic: a beautifully precise readout bolted into a janky machine is funnier
and more legible than making everything wobbly.

This also satisfies SPEC §24.4 and `CLAUDE.md`: decoration never obscures a
readout. The constraint improves the design rather than limiting it.

## On the source of the style

The look draws on the visual grammar of adult sci-fi cartoons — heavy ink
outlines, flat fills, acid palettes, grimy lab clutter, deadpan labels on
absurd machinery. **A style is not protected; specific characters, wordmarks,
props, frames and catchphrases are.** Nothing here reproduces any of those.
`assets/dialogue/lines.json` is guarded by a test that fails the build on a
copyrighted reference.

## Tokens

| Token | Hex | Role |
|---|---|---|
| `ground` | `#0b1410` | Page. Murky green-black, never neutral |
| `panel` | `#14211a` | Surfaces |
| `ink` | `#050a07` | Outlines — 2px, not hairlines |
| `portal` | `#9bcf4f` | The signature. Once per screen, never twice |
| `toxic` | `#3fbfb0` | Secondary accent, electrons |
| `bruise` | `#7b5ea7` | Tertiary |
| `hazard` | `#e8c547` | Warnings, tape, thresholds, visual-aid banners |
| `alarm` | `#ef5b4c` | Errors, model disagreement |
| `paper` | `#ede6d3` | Text. Yellowed, not white |

### Chart series are not brand colours

A brand accent and a chart series do different jobs. Portal green sits at
lightness 0.79 — outside the 0.48–0.67 band a dark-mode categorical palette
requires — so the spectrum uses its own darker step of the same hue.

| Series | Hex | Validated |
|---|---|---|
| signal | `#77A634` | lightness band, chroma floor, CVD ΔE 23 deutan / 12 tritan, normal-vision 27.8, contrast ≥ 3:1 |
| background | `#8168B0` | same |

Tritan separation of 12 clears the floor of 8 but sits below the comfort mark
of 15, which is why both series also appear in the legend and the table view.
**Colour never carries identity alone.**

## Type

| Face | Role |
|---|---|
| Anton | Wordmark and page titles. Condensed, heavy, confident |
| Work Sans | Prose |
| JetBrains Mono | **Every number.** Tabular figures, so values never reflow |
| Permanent Marker | Annotations only. Never a number |

## Treatments

- **Outlines** 2px `ink` with a 3px hard offset shadow. No soft shadows.
- **Corners** deliberately uneven, e.g. `18px 10px 20px 8px`. Each panel
  variant differs so no two read identical.
- **Tilt** `askew-a` / `askew-b` at ±0.3°. Enough to feel hand-placed, not
  enough to look broken. Cleared under `prefers-reduced-motion`.
- **Grain** halftone dots at 28% opacity. Subtle enough to read through.
- **Hazard tape** 45° yellow/ink stripes, for warnings and thresholds only.
- **CRT scanlines** the 3D viewer only — it is the one surface meant to read as
  a monitor.
- **Switches** chunky physical toggles, not browser defaults.

## The hero

The landing page opens on the detector viewed **down the beam pipe**. Along z,
the barrel layers are concentric circles and tracks radiate from the interaction
point — which reads as a vortex while being literally the ATLAS cross-section.

The radii are the real inner-detector layers (0.45, 0.75, 1.1 m) and the track
angles are the measured φ of `mc-signal-118662`. The signature circular motif
comes from real geometry rather than from an imitated prop.

Static SVG: SPEC §6.1 and §21.2 forbid the 3D bundle on a page that renders no
event.

## Still to do

- Character artwork replaces the placeholder initials in `Narrator`
  (`assets/characters/README.md`).
- Slot 6 needs two replacement dialogue lines.
