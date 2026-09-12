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

Deep navy and almost-black grounds, per `BRIEF.md`.

| Token | Hex | Role |
|---|---|---|
| `ground` | `#060a14` | Page. Deep navy-black |
| `panel` | `#0e1626` | Laboratory surfaces |
| `ink` | `#03060e` | Outlines — 2px, not hairlines |
| `portal` | `#8fe04a` | Radioactive green. The signature; once per screen |
| `toxic` | `#3fd4ef` | Electric cyan. Electrons, secondary accent |
| `bruise` | `#8b6bc4` | Purple. Tertiary, negative contributions |
| `hazard` | `#f0b429` | Warnings, tape, thresholds, visual-aid banners |
| `alarm` | `#ef5b4c` | Errors, model disagreement |
| `paper` | `#ece8dd` | Text. Off-white, never pure |

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

## Instrument readouts

The analysis panel and the event cards are built as laboratory instruments —
stencilled casing labels, blinking status lamps, rivets clipped to the panel
edge, big monospaced numerals with small quiet labels beneath.

The contribution bars are **real per-event SHAP values** from the trained
booster: additive log-odds shifts that say what drove *this* score, not global
importance. They diverge from a centre zero — green pushed the score up, purple
down.

The brief's example panel lists invariant mass as a contributing factor. It
cannot appear, because it is excluded from the feature set by design. What
appears instead is what the model genuinely used, and for a signal event that
is dominated by `m_z2` — the off-shell Z, which is the physical signature of a
125 GeV parent.

## The analysis sequence

The brief asks for comic-panel composition on major moments, and analysing an
event is the major moment. This is the only place in the product that spends
real animation budget.

**It is a replay, not a computation.** Predictions are precomputed at export
because they are deterministic for a fixed event, model and feature set
(ADR-0002), and SPEC §35 forbids faking progress for an operation that has
none. So nothing pretends to be working: each panel reveals a stage that
genuinely ran, showing the values that stage produced, and the footer says so
plainly.

| Panel | Shows |
|---|---|
| 01 Selection | The real criteria this event passed |
| 02 Reconstruction | Its actual derived masses |
| 03 Features | 14 inputs, and why the mass is not among them |
| 04 Discriminant | The score beside its threshold |
| 05 Explanation | The top real SHAP contributions |

The constraint made this better than a spinner. A progress bar conveys nothing;
these panels say what the pipeline actually does.

It is skippable, and under `prefers-reduced-motion` every panel lands at once.
An animation nobody can escape is a usability failure however good it looks.

## Legibility corrections made during the pass

Two decorations were dialled back after looking at them on screen, following
the brief's own priority order:

- **Rivets** tiled the whole panel and showed through the readout text. Now
  clipped to a 14px border strip.
- **Grain** at 0.28 opacity competed with monospaced numerals. Reduced to 0.15.

Neither was a matter of taste. A decoration that makes a number harder to read
has failed at priority 2 of 6.

## Still to do

- Character artwork replaces the placeholder initials in `Narrator`
  (`assets/characters/README.md`).
- Slot 6 needs two replacement dialogue lines.
