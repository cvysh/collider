import Link from "next/link";
import type { DataKind } from "@/lib/api";

const OPTIONS: { label: string; value: DataKind | undefined }[] = [
  { label: "All", value: undefined },
  { label: "Real data", value: "measured" },
  { label: "Simulation", value: "simulated" },
];

/**
 * Filter by data kind.
 *
 * Links rather than client-side state: the filter is reflected in the URL, so
 * a filtered view is shareable and works without JavaScript.
 */
export function FilterBar({ active }: { active?: DataKind }) {
  return (
    <nav className="flex gap-1 rounded-lg border border-edge bg-panel/60 p-1">
      {OPTIONS.map(({ label, value }) => {
        const isActive = active === value;
        return (
          <Link
            key={label}
            href={value ? `/explore?kind=${value}` : "/explore"}
            aria-current={isActive ? "page" : undefined}
            className={[
              "rounded-md px-3 py-1.5 text-xs transition-colors",
              isActive
                ? "bg-mint/15 text-mint ring-1 ring-mint/40"
                : "text-muted hover:text-paper",
            ].join(" ")}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
