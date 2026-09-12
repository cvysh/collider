# Visual direction

Derived from the project storyboard. This document records the decisions in
words; the reference images stay local and uncommitted
(`assets/reference/README.md`).

---

## What the storyboard gets right, and we keep

**Panel rhythm.** Nine beats across roughly 30 seconds: title → browse →
reveal → inspect → analyse → result → distribution → reflect → close. The
product should be legible in that order, and the demo video follows it.

**Palette.** Near-black ground, panel navy, one radioactive-mint accent used
sparingly, cyan for secondary state, orange/red reserved for warnings. Matches
SPEC §24.1 — accents are rare, most of the UI stays dark.

**Hand annotation.** Handwritten marginalia beside clean technical panels. The
contrast between the two is the whole aesthetic: the *data* is precise and the
*voice* is loose. Never handwrite a number.

**Rounded irregular panels.** Slightly uneven corners, soft glow on the active
element. Not sterile rectangles, not skeuomorphism.

**Characters as narrators.** Two figures who comment on state — SPEC §25. See
"Dialogue" below, which is the strongest idea in the storyboard.

---

## What must change

### Characters must be original

The storyboard uses existing show characters and a catchphrase. SPEC §23.1,
§25 and `CLAUDE.md` all require original characters, dialogue and assets — the
aesthetic vocabulary, never the assets. See `assets/characters/README.md`.

### Track density does not match our data

The storyboard shows dozens of tracks radiating from the vertex. **Our events
contain about four objects** (`docs/FINDINGS.md` #5). Four-lepton events are
sparse, and no amount of art direction changes that.

Drama must therefore come from:

- schematic detector geometry — barrel layers, endcap discs, the beam line
- camera choreography — entry sweep, focus pull on selection
- the analysis reveal sequence
- colour and glow coded by particle type
- annotation and typography

**and never from inventing particles to fill the frame.**

### Tracks are nearly straight, and that is the point

`docs/FINDINGS.md` #9: a 45 GeV muon deviates 8 mm across the 1.1 m inner
detector. The storyboard's dramatic curves belong to sub-GeV particles.

- Default: true helix, `curvature_scale = 1.0`.
- An **exaggeration toggle** is available and must be labelled a visual aid.
- The *sign* of the bend is real at any scale: opposite charges splay apart.

### Scientific labelling

Every one of these appears in the storyboard and must change:

| Storyboard | Why it is wrong | Correct form |
|---|---|---|
| "87.4% confidence" | Training class balance is a choice, not a physical prior | "Discriminant 0.874 · threshold 0.92" |
| "Expected (Higgs) 125.1 / Difference +0.2 GeV" | Implies we measured the Higgs mass | Remove, or mark as a PDG reference value |
| "Real data. Real results." over a signal plot | Our signal is **simulation** | "Simulated signal vs simulated background" |
| "3.1 TeV" per event | Collision energy is a beam property, 13 TeV | Remove, or label as beam configuration |
| Fixed object-type counts | Only what the payload contains may be shown | Render from `objects`; omit absent types |
| "Higgs candidate" as a browse label | No measured event is a verified candidate | "Simulated H→ZZ→4ℓ" / "Z→μμ candidate (real data)" |

Real and simulated events must be visually distinct at every size, including
in the browse list, and never by colour alone (SPEC §37).

---

## Dialogue

The best idea in the storyboard: a character reacting to **real application
state**, not decoration. This is how caveats get surfaced without a wall of
text.

```
toggle curvature off   A: "Told you. Those tracks were always that straight."
measured event opened  B: "This one's real. Nobody knows what it is — that's
                           the point."
model cannot score     A: "Two muons. I'm built for four. Ask me something
                           I can answer."
score near threshold   A: "Right on the line. Don't read too much into it."
empty filter result    B: "Nothing. Either it doesn't exist or you asked for
                           something very specific."
```

Rules: every line is original; a line may state a limitation but never a
result; dialogue never covers a readout; it is dismissible and respects
reduced-motion.

---

## Typography

| Use | Family |
|---|---|
| Display / brand | Wide geometric sans |
| UI | Modern grotesk |
| Numbers, units, IDs | Monospace, tabular figures |
| Annotation | Handwriting-inspired, sparingly, never for numbers |

Tabular figures are not optional: values that change on hover must not shift
the layout.

---

## Motion

Permitted: camera entry, track reveal, selection response, analysis-state
transitions, a single subtle ambient element.

Not permitted: continuous pulsing on every object, full-screen particle
fields, decorative physics simulation, heavy post-processing. SPEC §20.

Under `prefers-reduced-motion`: no camera drift, no pulsing, transitions
reduced to opacity, full interactivity retained.
