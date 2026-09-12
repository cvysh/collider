# COLLIDER
## An Interactive CERN Open-Data + Machine Learning Laboratory

**Project specification / product requirements / technical architecture / visual design system / implementation roadmap**

**Status:** Build specification
**Prepared:** 12 September 2026
**Primary goal:** Build a technically serious, visually memorable portfolio project that combines CERN particle-physics open data, machine learning, scientific visualization, interactive 3D, modern web engineering, and AI-assisted software development.

---

# 0. Executive Summary

COLLIDER is an interactive web application for exploring particle-collision data and learning what an event means physically and computationally.

The product should not be a generic dashboard and should not be a thin wrapper around an LLM. Its core loop is:

```text
EXPLORE  →  INSPECT  →  UNDERSTAND  →  ANALYSE  →  PREDICT  →  EXPLAIN
```

A visitor selects a collision event from a curated CERN-derived dataset. COLLIDER loads only the event needed for that session, renders a stylized interactive detector/event scene in the browser, lets the visitor inspect reconstructed particles and derived quantities, and can run a machine-learning model over the event or its relevant features. The result is presented as a probability/score together with the physics features that drove the result.

The first major ML task should be a signal-vs-background problem based on a suitable open educational dataset, with Higgs-related classification as the first flagship experiment. The architecture must remain general enough to add other problems later, such as Z/top/jet classification or anomaly detection.

The product should feel like an experimental laboratory from an intelligent adult sci-fi cartoon: dark space/science setting, hand-drawn annotations, exaggerated micro-copy, irregular panels, expressive original cartoon characters, playful machinery, and visual humor. The design should be inspired by the energy and irreverence of that genre rather than copying copyrighted characters, exact art, logos, dialogue, or production assets.

The project should be built in stages. The scientific pipeline must work before the 3D experience becomes elaborate. The 3D layer must be optimized so the site does not become slow just because it has animation.

---

# 1. What COLLIDER Actually Does

## 1.1 Product definition

COLLIDER is an **interactive particle-event exploration and ML analysis application**.

It has three primary layers:

### Layer A: EXPLORE

The user browses a curated set of particle-collision events.

For an event the application can show:

- event ID
- run number if relevant
- experiment/detector
- collision energy when the metadata supports it
- event category
- number of reconstructed objects
- particle/object types
- event thumbnail
- links/citations to the originating CERN dataset

The user selects one event.

### Layer B: UNDERSTAND

The user enters an interactive event-display-like environment.

They can:

- orbit/rotate the view
- zoom and pan
- click a reconstructed object
- highlight a track
- isolate a particle type
- hide/show layers
- inspect momentum and energy
- inspect transverse momentum
- inspect pseudorapidity and azimuth when available
- inspect charge when relevant
- inspect derived quantities
- calculate/visualize invariant masses for valid object combinations
- compare the event against related events

This is the scientific-visualization layer.

### Layer C: PREDICT

The user can run the ML pipeline.

Example:

```text
Event
  ↓
Feature extraction
  ↓
Preprocessing
  ↓
ML model
  ↓
Probability / class / anomaly score
  ↓
Explanation
```

Example UI:

```text
MODEL ANALYSIS

Higgs-like signal probability
██████████████████░░  87.4%

Classification: SIGNAL CANDIDATE

Top contributing features
• invariant mass
• lepton multiplicity
• transverse-momentum pattern
• event topology
```

The model must never be presented as a scientific discovery engine. It is a portfolio/educational model operating on a defined dataset and task. Results must be described with the dataset's labels, assumptions, and limitations.

---

# 2. Why This Is a Strong Portfolio Project

The project is intentionally cross-disciplinary.

It can demonstrate:

- Python
- NumPy
- Pandas / Polars
- statistics
- exploratory data analysis
- scientific computing
- feature engineering
- classical machine learning
- PyTorch / deep learning
- model evaluation
- explainability
- data pipelines
- REST APIs
- FastAPI
- TypeScript
- Next.js / React
- WebGL / Three.js
- GPU-aware rendering
- caching
- object storage
- PostgreSQL
- deployment
- testing
- observability
- performance engineering
- AI-assisted software development

The project should evolve with the developer's learning roadmap.

The project is not meant to be completed as one giant code generation task. Each major subsystem should correspond to something the developer understands and can explain.

---

# 3. Product Goals

## 3.1 Primary goals

1. Make particle-physics data approachable without reducing it to meaningless animation.
2. Make the 3D event display visually memorable.
3. Use real CERN/Open Data-derived inputs instead of invented toy values for the main demonstrations.
4. Build at least one meaningful ML experiment end-to-end.
5. Make the ML result reproducible.
6. Explain what the model is doing rather than only showing a confidence number.
7. Keep the initial web experience fast.
8. Keep raw/source datasets out of the browser.
9. Give every scientific result traceability to a dataset/version and preprocessing pipeline.
10. Build an architecture that can grow into multiple physics tasks.

## 3.2 Secondary goals

- Make the website fun enough that a non-physicist will explore it.
- Make it useful as a learning tool.
- Make it visually strong enough for a portfolio case study.
- Make the codebase clean enough to demonstrate engineering ability.
- Use Claude Code heavily for implementation, refactoring, tests, and debugging while keeping the developer responsible for understanding architecture and results.

## 3.3 Non-goals for the first release

Do not attempt to:

- host the entire CERN Open Data corpus
- reproduce the complete CMS/ATLAS detector in photorealistic detail
- run large-scale physics reconstruction from raw detector hits in the browser
- claim a new physics discovery
- train enormous foundation models
- build a social network around particle physics
- build user accounts before the core experience works
- build a conversational AI before the core scientific workflow works

---

# 4. Official Data Foundation

CERN's Open Data Portal provides datasets, software, documentation, and visualization resources across experiments including ATLAS and CMS. The portal itself links users to event visualisation and basic histogramming resources. [CERN Open Data Portal](https://opendata.cern.ch/)

ATLAS Open Data currently provides educational analysis material including histogram tools, Jupyter notebooks, physics analyses, and event-display visualization resources. [ATLAS Open Data](https://atlas.cern/Resources/Opendata)

CMS Open Data includes downloadable datasets, primary/simulated datasets, analysis tools, and educational documentation. [CMS Open Data documentation](https://opendata.cern.ch/docs/about-cms)

The project must record for each dataset:

- experiment
- dataset name
- dataset/version identifier if provided
- DOI or official record identifier when available
- license/usage conditions
- source URL
- date accessed
- preprocessing script version
- feature schema version
- model version used with it

This metadata belongs in the repository and in the deployed application where appropriate.

---

# 5. Recommended First Scientific Problem

## 5.1 First flagship experiment: signal vs background

The first ML task should be chosen from a CERN/ATLAS/CMS educational dataset that has:

- a clear target label
- manageable feature dimensions
- a reproducible training/test split
- enough documentation to explain the physics and features
- a problem that can be solved first with classical ML and later with deep learning

A Higgs-related signal/background task is recommended as the first flagship because it naturally produces compelling product interactions:

```text
EVENT
  ↓
particle/event features
  ↓
model
  ↓
signal probability
  ↓
physics explanation
```

The exact dataset must be selected from the official CERN/ATLAS/CMS material rather than invented in code.

ATLAS Open Data explicitly offers tutorials and tools covering event visualization and analyses involving Higgs and Z-boson physics, making it a strong source for the educational side of this project. [ATLAS Open Data](https://atlas.cern/Resources/Opendata)

## 5.2 Future ML tasks

Potential second-generation tasks:

- Z-boson candidate classification
- top-quark / jet classification
- particle identification
- jet flavor classification
- anomaly detection
- event similarity search
- learned event embeddings
- graph neural networks over particle/event structures
- transformer-based particle classification

The data contract should therefore not hard-code the word `Higgs` everywhere.

Use generic abstractions such as:

```text
Task
Model
FeatureSet
LabelSpace
Event
Prediction
Explanation
```

Higgs becomes one implementation of a task.

---

# 6. Core User Journey

## 6.1 Landing page

User sees:

```text
COLLIDER

REAL PARTICLES.
REAL DATA.
REAL AI.

[ EXPLORE COLLISIONS ]
[ HOW IT WORKS ]
```

A small stylized detector/cosmic background animation is allowed, but the landing page must remain light enough to load quickly.

Do not initialize the full Three.js event scene on the landing page.

## 6.2 Explore screen

The user sees a searchable/filterable list of curated events.

Example filters:

- Higgs candidate
- 4-lepton
- photon-rich
- high energy
- rare-looking
- model uncertainty
- random

The event browser should support:

- search
- sorting
- filtering
- small static preview image or lightweight event thumbnail
- event metadata
- direct link/share URL

## 6.3 Event screen

The event screen is the main application.

Layout:

```text
┌────────────────────────────────────────────────────┐
│ Event #1847291                     [Share] [Fullscreen]
├────────────────────────────────────────────────────┤
│                                                    │
│                 3D EVENT VIEW                     │
│                                                    │
│              collision + tracks                   │
│                                                    │
├──────────────────────────┬─────────────────────────┤
│ particle list             │ event information      │
│                           │ energy                 │
│ μ+   46.2 GeV            │ detector               │
│ μ-   38.7 GeV            │ object counts          │
│ e+   31.1 GeV             │                         │
│ e-   29.8 GeV             │ [ANALYSE EVENT]        │
└──────────────────────────┴─────────────────────────┘
```

## 6.4 Particle inspection

Clicking a particle opens a compact HUD/card.

Example:

```text
MUON (μ−)

Momentum             46.2 GeV
Transverse momentum  38.1 GeV
Pseudorapidity        -1.23
Azimuthal angle        2.41
Charge                   -1

[ HIGHLIGHT TRACK ]
```

The values should come from the selected event's available fields. If a field is not present, the UI must say that it is unavailable instead of fabricating it.

## 6.5 Analyze event

The user clicks:

```text
ANALYSE EVENT
```

The application immediately renders the event and shows an independent analysis status layer.

Do not block the 3D visualization while inference occurs.

Recommended state progression:

```text
QUEUED
  ↓
VALIDATING EVENT
  ↓
EXTRACTING FEATURES
  ↓
RUNNING MODEL
  ↓
CALCULATING EXPLANATION
  ↓
COMPLETE
```

## 6.6 Prediction screen

The result should show:

- class/probability
- threshold used
- model name/version
- dataset/task name
- top features
- confidence/uncertainty wording appropriate to the actual model
- important caveats
- link to model methodology

Example:

```text
HIGGS-LIKE SIGNAL

87.4%

Model: XGBoost v0.3.1
Task: signal-vs-background
Feature set: event-features-v2

WHY?

+ invariant mass
+ lepton multiplicity
+ transverse momentum pattern
- background-like topology

[ EXPLAIN ]  [ COMPARE ]
```

Do not show a percentage without context.

---

# 7. Educational / Scientific Explanation Layer

A central requirement is that users should be able to move from “cool animation” to “I understand what I am looking at.”

Each important scientific term should have a short plain-language explanation.

Example:

### Invariant mass

```text
A quantity calculated from the combined energy and momentum
of a set of particles. Resonances can produce characteristic
peaks in invariant-mass distributions.
```

The application should be able to switch between:

```text
BEGINNER
INTERMEDIATE
TECHNICAL
```

The content should not pretend to be a formal physics textbook. Link to the official CERN/ATLAS/CMS resources for deeper reading.

---

# 8. Data Architecture

## 8.1 Critical rule

**Never put the full CERN dataset into the browser.**

The raw data stays offline/on the source platform or in controlled preprocessing storage. The application hosts only the curated/processed artifacts needed by the product.

The browser should typically receive:

- one event
- its metadata
- the model's prediction
- small supporting data

It should not receive a giant raw dataset merely to locate one event.

## 8.2 High-level data flow

```text
                    CERN Open Data
                          │
                          ▼
                 Raw dataset acquisition
                          │
                          ▼
                   Local / batch ETL
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       Curated event data       ML training data
              │                       │
              │                 ┌─────┴─────┐
              │                 │           │
              │                 ▼           ▼
              │              XGBoost    PyTorch
              │                 │           │
              │                 └─────┬─────┘
              │                       │
              ▼                       ▼
        Object storage             Model artifact
              │                       │
              └──────────┬────────────┘
                         ▼
                     Application API
                         │
                    Next.js frontend
                         │
              ┌──────────┴──────────┐
              │                     │
          normal web UI          Three.js
                                    │
                                  GPU
```

## 8.3 Storage recommendation

The simplest first production architecture is:

- **PostgreSQL** for structured metadata
- **Object storage** for processed event files and static artifacts
- **Vercel** for frontend/web deployment
- **FastAPI** or equivalent server/API layer for ML inference

Supabase is a strong one-provider choice because its product includes full PostgreSQL plus Storage. Supabase Storage is object storage with CDN delivery and access controls, while the database is real Postgres rather than a proprietary database abstraction. [Supabase Database](https://supabase.com/docs/guides/database/overview) [Supabase Storage](https://supabase.com/docs/guides/storage)

Vercel Blob is an alternative object-storage option for unstructured assets and integrates naturally with a Vercel/Next.js deployment. [Vercel Blob](https://vercel.com/storage/blob)

Do not lock the application to a specific provider in code. Create an internal `ObjectStore` interface so storage can be replaced.

---

# 9. Database Design

Recommended initial tables:

## `events`

```text
id
external_event_id
experiment
detector
run_number
event_number
collision_energy
category
source_dataset
source_record_url
source_doi
storage_path
schema_version
created_at
```

## `event_objects`

```text
event_id
object_id
object_type
charge
px
py
pz
energy
pt
eta
phi
mass
metadata_json
```

Only include columns actually justified by the source dataset.

## `datasets`

```text
dataset_id
experiment
name
version
source_url
doi
license
accessed_at
schema_version
notes
```

## `models`

```text
model_id
name
version
task_id
artifact_path
framework
training_dataset_id
feature_set_version
metrics_json
created_at
```

## `predictions`

```text
id
event_id
model_id
prediction
probability
threshold
explanation_json
created_at
latency_ms
```

Predictions may be cached. A prediction should be deterministic for the same model version, preprocessing version, event version, and inference configuration.

---

# 10. Object Storage Layout

Recommended:

```text
collider/
├── events/
│   ├── v1/
│   │   ├── 1847291.json.gz
│   │   ├── 3021456.json.gz
│   │   └── ...
│   └── v2/
├── thumbnails/
│   ├── 1847291.webp
│   └── ...
├── models/
│   ├── task-higgs/
│   │   ├── xgboost-0.3.1.json
│   │   └── metadata.json
│   └── ...
├── datasets/
│   └── manifests/
└── experiments/
    ├── run-001/
    └── run-002/
```

Use versioned paths. Never silently overwrite a production dataset or model artifact.

---

# 11. Event Data Representation

## 11.1 First implementation: compressed JSON

Start with gzip/brotli-compressed JSON because it is easy to inspect and debug.

Example conceptual payload:

```json
{
  "eventId": "1847291",
  "schemaVersion": "1.0",
  "experiment": "CMS",
  "objects": [
    {
      "id": 1,
      "type": "muon",
      "charge": -1,
      "px": 42.1,
      "py": 17.3,
      "pz": 81.4,
      "energy": 94.2
    }
  ],
  "metadata": {
    "category": "4-lepton"
  }
}
```

## 11.2 Later implementation: binary/typed arrays

If performance measurements show JSON parsing or transfer size is important, move to a compact binary representation.

Possible layout:

```text
Float32Array:
[px, py, pz, E, pt, eta, phi, ...]
```

The exact representation should be designed around actual profiling, not premature optimization.

---

# 12. ETL / Preprocessing Pipeline

Create a reproducible data-preparation pipeline.

```text
RAW SOURCE
   ↓
DOWNLOAD / READ
   ↓
VALIDATE
   ↓
NORMALIZE SCHEMA
   ↓
FILTER / SELECT EVENTS
   ↓
DERIVE FEATURES
   ↓
GENERATE EVENT REPRESENTATION
   ↓
GENERATE PREVIEWS
   ↓
WRITE MANIFEST
   ↓
UPLOAD ARTIFACTS
```

The ETL pipeline must be executable from the repository.

Example command:

```bash
python -m collider_pipeline.prepare \
  --dataset path/to/source \
  --output data/processed \
  --schema-version 1
```

## 12.1 Reproducibility requirements

Record:

- source URL
- source dataset/version
- checksum where practical
- preprocessing code version / git commit
- Python version
- dependency lockfile
- schema version
- feature-set version
- random seed
- train/test split seed

---

# 13. Feature Engineering

The exact feature set depends on the selected dataset.

Potential event-level features may include:

- object multiplicity
- particle-type counts
- total transverse momentum
- leading-object transverse momentum
- summed energy
- missing transverse momentum when available
- invariant masses
- angular separations
- event-shape variables
- topology-related features

Do not automatically compute every conceivable feature. Start with a small interpretable set.

Every feature should have:

```text
name
unit
source
formula/definition
null behavior
normalization
physics interpretation
```

---

# 14. ML Roadmap

The ML stack should grow incrementally.

## Stage 1: Baseline

Implement:

- train/validation/test split
- preprocessing
- logistic regression
- ROC curve
- AUC
- confusion matrix
- precision/recall
- calibration check where meaningful

Goal: establish a transparent baseline.

## Stage 2: Tree model

Try:

- random forest
- gradient boosting / XGBoost or another suitable library

Record:

- training time
- AUC
- precision
- recall
- inference latency
- feature importance

## Stage 3: Neural network

Implement a modest PyTorch MLP.

Do not use a huge model simply because deep learning is fashionable.

Document:

- architecture
- parameter count
- activation functions
- optimizer
- learning rate
- batch size
- epochs
- regularization
- early stopping

## Stage 4: Specialized representation

Only after the simple models are understood:

- sequence models
- graph representations
- particle/event transformers

This is future scope.

---

# 15. ML Explanation Layer

The product should never stop at:

```text
87.4%
```

It should explain the model in a way appropriate to the model type.

Possible techniques:

- permutation importance
- SHAP for supported tabular models
- ablation analysis
- feature contribution plots
- counterfactual feature changes where scientifically reasonable

The UI should distinguish:

```text
MODEL FACT
```

from:

```text
PHYSICS INTERPRETATION
```

The application should not claim that an explanation method proves causality.

---

# 16. Inference Architecture

## 16.1 Preferred pattern

```text
Browser
  │
  │ GET /events/:id
  ▼
API
  │
  ├── metadata lookup
  └── event URL / payload

Browser
  │
  │ POST /predict
  │ {eventId, modelVersion}
  ▼
Inference service
  │
  ├── load model
  ├── load feature config
  ├── transform event
  ├── predict
  └── generate explanation
  │
  ▼
Prediction JSON
```

## 16.2 Do not block rendering on inference

The event view should render independently.

The desired experience:

```text
0 ms     request event
100 ms   event payload starts rendering
250 ms   3D scene usable
300 ms   inference begins/continues
500 ms   prediction appears
```

These numbers are initial engineering targets, not guaranteed production values.

---

# 17. API Design

## `GET /api/events`

Parameters:

```text
q
category
experiment
limit
cursor
```

Returns paginated summaries.

## `GET /api/events/:id`

Returns event metadata plus a reference to the event payload.

## `GET /api/events/:id/objects`

Returns event objects if not bundled into the event response.

## `POST /api/predict`

Request:

```json
{
  "eventId": "1847291",
  "modelVersion": "xgb-0.3.1"
}
```

Response:

```json
{
  "eventId": "1847291",
  "modelVersion": "xgb-0.3.1",
  "task": "signal-vs-background",
  "class": "signal",
  "probability": 0.874,
  "explanations": [
    {
      "feature": "invariant_mass",
      "direction": "positive",
      "importance": 0.41
    }
  ],
  "latencyMs": 184
}
```

## `GET /api/models`

Returns deployed model versions and supported tasks.

---

# 18. Frontend Architecture

Recommended:

- Next.js
- TypeScript
- React
- Tailwind CSS or a controlled CSS system
- Three.js
- React Three Fiber only if it genuinely improves developer velocity without causing excessive abstraction
- Zustand or another small state manager if needed
- Zod for runtime validation of API payloads

Do not put scientific data calculations into arbitrary React components.

Use domain modules:

```text
src/
├── app/
├── components/
├── features/
│   ├── events/
│   ├── analysis/
│   ├── predictions/
│   └── education/
├── lib/
├── physics/
├── rendering/
├── api/
└── styles/
```

---

# 19. 3D Rendering Architecture

## 19.1 Core scene

The scene contains:

1. collision origin
2. reconstructed tracks
3. particle markers
4. simplified detector layers
5. labels/HUDs
6. optional particle effects
7. subtle ambient background

## 19.2 Rendering principles

The target is a polished, stylized event display, not a CAD model.

Avoid:

- unnecessary high-poly meshes
- thousands of React DOM nodes
- one Mesh per particle when instances would work
- huge textures
- real-time expensive physics simulations
- excessive bloom/post-processing
- multiple full-screen particle systems running continuously

Three.js provides `InstancedMesh` specifically for rendering many objects that share geometry/material while reducing draw calls, which is useful for repeated markers or detector elements. [Three.js InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html)

## 19.3 Track rendering

Tracks should preferably be represented through efficient buffer-based line geometry.

Possible grouping:

```text
muon tracks      → geometry/material group
electron tracks  → geometry/material group
photon tracks    → geometry/material group
other tracks     → geometry/material group
```

## 19.4 Level of detail

Implement LOD conceptually:

### LOD 0

Basic event skeleton.

### LOD 1

Tracks and particle markers.

### LOD 2

Detector layers and additional metadata.

### LOD 3

Detailed hit-level/secondary details where supported.

The exact LOD system should be driven by actual content and profiler measurements.

## 19.5 Frustum culling

The renderer should avoid work for objects outside the camera's view where feasible.

## 19.6 GPU strategy

The visual scene should be designed around GPU-friendly buffers and limited draw calls.

---

# 20. Animation Strategy

Animation should be used to communicate state, not to continuously waste compute.

### Good animation

- camera entry
- track reveal
- subtle detector glow
- particle highlight
- scanline
- loading sequence
- analysis status transitions
- hover/selection response

### Bad animation

- every object constantly pulsing
- huge background particle fields
- dozens of DOM animations on top of WebGL
- physics simulation running simply for decoration
- continuous expensive post-processing

The collision event itself can be static while camera, highlights, and limited shaders provide the feeling of life.

---

# 21. Performance Strategy

The project must treat performance as a first-class feature.

## 21.1 Performance layers

There are four major bottlenecks:

1. initial network transfer
2. JavaScript execution
3. data parsing
4. GPU rendering

Optimizations must target the correct bottleneck.

## 21.2 Landing page

Do not load the full event-rendering bundle immediately.

Use code splitting / lazy loading for the heavy 3D experience.

Target:

- fast first content
- low JS on landing
- no giant dataset downloads
- no full event scene initialization until needed

## 21.3 Event loading

Only load the selected event.

Example:

```text
User opens event #1847291
       ↓
GET /events/1847291
       ↓
small compressed payload
       ↓
parse
       ↓
GPU buffers
```

## 21.4 Caching

Cache immutable event artifacts aggressively.

An event payload with a versioned path can be treated as immutable:

```text
/events/v1/1847291.json.gz
```

If the event changes, create a new version rather than mutating the old artifact.

## 21.5 CDN

Use a CDN-backed object-storage path for processed assets.

Supabase Storage provides CDN-backed asset delivery, and Vercel Blob provides globally delivered object storage. Choose one rather than adding unnecessary infrastructure. [Supabase Storage](https://supabase.com/docs/guides/storage) [Vercel Blob](https://vercel.com/storage/blob)

## 21.6 Data compression

Start with compressed JSON.

Only implement binary formats if measurements show that JSON transfer/parsing is a material bottleneck.

## 21.7 Rendering targets

Initial engineering targets:

```text
Landing first meaningful render: < 1.5 s on a typical modern laptop
3D initialization after event selection: < 1.0 s target
Event payload: ideally < 100 KB compressed for curated events
Steady-state render target: ~60 FPS on a modern laptop
Draw calls: keep low and measure continuously
Inference: ideally < 500 ms for the first hosted model
```

These are project targets, not promises.

---

# 22. Performance Instrumentation

The application should have a developer-only performance panel.

Example:

```text
COLLIDER PERFORMANCE

FPS             60
Frame time      16.4 ms
Draw calls      24
Triangles       82,412
Textures        7
Event payload   41 KB
JS loaded       312 KB
Inference       184 ms
Memory          N/A / browser dependent
```

Use browser profiling tools and Three.js instrumentation rather than guessing.

Every major optimization should be backed by before/after measurements.

---

# 23. Visual Design Direction

## 23.1 Creative direction

The target visual language is:

**adult sci-fi cartoon laboratory + chaotic genius energy + CERN instrumentation + cosmic night + hand-drawn annotation**

It should feel like:

- a dangerous-looking science machine built by an eccentric genius
- a cartoon observatory
- a spaceship control room
- a particle-physics lab
- a data-analysis terminal

The inspiration is the irreverent visual energy of *Rick and Morty*, but the production should use **original characters, original illustrations, original jokes, original dialogue, original icons, and original assets**.

Do not use:

- Rick or Morty character art
- copyrighted screenshots
- exact show frames
- copied dialogue
- copied logos
- portal-gun artwork
- copyrighted background art

The goal is the aesthetic vocabulary, not asset imitation.

---

# 24. Visual System

## 24.1 Color palette

Base:

```text
Near-black          #07100F
Deep space          #07131A
Panel navy          #0D1A22
```

Primary accent:

```text
Radioactive mint    #69F7C6
```

Secondary accent:

```text
Electric cyan      #39C9FF
```

Warning:

```text
Plasma orange      #FF9D3D
```

Danger:

```text
Hot red            #FF5D5D
```

Paper/annotation:

```text
Off-white           #F2F0E9
```

Use accents sparingly. Most of the UI remains dark.

## 24.2 Typography

Primary UI:

- modern grotesk/sans-serif
- wide display lettering for brand
- clean numeric typography

Technical labels:

- monospace

Annotations:

- handwriting-inspired font used sparingly

Do not make the entire interface look handwritten. The science/data UI must remain legible.

## 24.3 Borders

Use slightly irregular rounded panels rather than sterile corporate rectangles.

Possible pattern:

```text
╭──────────────────────────────╮
│ EVENT #1847291               │
│                              │
│             125.3 GeV        │
╰──────────────────────────────╯
```

Some modules can have intentionally uneven corners or hand-drawn underline marks.

## 24.4 Texture

Subtle:

- paper grain
- CRT-like scan texture
- tiny stars
- marker strokes
- technical grid lines

Avoid strong noise that interferes with readability.

---

# 25. Character / Illustration Direction

Use an original pair of recurring cartoon scientists.

Character A:

- eccentric senior scientist
- spiky/untamed hair silhouette without copying an existing character
- lab coat
- bored or smug expressions
- frequently appears beside the AI/instrumentation panels

Character B:

- younger student/intern character
- more expressive
- asks obvious questions
- occasionally points at absurdly complicated physics diagrams

They are visual narrators, not required for every screen.

Use them for:

- onboarding
- empty states
- educational tooltips
- loading sequences
- 404 page
- “something went wrong” states
- occasional Easter eggs

Do not let them dominate scientific screens.

---

# 26. Micro-copy Direction

The copy should be technically correct but playful.

Examples:

```text
Scanning the collision...

The particles are doing something suspicious.

This is either physics or a very expensive coincidence.

Crunching numbers. Please don't touch the machine.

Model says: probably interesting.

Physics says: let's check.

We found a bump.

No, not that kind of bump.
```

Avoid fake scientific claims.

Never say:

```text
WE DISCOVERED THE HIGGS BOSON
```

when the system merely classified an educational sample.

Prefer:

```text
HIGGS-LIKE SIGNAL CANDIDATE
```

or whatever terminology is justified by the dataset.

---

# 27. Landing Page Design

Conceptual sequence:

```text
[dark starfield]

            COLLIDER

    REAL PARTICLES.
       REAL DATA.
         REAL AI.

       [EXPLORE]

small original cartoon scientist silhouette
standing near a detector panel
```

Background:

- stylized horizon / planet-like curve
- simplified detector rings
- tiny stars
- subtle particle paths

Animation:

- gentle camera drift
- slow track movement
- occasional tiny signal pulse

Performance constraint:

The landing page must not instantiate the full event explorer.

---

# 28. Explore Page Design

The explore page should feel like a cartoon control console.

Left rail:

```text
◉ Explore
⌁ Analyse
? Learn
⚙ About
```

Main panel:

```text
BROWSE COLLISIONS

[ search ----------------------- ]

[ Higgs ] [ 4 leptons ] [ Random ]

┌───────────────────────────────┐
│ miniature event visualization │
│                               │
│ EVENT #1847291                │
│ 4-lepton event                │
│ 125.3 GeV                     │
│                         VIEW →│
└───────────────────────────────┘
```

Cards can have slightly irregular illustrations.

---

# 29. Event Viewer Design

The 3D viewer should dominate the screen.

Controls should be obvious but compact:

```text
[ORBIT]
[ZOOM]
[PAN]
[SELECT]
```

Right-side event panel:

```text
EVENT #1847291

Detector      CMS
Objects       24
Muons          4
Electrons      2
Photons        0
Jets           6

Collision energy
13 TeV
```

Do not show metrics not supported by the selected event.

---

# 30. AI Analysis Animation

When the user presses ANALYSE:

```text
        AI ANALYSIS

✓ Processing event data
✓ Extracting features
✓ Running model inference
✓ Comparing with learned patterns
✓ Generating explanation

            [ DONE ]
```

Visual effect:

- glowing cyan/mint AI core
- lines from particle tracks into an abstract neural structure
- small bursts of data
- minimal motion

This is a UI metaphor. It must not imply that a physically realistic “AI cloud” exists inside the detector.

---

# 31. Prediction Screen

The result card should visually resemble a laboratory instrument readout.

```text
╭──────────────────────────────────────╮
│ ANALYSIS RESULT                      │
│                                      │
│ HIGGS-LIKE SIGNAL                    │
│                                      │
│ 87.4%                                │
│ ██████████████████░░                 │
│                                      │
│ Invariant mass       125.3 GeV       │
│ Model                XGBoost 0.3.1   │
│                                      │
│ [ WHY? ]  [ COMPARE ]               │
╰──────────────────────────────────────╯
```

A small original cartoon scientist can react in a corner:

```text
Scientist:
“Okay. That's interesting.”
```

Do not turn a serious result into a meme.

---

# 32. Physics Visualization Screen

A flagship visualization should show an invariant-mass-like distribution or other scientifically appropriate distribution.

The key aesthetic moment is the appearance of a peak/signature.

Sequence:

```text
Background distribution
        ↓
add selected event
        ↓
show its contribution
        ↓
highlight relevant region
        ↓
explain what the region means
```

This gives the user a feeling of discovering structure in the data.

The visualization must use real data from the selected task, not a fake curve merely designed to look impressive.

---

# 33. Compare Mode

A later feature can compare two events.

```text
EVENT A                 EVENT B
────────                ────────
objects: 24             objects: 18
leptons: 4              leptons: 2
mass: 125.3 GeV         mass: 91.2 GeV
score: 0.874            score: 0.129
```

3D scenes could be shown side-by-side.

Comparison should be implemented after the single-event experience is stable.

---

# 34. Discovery / Challenge Mode

Potential feature after MVP:

```text
FIND THE SIGNAL

You have 20 events.
One contains a signal-like event.
Can you find it before the model?

[ BEGIN ]
```

The user can inspect events manually and submit a guess.

Then reveal:

```text
YOUR PICK: #1847291
MODEL PICK: #1847291
DATA LABEL: SIGNAL
```

This turns the project into a learning game while keeping the scientific core intact.

---

# 35. Loading States

Loading states are part of the aesthetic.

Examples:

```text
CALIBRATING DETECTOR...
```

```text
TRACKS FOUND.
```

```text
SOMETHING INTERESTING IS HAPPENING.
```

```text
RUNNING THE NUMBERS...
```

Use short animations and progress indicators.

Do not fake progress percentages if the underlying operation has no measurable progress.

---

# 36. Empty / Error States

## No events found

```text
NOTHING HERE.

Either the collision doesn't exist,
or you asked for something extremely specific.
```

## Server error

```text
THE MACHINE DISAGREED WITH US.

Try again.
```

## Missing data

```text
THIS EVENT DOESN'T CONTAIN THAT MEASUREMENT.

We won't invent it.
```

That last message is especially important for scientific integrity.

---

# 37. Accessibility

Even though this is highly visual, it must remain usable.

Requirements:

- keyboard navigation for major controls
- accessible buttons
- readable contrast
- text alternative for critical event information
- 3D interaction must have a 2D fallback summary
- reduced-motion mode
- mobile fallback
- no critical meaning communicated only by color

If reduced motion is enabled:

```text
Disable camera drift
Disable particle pulses
Reduce transitions
Keep functional 3D interaction
```

---

# 38. Responsive Design

Desktop is the primary target.

Target breakpoints:

```text
Large desktop     1440+
Laptop            1024-1439
Tablet            768-1023
Mobile            < 768
```

On mobile, do not try to squeeze the desktop 3D laboratory into a tiny box.

Use:

```text
event summary
↓
2D simplified event visualization
↓
expandable 3D view
```

The full desktop event lab can remain optimized for larger screens.

---

# 39. Security

Even though this is not a security-sensitive product, follow basic rules:

- never expose server-side database secrets
- never expose private storage credentials
- validate API inputs
- validate event IDs
- validate model IDs
- rate-limit public inference endpoints if necessary
- do not accept arbitrary model paths from clients
- use allowlisted model versions
- keep admin/data-preparation operations separate from public endpoints
- use environment variables for secrets

---

# 40. Caching Strategy

Cache immutable resources aggressively:

```text
/static/*
/events/v1/*
/models/public-metadata/*
/thumbnails/*
```

Prediction caching key:

```text
hash(event_id + event_version + model_version + feature_version)
```

If the exact same model and input event are requested again, a cached prediction can be returned.

---

# 41. Observability

Track:

- event load latency
- event payload size
- inference latency
- inference errors
- client FPS if feasible
- JS errors
- failed requests
- model version usage
- most-viewed events

Do not collect unnecessary personal data.

A basic anonymous analytics system is enough at first.

---

# 42. Testing Strategy

## Unit tests

Test:

- physics helper calculations
- event schema parsing
- feature calculations
- preprocessing
- inference output validation
- API validation

## ML tests

Test:

- no train/test leakage
- deterministic preprocessing
- correct feature ordering
- model artifact loads successfully
- inference matches expected schema

## Frontend tests

Test:

- event loading
- empty state
- model loading state
- result rendering
- keyboard accessibility

## Visual regression

Use screenshots for important UI states.

3D scenes can be tested at a lower level through deterministic fixtures rather than relying entirely on pixel-perfect GPU screenshots.

## Performance tests

Have at least one reproducible “benchmark event.”

Measure:

- payload size
- parse time
- scene setup time
- frame time
- draw calls
- triangles
- inference latency

---

# 43. Deployment Architecture

Recommended first production setup:

```text
                        GitHub
                           │
                           ▼
                     CI / checks
                           │
                           ▼
                        Vercel
                           │
                ┌──────────┴──────────┐
                │                     │
             Next.js               API layer
                                      │
                              ┌───────┴────────┐
                              │                │
                          Postgres         Object store
                              │                │
                           metadata       events/models
```

The ML inference service can initially live with the API if the model is lightweight enough.

If inference becomes resource-heavy, move it into a separate service.

Do not introduce Kubernetes, microservices, queues, or GPU clusters unless an actual requirement appears.

---

# 44. Recommended Technology Stack

## Frontend

- Next.js
- TypeScript
- React
- Tailwind or controlled CSS
- Three.js
- optional React Three Fiber
- Zod

## Backend

- Python
- FastAPI
- Pydantic

## Data

- Pandas or Polars
- NumPy
- PyArrow where useful

## ML

- scikit-learn
- XGBoost or equivalent tree model
- PyTorch

## Storage

Option A:

- Supabase Postgres
- Supabase Storage

Option B:

- Vercel for web
- Vercel Blob for object storage
- separate Postgres provider

Start with the minimum number of services.

## Dev tooling

- Git
- GitHub
- Docker where useful
- Ruff
- pytest
- mypy or pyright as appropriate
- ESLint
- Prettier
- Playwright for browser tests

---

# 45. Repository Structure

Recommended monorepo:

```text
collider/
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── rendering/
│   │   ├── lib/
│   │   └── styles/
│   │
│   └── api/
│       ├── app/
│       ├── routes/
│       ├── services/
│       └── models/
│
├── packages/
│   ├── schemas/
│   ├── physics/
│   └── ui/
│
├── ml/
│   ├── notebooks/
│   ├── src/
│   ├── configs/
│   ├── experiments/
│   └── models/
│
├── data-pipeline/
│   ├── src/
│   ├── configs/
│   └── manifests/
│
├── data/
│   ├── README.md
│   └── sample/
│
├── docs/
│   ├── architecture.md
│   ├── data-lineage.md
│   ├── ml.md
│   ├── physics.md
│   └── performance.md
│
├── scripts/
├── tests/
├── .github/
├── README.md
└── LICENSE
```

Do not commit large source datasets to Git.

---

# 46. Data Lineage

Every production event should be traceable.

For example:

```text
UI event #1847291
      ↓
processed event v1
      ↓
source dataset X
      ↓
official CERN record Y
      ↓
preprocessing commit abc123
      ↓
feature schema v2
      ↓
model xgb-0.3.1
```

The UI should provide a small “Data provenance” drawer.

This is one of the strongest differentiators from a generic AI demo.

---

# 47. Model Registry

At minimum, a YAML/JSON registry should describe every model.

Example:

```yaml
id: xgb-0.3.1
task: signal-vs-background
dataset: atlas-higgs-education-v1
features: event-features-v2
framework: xgboost
metrics:
  auc: 0.93
  precision: 0.81
  recall: 0.74
artifact: models/xgb-0.3.1.json
created_at: 2026-09-12
```

The live API should refuse unknown model IDs.

---

# 48. Model Evaluation Page

A serious portfolio project should have a page that shows how the model was evaluated.

Include:

- dataset description
- target definition
- train/validation/test strategy
- class distribution
- baseline model
- final model
- ROC-AUC
- confusion matrix
- precision/recall
- calibration where relevant
- limitations
- feature list
- known failure modes

This page is less flashy than the 3D viewer but is extremely valuable for recruiters/engineers.

---

# 49. “How It Works” Page

A visual architecture explanation:

```text
CERN DATA
   ↓
DATA ENGINEERING
   ↓
FEATURE ENGINEERING
   ↓
MACHINE LEARNING
   ↓
API
   ↓
3D VISUALIZATION
   ↓
YOU
```

Each node expands into a short explanation.

The original cartoon scientist can point to each stage.

---

# 50. AI-Assisted Development Rules

Claude Code should be treated as an engineering partner, not a black-box project generator.

## Rule 1

Every major subsystem needs a human-understandable design note.

## Rule 2

Before implementing a major feature, Claude Code should state:

- what files will change
- why they change
- important tradeoffs
- possible failure modes
- tests required

## Rule 3

Do not accept generated physics formulas without checking them.

## Rule 4

Do not fabricate CERN data.

Generated mock data may exist only in an explicitly labeled development fixture.

## Rule 5

Do not let Claude silently alter scientific definitions.

## Rule 6

Use Claude for:

- implementation
- debugging
- refactoring
- test generation
- documentation
- profiling assistance
- API scaffolding
- UI implementation
- shader experimentation

The developer remains responsible for:

- understanding the dataset
- choosing the ML task
- validating results
- understanding metrics
- understanding architecture
- explaining the physics

---

# 51. Claude Code Project Instructions

Add a project-level instruction file containing rules similar to:

```text
You are working on COLLIDER, an interactive CERN Open Data + ML application.

Before changing architecture, inspect existing documentation.
Do not invent scientific facts or fabricate source data.
Do not claim a model proves a physics discovery.
Prefer small, testable modules.
Do not add dependencies without explaining why they are needed.
Do not load large datasets into the browser.
Do not initialize Three.js globally on pages that do not need it.
Prefer GPU-friendly rendering patterns.
Use typed schemas for API responses.
Preserve dataset/model versioning.
Every major feature must include tests.
Measure before optimizing.
Do not turn a performance problem into an infrastructure problem without profiling.
Keep the aesthetic playful but scientifically honest.
Use original artwork/characters; do not include copyrighted show assets.
```

---

# 52. Development Phases

## Phase 0: Research and setup

Deliverables:

- choose official dataset
- read official documentation
- establish data license/citation notes
- create repository
- set up Python environment
- set up frontend skeleton
- write architecture document

No fancy UI yet.

## Phase 1: Data understanding

Deliverables:

- load data
- inspect schema
- create EDA notebook
- understand labels
- understand class balance
- document features
- create first visualizations

This is the first major learning milestone.

## Phase 2: ML baseline

Deliverables:

- preprocessing pipeline
- baseline classifier
- evaluation
- metrics
- model artifact
- model registry entry

At the end of this phase, the ML task must actually work.

## Phase 3: Event representation

Deliverables:

- event schema
- curated event manifest
- JSON fixture format
- static event previews
- API endpoint

## Phase 4: 3D prototype

Deliverables:

- collision origin
- tracks
- particles
- camera
- selection
- labels

No elaborate visual polish yet.

## Phase 5: Product UI

Deliverables:

- landing page
- explorer
- event page
- analysis panel
- result page

## Phase 6: Cartoon-scifi art direction

Deliverables:

- original characters
- illustrations
- annotations
- expressive loading states
- custom icons
- backgrounds
- typography system

## Phase 7: Performance pass

Deliverables:

- bundle measurement
- lazy loading
- event compression
- caching
- instancing where appropriate
- draw-call measurement
- mobile/reduced-motion fallback

## Phase 8: Deployment

Deliverables:

- production deployment
- domain
- storage
- database
- API
- inference
- monitoring

## Phase 9: Portfolio documentation

Deliverables:

- README
- architecture diagram
- ML methodology
- performance report
- data provenance
- demo video
- screenshots
- lessons learned

---

# 53. MVP Definition

The MVP is complete when a user can:

1. Open the website.
2. Browse at least a curated set of real CERN-derived events.
3. Open one event.
4. Rotate/zoom the event.
5. Select a particle/object.
6. See its available properties.
7. Click ANALYSE.
8. Receive a real ML prediction.
9. See at least one explanation/important feature visualization.
10. Inspect the underlying data provenance.
11. Use the website without downloading a massive dataset.
12. Use the website at a reasonable frame rate on a modern laptop.

That is enough.

Everything beyond this is an extension.

---

# 54. V1 Feature Set

Recommended V1:

```text
✓ Landing
✓ Explore events
✓ Event detail
✓ 3D event display
✓ Particle selection
✓ Physics metadata
✓ One ML task
✓ Prediction
✓ Model explanation
✓ Invariant-mass or equivalent scientific visualization
✓ Data provenance
✓ Responsive fallback
✓ Performance panel in development
```

Do not include user accounts yet.

Do not include an LLM assistant yet.

Do not include social features yet.

---

# 55. V2 Feature Set

After V1:

```text
+ event comparison
+ challenge mode
+ multiple ML tasks
+ model comparison
+ experiment browser
+ more detailed detector visualization
+ saved event bookmarks
+ educational mode
+ model uncertainty visualization
```

---

# 56. V3 Feature Set

Possible long-term features:

```text
+ anomaly detection
+ event similarity search
+ learned embeddings
+ graph neural network
+ transformer model
+ semantic search over events
+ natural-language explanations
+ user accounts
+ collaborative collections
```

The project should never become so feature-heavy that the core event experience gets buried.

---

# 57. LLM Integration: Later, Not First

An LLM can eventually provide:

```text
“Explain this event like I'm new to particle physics.”
```

or:

```text
“Why did the model classify this as signal?”
```

The LLM should receive structured information produced by the actual system:

```text
event metadata
physics features
model prediction
model explanation
```

The LLM should not invent the event data.

Architecture:

```text
CERN data
   ↓
physics/ML pipeline
   ↓
structured result
   ↓
LLM explanation layer
```

The LLM is the narrator, not the source of truth.

---

# 58. Performance and Cost Philosophy

The first deployment should be cheap.

Do not pay for infrastructure simply because the architecture diagram looks impressive.

Start with:

- local preprocessing
- local model training
- free/low-cost deployment tiers
- one database
- one object store
- one API

Only pay for:

- GPU compute when model experiments actually require it
- storage when processed artifacts become large
- premium backend capacity when traffic requires it

The M-series Mac development machine is sufficient for the initial classical ML and modest neural-network work. Larger experiments can move to temporary cloud GPU sessions when necessary.

---

# 59. Cost-Aware Architecture

A sensible initial deployment may consist of:

```text
Frontend          Vercel
Database          Supabase Postgres
Object storage   Supabase Storage OR Vercel Blob
API               lightweight FastAPI deployment
ML training       local machine
Domain            optional paid domain
```

The application should be designed so the ML training machine is not part of the production runtime.

Production inference only needs the trained model artifact and preprocessing logic.

---

# 60. Data Storage Rule of Thumb

Separate storage by purpose:

### Raw/source data

Keep locally or use official source infrastructure where appropriate.

### Curated event artifacts

Store in object storage.

### Metadata

Store in Postgres.

### Model artifacts

Store in object storage with versioned references in Postgres/registry.

### Code

GitHub.

### Documentation

GitHub.

Do not store giant datasets in Postgres.

Supabase itself recommends storing large files outside the database in Storage while keeping file metadata separately. [Supabase Storage Quickstart](https://supabase.com/docs/guides/storage/quickstart)

---

# 61. Data Privacy

The base application does not need personal user data.

Avoid collecting:

- names
- emails
- precise location
- unnecessary device fingerprints

For anonymous analytics, collect only what helps improve the product.

---

# 62. Sharing / Deep Links

Every event should eventually be addressable like:

```text
/collision/1847291
```

A shared URL should open the event directly.

Query parameters can specify optional state:

```text
/collision/1847291?focus=muon-3
```

Do not encode massive event payloads into URLs.

---

# 63. Demo Script

A strong portfolio demo should be about 60–90 seconds.

### 0–8 seconds

Landing page.

Text:

```text
REAL PARTICLES.
REAL DATA.
REAL AI.
```

### 8–18 seconds

Open Explore.

Select an interesting event.

### 18–35 seconds

3D event loads.

Rotate detector.

Click particle.

Show its properties.

### 35–45 seconds

Click ANALYSE.

Show AI analysis animation.

### 45–55 seconds

Reveal model result.

### 55–70 seconds

Show scientific distribution/physics visualization.

### 70–85 seconds

Show data provenance and architecture briefly.

### 85–90 seconds

Logo:

```text
COLLIDER

Science you can explore.
```

---

# 64. Portfolio Case Study Structure

The final project page should explain:

## The problem

Particle physics data is powerful but difficult to understand.

## The idea

Make real events explorable and connect visualization to ML analysis.

## Data

Official CERN/ATLAS/CMS sources.

## Engineering

Data preprocessing, API, storage, WebGL, deployment.

## ML

Baseline → strong model → explanation.

## Performance

What was optimized and why.

## Result

Screenshots/video + measured model metrics.

## Lessons

What failed, what changed, what was learned.

---

# 65. What Would Make This Project Weak

Avoid these traps.

### Trap 1: Pretty 3D, no science

If it is only an animated detector, it is a frontend project.

### Trap 2: Generic AI wrapper

If Claude/GPT generates all of the “physics explanation” while your system has no real analysis, it is an AI wrapper.

### Trap 3: Fake physics

Do not invent scientific-looking values just to make the UI look good.

### Trap 4: Giant backend for no reason

Do not use Kubernetes because the README says “scalable architecture.”

### Trap 5: Too many models

One well-understood model is better than ten unexplained models.

### Trap 6: Premature optimization

Measure before switching formats or building complex rendering infrastructure.

### Trap 7: Copied cartoon IP

Use the genre's energy, not copyrighted character art or dialogue.

---

# 66. What Would Make This Project Excellent

A genuinely excellent version would have:

1. Real official-source data.
2. Clear dataset provenance.
3. A reproducible preprocessing pipeline.
4. A properly evaluated ML model.
5. Honest scientific language.
6. A visually distinctive 3D explorer.
7. Fast page loading.
8. Smooth GPU rendering.
9. Strong API boundaries.
10. Good versioning.
11. Clear failure states.
12. A case study showing engineering decisions.
13. A demo that is understandable in under 90 seconds.
14. A developer who can explain every major design choice without relying on Claude.

---

# 67. First Tasks to Give Claude Code

Do not start with “build everything.”

Use this sequence.

## Prompt 1: repository architecture

```text
Read COLLIDER_Project_Spec.md completely.
Do not write application code yet.

Create an implementation plan for the repository structure.
Identify the smallest useful Phase 0 and Phase 1.
List all assumptions that require validation against official CERN documentation.
Do not invent dataset details.
```

## Prompt 2: dataset research

```text
Using only official CERN/ATLAS/CMS documentation and the sources listed in the project spec, identify the best first educational ML dataset for COLLIDER.

Compare at least two viable options.
Explain:
- target label
- available features
- approximate scale
- analysis difficulty
- browser visualization suitability
- ML suitability
- licensing/citation requirements

Do not write the application yet.
```

## Prompt 3: data exploration

```text
Set up the Python data-exploration environment.
Create an EDA notebook and scripts.
Do not build the frontend yet.
The goal is to understand the dataset, labels, feature distributions, missing values, leakage risks, and class balance.
```

## Prompt 4: ML baseline

```text
Implement the baseline signal-vs-background classifier.

Requirements:
- reproducible split
- no leakage
- preprocessing pipeline
- baseline model
- ROC-AUC
- precision/recall
- confusion matrix
- saved artifact
- model metadata

Explain every major choice before implementation.
```

## Prompt 5: event schema

```text
Design a versioned event schema that is independent from the UI.
Show the mapping from source dataset fields to event objects.
Create sample fixture data only for development and clearly label it synthetic.
```

## Prompt 6: 3D prototype

```text
Build the simplest correct Three.js event display.

Requirements:
- one event
- camera orbit
- zoom
- particle tracks
- selectable objects
- no giant assets
- no unnecessary animation
- measure draw calls

Do not style it heavily yet.
```

## Prompt 7: final visual system

```text
Now implement the COLLIDER visual language from the project spec.
Use an original adult sci-fi cartoon laboratory aesthetic.
Do not use copyrighted character artwork, show screenshots, logos, or copied dialogue.
Keep scientific UI readable and the 3D rendering efficient.
```

---

# 68. Engineering Decision Log

Maintain a file:

```text
docs/decisions.md
```

Each decision:

```text
## ADR-001: Storage provider

Decision:
Supabase Storage for MVP.

Reason:
Postgres + object storage in one provider.

Alternatives:
Vercel Blob + separate Postgres.

Tradeoff:
Less provider flexibility, simpler MVP.
```

This makes the project much more professional.

---

# 69. Physics Integrity Checklist

Before publishing any scientific feature:

```text
[ ] Source identified
[ ] Dataset version recorded
[ ] Units verified
[ ] Formula checked
[ ] Missing values handled
[ ] No fabricated values
[ ] No leakage
[ ] Model metric verified
[ ] Explanation wording reviewed
[ ] Limitations stated
```

---

# 70. Final UX Principle

The website should produce this progression in the user's mind:

```text
“Whoa, this looks cool.”
           ↓
“What am I looking at?”
           ↓
“Oh, these are actual particle-event data.”
           ↓
“I can inspect the event.”
           ↓
“The model is analyzing it.”
           ↓
“I understand why it made that prediction.”
           ↓
“Holy shit, I just interacted with particle-physics data.”
```

That is the experience to optimize for.

---

# 71. The One-Sentence Product Definition

> **COLLIDER is an interactive CERN Open Data laboratory where users explore real particle-collision events in 3D, investigate the physics behind them, and use machine learning to identify and explain interesting event signatures.**

---

# 72. Recommended Final Tagline Options

Primary:

> **REAL PARTICLES. REAL DATA. REAL AI.**

Alternative:

> **SCIENCE YOU CAN EXPLORE.**

Alternative:

> **THE UNIVERSE LEFT THE DATA LYING AROUND. WE BUILT A UI FOR IT.**

Alternative:

> **SAME PARTICLES. A BRIGHTER YOU.**

Use the first as the main product tagline and keep the others for playful surfaces.

---

# 73. Official / Technical References

1. CERN Open Data Portal — datasets, software, documentation, visualisation resources:
   https://opendata.cern.ch/

2. ATLAS Open Data — access, tutorials, histogram analysis, Jupyter notebooks, Higgs/Z analyses, event visualization:
   https://atlas.cern/Resources/Opendata

3. CMS Open Data overview and documentation:
   https://opendata.cern.ch/docs/about-cms

4. Three.js InstancedMesh documentation:
   https://threejs.org/docs/pages/InstancedMesh.html

5. Supabase database documentation:
   https://supabase.com/docs/guides/database/overview

6. Supabase Storage documentation:
   https://supabase.com/docs/guides/storage

7. Supabase Storage quickstart:
   https://supabase.com/docs/guides/storage/quickstart

8. Vercel Blob:
   https://vercel.com/storage/blob

These should be re-checked before implementation because vendor features, plans, URLs, and product capabilities can change.

---

# 74. Final Build Order

The correct order is:

```text
1. Understand the dataset
         ↓
2. Build EDA
         ↓
3. Build physics feature pipeline
         ↓
4. Train baseline ML model
         ↓
5. Evaluate model honestly
         ↓
6. Create event schema
         ↓
7. Build event API
         ↓
8. Build basic 3D event viewer
         ↓
9. Connect prediction API
         ↓
10. Build full UI
         ↓
11. Apply cartoon-scifi art direction
         ↓
12. Optimize loading/rendering
         ↓
13. Deploy
         ↓
14. Measure real-world performance
         ↓
15. Document everything
```

Do not reverse this into:

```text
make cool UI
→ invent data
→ plug in AI
→ figure out science later
```

That produces a demo. The roadmap above produces a real project.

---

# 75. Definition of Done

COLLIDER V1 is done only when all of the following are true:

```text
DATA
[ ] Official source documented
[ ] Dataset version tracked
[ ] Preprocessing reproducible
[ ] Curated event manifest exists

ML
[ ] Baseline established
[ ] Model evaluated
[ ] Metrics documented
[ ] Model artifact versioned
[ ] Inference works through API

BACKEND
[ ] Event endpoint works
[ ] Prediction endpoint works
[ ] Database schema documented
[ ] Object storage integrated
[ ] Secrets protected

FRONTEND
[ ] Explore page works
[ ] Event page works
[ ] 3D viewer works
[ ] Particle selection works
[ ] Analysis state works
[ ] Prediction state works
[ ] Provenance is visible

3D/PERFORMANCE
[ ] Large dataset is never sent to browser
[ ] 3D engine loads lazily
[ ] Draw calls measured
[ ] Event payloads compressed
[ ] CDN/storage caching configured
[ ] Reduced-motion mode works

DESIGN
[ ] Original cartoon-scifi visual identity
[ ] No copyrighted show assets
[ ] Scientific UI remains readable
[ ] Mobile fallback exists

DOCUMENTATION
[ ] README
[ ] Architecture
[ ] ML methodology
[ ] Data lineage
[ ] Performance report
[ ] Demo video
```

---

# 76. Final Principle

COLLIDER should sit at the intersection of three things:

```text
                 SCIENCE
                   ▲
                   │
                   │
                   │
        ENGINEERING ┼ PRODUCT DESIGN
```

If one corner disappears, the project becomes weaker.

Science without product design becomes difficult to approach.

Product design without science becomes a visual demo.

Engineering without both becomes infrastructure nobody cares about.

The strongest version is a project where the visual experience gets someone to click, the science makes them stay, and the engineering makes the whole thing feel effortless.

---

# Appendix A — Minimal MVP Architecture

```text
               CERN Open Data
                     │
                     ▼
              Local Python ETL
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     Curated events         ML dataset
          │                     │
          ▼                     ▼
     Object storage       scikit-learn/XGBoost
          │                     │
          │                  model.pkl
          │                     │
          └──────────┬──────────┘
                     ▼
                  FastAPI
                     │
                Next.js app
                     │
            ┌────────┴────────┐
            ▼                 ▼
        HTML/CSS           Three.js
                              │
                             GPU
```

This is enough to build a compelling first release.

---

# Appendix B — Ideal Long-Term Architecture

```text
                         CERN
                          │
                    Open Data Sources
                          │
                          ▼
                Reproducible Data Pipeline
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
       Events          Features        Physics data
          │               │                │
          │               ▼                │
          │          Model Training        │
          │          ┌────┼────┐           │
          │          ▼    ▼    ▼           │
          │        Trees  MLP  GNN         │
          │          │    │    │           │
          │          └────┼────┘           │
          │               ▼                │
          │          Model Registry        │
          │               │                │
          └───────┬───────┴────────────────┘
                  ▼
             API / Inference
                  │
       ┌──────────┴───────────┐
       │                      │
       ▼                      ▼
  Metadata DB            Object storage
       │                      │
       └──────────┬───────────┘
                  ▼
              Next.js
                  │
       ┌──────────┼───────────┐
       │          │           │
       ▼          ▼           ▼
   Explore     Analyse     Explain
                  │
                  ▼
              Three.js
                  │
                  ▼
              WebGL/GPU
```

---

# Appendix C — What the User Should Be Able to Say in an Interview

A successful project should make it possible to answer these questions clearly:

### “What did you build?”

“I built an interactive particle-event explorer using CERN Open Data, a versioned ML pipeline, an inference API, and a GPU-accelerated 3D event visualization.”

### “What was the ML problem?”

“It was a defined signal-vs-background classification problem from an official educational dataset. I built a reproducible baseline, compared stronger models, and exposed the trained model through an inference service.”

### “How did you make the 3D experience fast?”

“I kept the raw datasets off the client, loaded only the selected event, lazy-loaded the 3D bundle, used GPU-friendly geometry and instancing where appropriate, compressed event payloads, and profiled draw calls/frame time.”

### “Where does the data live?”

“Structured event metadata lives in Postgres. Processed event artifacts and model files live in object storage. Raw CERN datasets are handled separately in the preprocessing pipeline.”

### “Why not just send the whole CERN dataset to the frontend?”

“Because that would be a bad architecture. The browser only needs a small event representation for the current view.”

### “Why use an LLM?”

“The LLM is optional and sits on top of structured scientific results. It explains the event; it does not invent the physics or replace the actual ML pipeline.”

### “How did AI help you build it?”

“I used Claude Code for implementation, debugging, tests, refactoring, and iteration, but I kept the dataset understanding, ML decisions, scientific validation, and architecture decisions explicit and reproducible.”

That is the standard this project should meet.
