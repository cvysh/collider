import lines from "@/lib/dialogue.json";
import { DismissibleNote } from "./DismissibleNote";

type Line = { text: string; expression: string };
type Slot = { id: string; speaker: string; lines: Line[] };

const SLOTS: Record<string, Slot> = Object.fromEntries(
  (lines.slots as Slot[]).map((s) => [s.id, s]),
);

/**
 * A narrator line for an application state.
 *
 * Renders nothing when the slot is unknown or has no line, so the dialogue
 * system can never block a feature.
 *
 * Variant selection is **deterministic**, derived from an optional `seed`.
 * Randomness during render is impure: React may re-render at any time, and an
 * impure choice would make the line flicker. A seed also makes the component
 * trivially testable and keeps server and client output identical.
 *
 * Pass something that varies per view -- an event id, say -- to get a
 * different variant without giving up determinism.
 *
 * Placeholder art: characters are the author's to draw
 * (assets/characters/README.md). Until then the speaker shows as an initial,
 * which keeps layout and dialogue testable without the artwork.
 */
/** FNV-1a: small, pure, stable across runs. Not for security. */
function hash(value: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < value.length; i++) {
    h ^= value.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h;
}

export function Narrator({
  slot,
  seed,
  className = "",
}: {
  slot: string;
  /** Varies the chosen variant deterministically, e.g. an event id. */
  seed?: string;
  className?: string;
}) {
  const entry = SLOTS[slot];
  if (!entry?.lines?.length) return null;

  const index = seed ? hash(seed) % entry.lines.length : 0;
  const line = entry.lines[index];
  const isA = entry.speaker === "A";

  return (
    <DismissibleNote className={`panel-hi flex items-start gap-3 p-3 text-sm ${className}`}>
      <span
        aria-hidden
        className={[
          "mt-0.5 grid size-7 shrink-0 place-items-center rounded-full font-mono text-xs",
          isA
            ? "bg-portal/15 text-portal ring-1 ring-portal/40"
            : "bg-toxic/15 text-toxic ring-1 ring-toxic/40",
        ].join(" ")}
        title={isA ? "Senior scientist" : "Intern"}
      >
        {entry.speaker}
      </span>
      <p className="flex-1 leading-relaxed text-paper/85">{line.text}</p>
    </DismissibleNote>
  );
}
