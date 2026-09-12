# Dialogue script

Every application state where a narrator can speak. **The drafts below are
placeholders** — they mark the slot, the speaker and the constraint. Replace
them with your own lines; that is the whole point of the file.

- **A** — eccentric senior scientist. Deadpan, unimpressed, occasionally smug.
- **B** — intern. Expressive, asks the question the user is already thinking.

## Rules

1. A line may state a **limitation**, never a **result**. "I can't score this"
   is fine. "This is a Higgs" never is.
2. Never obscure a readout. Dialogue sits beside data, never over it.
3. Original writing only. No existing show's catchphrases, names, or jokes.
4. Dismissible, and silent under `prefers-reduced-motion` beyond a static
   render.
5. Tier 1 slots want **2–3 variants** each so a repeat visit is not identical.
   Tiers 2–3 can have one.
6. Keep lines under ~90 characters. Longer belongs in the education panel.

---

## Tier 1 — essential (12 slots)

These carry scientific integrity. Each is a caveat we are obliged to surface
anyway; the character is what stops it reading as a disclaimer.

| # | Trigger | Who | The line must convey | Draft |
|---|---|---|---|---|
| 1 | Measured event opened | B | It is real, and unlabelled | "This one's real. Nobody knows what it is — that's the point." |
| 2 | Simulated event opened | A | It is simulation, and we know the answer | "Simulated. We know what this one is because we made it." |
| 3 | Model cannot score (2-muon event) | A | Wrong topology, not a failure | "Two muons. I'm built for four. Ask me something I can answer." |
| 4 | Score near threshold (within ±0.05) | A | Do not over-read it | "Right on the line. Don't read too much into it." |
| 5 | Score shown at all | A | Discriminant, not probability | "That's a score, not a probability. The odds were my choice, not nature's." |
| 6 | Curvature toggled to true | A | Straight is correct | "Told you. Those tracks were always that straight." |
| 7 | Curvature toggled to exaggerated | A | This is a visual aid | "Now you're just seeing what you want to see. Fine. It's labelled." |
| 8 | A requested quantity is absent | B | We don't invent it | "That measurement isn't in this event. We're not going to make one up." |
| 9 | Prediction disagrees with truth label | A | Models are wrong sometimes | "Got that one wrong. Happens. That's why we count instead of guess." |
| 10 | Provenance drawer opened | A | Traceability is the point | "Every number in here has an address. That's the difference." |
| 11 | Mass distribution / the bump | B | The excess is the interesting bit | "There. That lump. That's what everyone was looking for." |
| 12 | Model limitations panel | A | Scope is narrow and stated | "It's trained on simulation. Ask it about reality and it's guessing." |

---

## Tier 2 — interaction flavour (14 slots)

Reactions to ordinary use. Skippable at launch; they are what makes it feel
alive.

| # | Trigger | Who | Draft |
|---|---|---|---|
| 13 | Landing, first visit | B | "Same universe. Smaller things. Bigger questions." |
| 14 | Explore list, default | A | "Pick one. They're all real collisions or honest fakes." |
| 15 | Filter: measured only | B | "Real data only now. No answer key." |
| 16 | Filter: simulated only | A | "Simulation. Everything here has a label." |
| 17 | Empty filter result | B | "Nothing. Either it doesn't exist or you asked for something very specific." |
| 18 | First particle selected | B | "You can just… click them?" |
| 19 | Muon selected | A | "Muon. Heavy electron with somewhere to be." |
| 20 | Electron selected | A | "Electron. Light, loud, easy to lose." |
| 21 | Track highlighted | B | "Follow it out. That's the direction it left in." |
| 22 | Opposite-charge pair selected | A | "Opposite charges. They bend apart. That's how we know." |
| 23 | Analysis starts | B | "Let it think." |
| 24 | Analysis completes | A | "Done. Now read the caveats before you get excited." |
| 25 | Camera reset | A | "Back where you started. Happens to everyone." |
| 26 | Sparse event noticed | B | "Four particles. That's the whole event. Physics is quieter than it looks." |

---

## Tier 3 — edge, error, rare (12 slots)

| # | Trigger | Who | Draft |
|---|---|---|---|
| 27 | API error | A | "The machine disagreed with us. Try again." |
| 28 | Event not found (404) | B | "That one doesn't exist. Or it never did." |
| 29 | Slow load | A | "Still going. Patience is most of this job." |
| 30 | WebGL unavailable | B | "No 3D here. The numbers still work." |
| 31 | Reduced motion active | A | "Motion's off. Nothing important was in the motion." |
| 32 | η ≈ 0 gap explained | A | "There's a hole in the detector. On purpose. Cables have to go somewhere." |
| 33 | Detector feet explained | B | "It's sitting on something. You can see the legs in the data." |
| 34 | Trigger threshold explained | A | "Below ten GeV nobody was writing it down. It's not missing — it was never recorded." |
| 35 | Invariant mass explained | B | "Add the energies, subtract the momenta. Out falls a mass." |
| 36 | Z peak shown | A | "Ninety-one. Every time. That's not luck." |
| 37 | Event weight explained | A | "Simulation lies about how often things happen. The weight is the correction." |
| 38 | Shared deep link opened | B | "Someone sent you this exact collision. Odd gift. Good though." |

---

## Totals

| Tier | Slots | Variants wanted | Lines to write |
|---|---|---|---|
| 1 | 12 | 2–3 each | **24–36** |
| 2 | 14 | 1 | 14 |
| 3 | 12 | 1 | 12 |
| | **38** | | **50–62** |

**Minimum to ship:** Tier 1 only, one variant each — **12 lines**. Everything
else degrades to silence, which is an acceptable state.

---

## Implementation notes

Lines live in a single data file keyed by slot id, not scattered through
components. A slot with no line renders nothing. The dialogue system therefore
never blocks a feature, and lines can be written and edited without touching
code.

```
A2  →  "Simulated. We know what this one is because we made it."
```

Expression is chosen per line (`A/smug`, `B/surprised`), which is why the
expression filenames in `assets/characters/README.md` must stay stable.
