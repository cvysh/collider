# ADR-0002: MVP architecture scope

- **Status:** Proposed
- **Date:** 2026-09-12

## Context

SPEC §43/§44 propose Next.js on Vercel + FastAPI + Postgres + object storage.
For the MVP's actual workload — a few hundred curated events and a tree model
over ~20 tabular features — most of that is not load-bearing:

- Inference on such a model is sub-millisecond. Predictions are deterministic
  for a fixed (event, model, feature-set) triple, so they can be precomputed
  during ETL.
- A few hundred event summaries is a JSON manifest of tens of kilobytes, which
  a CDN serves faster than any database query.

Some of the stack is therefore justified by **learning goals** rather than by
load. That is a legitimate reason, but it must be stated rather than disguised.

## Decision

Stage the infrastructure, and record which parts are which:

| Component | Justification |
|---|---|
| Python ETL + `uproot` | Load-bearing. No alternative. |
| scikit-learn / XGBoost | Load-bearing. |
| Static event JSON on CDN | Load-bearing, and faster than the alternative. |
| Precomputed predictions | Load-bearing for the MVP's latency target. |
| Next.js frontend | Load-bearing. |
| Three.js event display | Load-bearing — it is the product. |
| FastAPI service | **Pedagogical.** Real for live/custom inference; not required for the curated path. |
| Postgres | **Pedagogical** at MVP scale. Becomes load-bearing with search, filtering at scale, or prediction caching. |

## Consequences

- The MVP ships without a cold-start-prone Python service on the critical path,
  which protects the sub-500 ms inference target on free hosting tiers.
- The `<500 ms` inference target in SPEC §21.7 is **unachievable** on a free
  serverless Python tier from cold, where starts run tens of seconds.
  Precomputation is what makes the target real.
- The interview answer becomes stronger, not weaker: "here is what the load
  actually required, here is what I built to learn, and I know the difference."

## Rejected for the MVP

Monorepo workspaces (`apps/` + `packages/`), a shared TS/Python schema package,
a four-level LOD system, `InstancedMesh` for particle markers, and prediction
caching tables. Each solves a problem this project does not yet have. Event
object counts are in the tens, not the thousands. API types are generated from
FastAPI's OpenAPI output instead of hand-maintained in a shared package.
