# Characters — original artwork only

Drop your own character drawings here (SVG preferred, PNG with transparency
also fine).

## Why this folder has a rule

`docs/SPEC.md` §23.1 and §25, and `CLAUDE.md`, require original characters.
The project takes the *aesthetic vocabulary* of adult sci-fi cartoons — the
energy, the deadpan annotations, the chaotic-lab palette — and none of the
assets.

**Do not place here:** existing show characters or their art, screenshots,
frames, catchphrases, logos, portal-gun imagery, or copyrighted backgrounds.
This repository is intended to be public under the author's name; a takedown
on a portfolio piece is a self-inflicted wound.

## The two narrators (SPEC §25)

| | Role | Appears in |
|---|---|---|
| **Character A** | Eccentric senior scientist. Deadpan, unimpressed, occasionally smug. | Analysis panels, caveats, results |
| **Character B** | Younger intern. Expressive, asks the obvious question the user is also thinking. | Onboarding, empty states, tooltips |

They are narrators, not furniture. They must never obscure a scientific
readout.

## Naming

```
character-a/  neutral.svg  smug.svg  unimpressed.svg  pointing.svg
character-b/  neutral.svg  surprised.svg  confused.svg  excited.svg
```

Expression names are referenced from the dialogue system, so keep them stable.

## Sizing

Author at 512×512 or larger, on transparent background, with the figure
occupying roughly the middle 80%. The UI scales down; it never scales up.
