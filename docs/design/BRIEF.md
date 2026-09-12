# Visual direction brief

Author's brief, canonical. `THEME.md` records how it is implemented; where the
two disagree, this file wins.

## The feeling

A chaotic adult-animated sci-fi aesthetic: eccentric mad-scientist laboratory,
absurd cosmic environments, hand-drawn cartoon energy, weird machinery,
scribbled annotations, portals and wires and tubes and screens, irreverent
scientific humour, slightly messy layouts, unexpected details.

> The website should feel like a mad scientist built a particle-physics
> laboratory and accidentally turned it into a web application.

**Not** copyrighted characters, exact character designs, logos, screenshots or
artwork from any show. The high-level visual language only.

## The balance

Chaotic presentation, serious science underneath. Not a children's cartoon —
the audience is technically curious students, developers, scientists and
engineers.

Scientific data always uses clean technical typography. Personality lives in
the annotations *around* it.

## Priority order for every design decision

1. Scientific correctness
2. Usability
3. Performance
4. Technical quality
5. Visual personality
6. Decorative effects

**Never sacrifice the first five to make something look cool.**

## Palette

Deep navy and almost-black grounds, dirty/aged laboratory surfaces, off-white
text. Electric cyan, radioactive green, purple, occasional orange and yellow.

Neon sparingly. Not every element glows.

## Typography

Clean technical type for measurements and data. Occasional handwritten or
cartoon type for annotations and commentary.

```
EVENT #1847291

4 LEPTONS
125.3 GeV
                 <- "THAT'S INTERESTING..."
```

## Microcopy

Contextual and humorous rather than generic. `CALIBRATING THE VERY IMPORTANT
MACHINES...`, `THE UNIVERSE IS DOING SOMETHING WEIRD...`, `PLEASE DON'T TOUCH
THE ANTIMATTER...`

Subtle. Not jokes everywhere.

## Event viewer

The visual centrepiece. Tracks energetic and slightly exaggerated while
remaining derived from the real event data. Particle types get distinct visual
identities — muon a clean bright track, electron more energetic, photon sharp
and light-like, jet a clustered structure.

**Do not invent physical properties for aesthetics.** The visualisation layer
may stylise the representation; the underlying measurements stay real.

## Event discovery

Browsing should feel like exploring a laboratory computer — experiment logs,
evidence boards, instrument readouts. Not a boring table.

## Environmental detail

Tiny warning labels, hand-drawn arrows, scribbled equations, blinking
indicators, cables, warning signs, handwritten notes, small diagrams. Mostly
decorative, never interfering with usability. A user who explores should
occasionally find something funny.

## Animation

An animated sci-fi laboratory, not corporate SaaS. Portal-like transitions,
drifting particles, subtle machinery movement, progressive track reveal, comic
panel transitions, occasional glitches.

**Performance always wins.** No oversized models, huge textures, excessive
particle counts, shaders everywhere, or constantly animated objects that do not
need it. Lazy loading and efficient geometry as the spec describes.

Reserve the strongest animation for important moments. Not every interaction.

## Where this brief and scientific integrity meet

The brief's example AI panel reads "HIGGS CANDIDATE / 87.4% confidence" with
"invariant mass" as a contributing factor. Two corrections, following the
brief's own priority order:

- The output is a **discriminant score**, not a confidence or probability — the
  training class balance is a choice, not a physical prior
  (`SCIENTIFIC_INTEGRITY.md` section 3).
- **Invariant mass cannot appear as a contributing factor**: it is deliberately
  excluded from the feature set so a score cut cannot sculpt the spectrum
  (`FINDINGS.md` #5).

The *visual treatment* the brief asks for — an instrument readout with
contribution bars — is kept in full. It is driven by real per-event SHAP
contributions over the features the model actually uses.
