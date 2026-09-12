"use client";

import { useSyncExternalStore } from "react";
import {
  getServerSnapshot,
  getSnapshot,
  setCompanionEnabled,
  subscribe,
} from "@/lib/companion-store";

/**
 * Global commentary switch.
 *
 * One control in the header rather than a dismiss button on every note. The
 * dialogue is part of the product's voice, but a reader who wants the science
 * without the jokes should be able to say so once and have it stick.
 */
export function useCompanionEnabled(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

export function CompanionToggle() {
  const enabled = useCompanionEnabled();
  return (
    <button
      onClick={() => setCompanionEnabled(!enabled)}
      aria-pressed={enabled}
      className="flex items-center gap-2 border-2 border-ink bg-panel-hi px-2 py-1 text-[11px] text-muted transition-colors hover:text-paper"
      style={{ borderRadius: "9px 5px 10px 4px" }}
    >
      <span
        aria-hidden
        className={`size-2 rounded-full border border-ink ${enabled ? "bg-portal" : "bg-dim"}`}
      />
      commentary {enabled ? "on" : "off"}
    </button>
  );
}
