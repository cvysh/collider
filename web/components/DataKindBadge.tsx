import type { DataKind } from "@/lib/api";

/**
 * Marks an event as real detector data or simulation.
 *
 * This is the visible form of the project's central scientific rule
 * (docs/SCIENTIFIC_INTEGRITY.md): measured data carries no truth label,
 * simulation does. A user must never be unsure which they are looking at.
 *
 * The distinction is carried by **text, shape and colour together**, never by
 * colour alone -- SPEC section 37 requires that no critical meaning depend on
 * colour, and "is this real?" is as critical as meaning gets here.
 */
export function DataKindBadge({
  kind,
  size = "md",
}: {
  kind: DataKind;
  size?: "sm" | "md";
}) {
  const measured = kind === "measured";
  const pad = size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-1 text-xs";

  return (
    <span
      className={[
        "inline-flex items-center gap-1.5 font-mono uppercase tracking-wider",
        pad,
        measured
          ? "border border-mint/50 bg-mint/10 text-mint rounded-full"
          : "border border-dashed border-cyan/50 bg-cyan/10 text-cyan rounded-sm",
      ].join(" ")}
      title={
        measured
          ? "Real collision data. No truth label exists for this event."
          : "Monte Carlo simulation. The underlying process is known."
      }
    >
      {/* Solid dot for real, hollow square for simulated: the shapes differ
          so the two remain distinguishable without colour. */}
      <span
        aria-hidden
        className={
          measured
            ? "size-1.5 rounded-full bg-mint"
            : "size-1.5 border border-cyan bg-transparent"
        }
      />
      {measured ? "measured" : "simulated"}
    </span>
  );
}
