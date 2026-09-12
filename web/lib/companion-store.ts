/**
 * Whether narrator commentary is shown, as an external store.
 *
 * `useSyncExternalStore` rather than an effect. The preference lives in
 * `localStorage`, which does not exist during server rendering, so reading it
 * in a render or a lazy initialiser either crashes on the server or produces a
 * hydration mismatch. An effect avoids both but sets state synchronously,
 * which React 19 flags because it causes a cascading render.
 *
 * This hook is the intended answer: a subscribe function, a client snapshot
 * and a separate server snapshot. React reads the right one in each
 * environment and re-renders only when the store actually changes.
 */
const KEY = "collider:companion";
const EVENT = "collider:companion";

const listeners = new Set<() => void>();

export function subscribe(onChange: () => void): () => void {
  listeners.add(onChange);
  const onExternal = () => onChange();
  // Same tab changes broadcast a custom event; other tabs arrive via storage.
  window.addEventListener(EVENT, onExternal);
  window.addEventListener("storage", onExternal);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener(EVENT, onExternal);
    window.removeEventListener("storage", onExternal);
  };
}

export function getSnapshot(): boolean {
  try {
    return window.localStorage.getItem(KEY) !== "off";
  } catch {
    // Private mode or storage disabled. Commentary stays on.
    return true;
  }
}

/** Commentary is on by default, so the server renders it. */
export function getServerSnapshot(): boolean {
  return true;
}

export function setCompanionEnabled(enabled: boolean): void {
  try {
    window.localStorage.setItem(KEY, enabled ? "on" : "off");
  } catch {
    // Not persisting is acceptable; the session still respects the choice.
  }
  window.dispatchEvent(new Event(EVENT));
  listeners.forEach((l) => l());
}
