"use client";

import { useState } from "react";
import { useCompanionEnabled } from "./Companion";

/**
 * Wrapper providing dismiss behaviour and honouring the global switch.
 *
 * The only interactive part of a narrator line, kept separate so the line
 * itself renders on the server and the client bundle stays small.
 */
export function DismissibleNote({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const [dismissed, setDismissed] = useState(false);
  const enabled = useCompanionEnabled();

  if (dismissed || !enabled) return null;

  return (
    <div className={className} role="note">
      {children}
      <button
        onClick={() => setDismissed(true)}
        className="shrink-0 rounded px-1 text-dim transition-colors hover:text-paper focus:outline-none focus-visible:ring-1 focus-visible:ring-portal/60"
        aria-label="Dismiss this note"
      >
        ×
      </button>
    </div>
  );
}
