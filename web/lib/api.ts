/**
 * Typed client for the COLLIDER API.
 *
 * Types come from `api-types.ts`, generated from the server's OpenAPI
 * document. They are never hand-written: a hand-maintained copy of a schema
 * drifts from the server silently, and the drift shows up as a runtime
 * surprise rather than a type error.
 *
 * Regenerate after any API change:
 *   python -c "import json;from collider.api.app import create_app;\
 *              print(json.dumps(create_app().openapi()))" > ../docs/openapi.json
 *   npx openapi-typescript ../docs/openapi.json -o lib/api-types.ts
 */
import type { components } from "./api-types";

export type EventSummary = components["schemas"]["EventSummary"];
export type EventPayload = components["schemas"]["EventPayload"];
export type ReconstructedObject = components["schemas"]["ReconstructedObject"];
export type Prediction = components["schemas"]["Prediction"];
export type Provenance = components["schemas"]["Provenance"];
export type ModelInfo = components["schemas"]["ModelInfo"];
export type DataKind = "measured" | "simulated";

/**
 * API base URL.
 *
 * `COLLIDER_API_BASE` is read at runtime on the server; `NEXT_PUBLIC_API_BASE`
 * is inlined at build time and exists for future client-side calls. The
 * default avoids port 8000, which collides with almost every other dev server
 * on a developer machine.
 */
const BASE =
  process.env.COLLIDER_API_BASE ??
  process.env.NEXT_PUBLIC_API_BASE ??
  "http://127.0.0.1:8123";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function get<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
  });
  if (!res.ok) {
    throw new ApiError(res.status, `${res.status} on ${path}`);
  }
  return (await res.json()) as T;
}

export interface ListOptions {
  dataKind?: DataKind;
  limit?: number;
  offset?: number;
}

export async function listEvents(
  opts: ListOptions = {},
): Promise<{ total: number; count: number; events: EventSummary[] }> {
  const q = new URLSearchParams();
  if (opts.dataKind) q.set("data_kind", opts.dataKind);
  q.set("limit", String(opts.limit ?? 200));
  q.set("offset", String(opts.offset ?? 0));
  return get(`/api/events?${q}`);
}

export async function getEvent(id: string): Promise<EventPayload> {
  return get(`/api/events/${encodeURIComponent(id)}`);
}

export async function listModels(): Promise<ModelInfo[]> {
  return get("/api/models");
}
