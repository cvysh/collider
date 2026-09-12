"""Export curated event artifacts for the web application.

Usage:
    python scripts/export_events.py

Writes data/processed/events/v1/<event_id>.json.gz plus an index.json
summary list.

Curation
--------
Real 4-lepton data is not usable for display: only 1 of 3,708 events survives
selection, the rest being fake leptons (docs/FINDINGS.md #4). But the 2muons
data is genuine, clean and validated -- it reproduces the Z, J/psi and Upsilon
at their known masses. So:

* **measured**   real Z->mumu candidates from 2015 collision data
* **simulated**  ggH->ZZ->4l signal and ZZ->4l background

Each is badged with ``data_kind`` and the browser is never left guessing.

Artifacts are immutable and versioned by path (SPEC section 21.4). Changing an
event means writing v2, never overwriting v1.
"""

import gzip
import json
import subprocess
from pathlib import Path

import awkward as ak
import numpy as np
import uproot
import xgboost as xgb
from xgboost import XGBClassifier

from collider.api.schema import (
    SCHEMA_VERSION,
    EventPayload,
    EventSummary,
    FeatureContribution,
    MissingEnergy,
    Prediction,
    Provenance,
    ReconstructedObject,
)
from collider.data.atlas import PDG_MUON, load_leptons, select_dilepton
from collider.features.fourlepton import FEATURE_NAMES, READ_BRANCHES, build_features
from collider.ml.registry import load_registry
from collider.physics.fourvector import invariant_mass, to_cartesian
from collider.physics.selection import PAIRINGS, pair_into_z_candidates, select_four_lepton

OUTPUT = Path("data/processed/events/v1")
RAW = Path("data/raw")
N_PER_CATEGORY = 40
REGISTRY_PATH = Path("ml/models/registry.json")

#: The trained model consumes four-lepton features. A two-muon Z candidate has
#: no second lepton pair, so m_z2 and the third and fourth lepton momenta do
#: not exist for it. The model cannot score these events, and inventing inputs
#: to make it possible would be fabrication.
NO_SCORE_REASON = (
    "This model scores four-lepton events. This is a two-muon event, which has "
    "no second lepton pair, so the required features do not exist for it."
)
SEED = 20260912

PDG_TO_TYPE = {11: "electron", 13: "muon"}

SOURCES = {
    "measured": {
        "path": RAW / "ODEO_FEB2025_v0_2muons_data15_periodD.2muons.root",
        "record": "https://opendata.cern.ch/record/93921",
        "doi": "10.7483/OPENDATA.ATLAS.6VGH.HN41",
        "dataset": "ATLAS 13 TeV 2015+2016 education, 2muons skim, collision data",
    },
    "signal": {
        "path": RAW
        / "4lep"
        / (
            "ODEO_FEB2025_v0_4lep_mc_345060."
            "PowhegPythia8EvtGen_NNLOPS_nnlo_30_ggH125_ZZ4l.4lep.root"
        ),
        "record": "https://opendata.cern.ch/record/93932",
        "doi": "10.7483/OPENDATA.ATLAS.IPG4.6M6X",
        "dataset": "ATLAS 13 TeV 2015+2016 education, 4lep skim, MC simulation",
        "process": "ggH125_ZZ4l",
    },
    "background": {
        "path": RAW / "4lep" / "ODEO_FEB2025_v0_4lep_mc_700600.Sh_2212_llll.4lep.root",
        "record": "https://opendata.cern.ch/record/93932",
        "doi": "10.7483/OPENDATA.ATLAS.IPG4.6M6X",
        "dataset": "ATLAS 13 TeV 2015+2016 education, 4lep skim, MC simulation",
        "process": "Sh_2212_llll",
    },
}


def pipeline_version() -> str:
    """Git commit of the code that produced these artifacts (SPEC section 12.1)."""
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def provenance_for(key: str) -> Provenance:
    src = SOURCES[key]
    return Provenance(
        dataset=src["dataset"],
        record_url=src["record"],
        doi=src["doi"],
        source_file=src["path"].name,
        pipeline_version=pipeline_version(),
        accessed="2026-09-12",
    )


def make_objects(pt, eta, phi, energy, charge, ltype) -> list[ReconstructedObject]:
    px, py, pz = to_cartesian(pt, eta, phi)
    return [
        ReconstructedObject(
            id=i,
            type=PDG_TO_TYPE[int(ltype[i])],
            charge=int(charge[i]),
            pt=round(float(pt[i]), 4),
            eta=round(float(eta[i]), 4),
            phi=round(float(phi[i]), 4),
            energy=round(float(energy[i]), 4),
            px=round(float(px[i]), 4),
            py=round(float(py[i]), 4),
            pz=round(float(pz[i]), 4),
        )
        for i in range(len(pt))
    ]


def export_dimuon(rng) -> list[EventPayload]:
    """Real Z->mumu candidates, restricted to the Z peak so the display is honest."""
    src = SOURCES["measured"]
    mu = select_dilepton(load_leptons(src["path"]))
    mass = ak.to_numpy(invariant_mass(mu["pt"], mu["eta"], mu["phi"], mu["energy"]))

    near_z = np.flatnonzero(np.abs(mass - 91.188) < 5.0)
    chosen = rng.choice(near_z, size=min(N_PER_CATEGORY, len(near_z)), replace=False)

    pt = ak.to_numpy(mu["pt"])
    eta = ak.to_numpy(mu["eta"])
    phi = ak.to_numpy(mu["phi"])
    en = ak.to_numpy(mu["energy"])
    q = ak.to_numpy(mu["charge"])

    out = []
    for i in chosen:
        out.append(
            EventPayload(
                event_id=f"data-zmumu-{i}",
                data_kind="measured",
                objects=make_objects(pt[i], eta[i], phi[i], en[i], q[i], np.full(2, PDG_MUON)),
                derived={"m_mumu": round(float(mass[i]), 3)},
                prediction_unavailable_reason=NO_SCORE_REASON,
                provenance=provenance_for("measured"),
            )
        )
    return out


#: How many contributions to carry. Enough to explain, few enough to read.
N_CONTRIBUTIONS = 6


def _top_contributions(row, values, names) -> list[FeatureContribution]:
    """Largest absolute SHAP contributions for one event, biggest first.

    The final column of an XGBoost contribution row is the bias term, not a
    feature, so it is dropped.
    """
    if row is None or not np.isfinite(row).all():
        return []
    shap = row[:-1]
    order = np.argsort(-np.abs(shap))[:N_CONTRIBUTIONS]
    return [
        FeatureContribution(
            feature=names[j],
            value=round(float(values[j]), 4),
            contribution=round(float(shap[j]), 4),
        )
        for j in order
    ]


def load_model():
    """Load the registered model, or None if it has not been trained yet."""
    if not REGISTRY_PATH.exists():
        return None, None
    registry = load_registry(REGISTRY_PATH)
    entry = next(iter(registry.values()))
    entry.verify_features(list(FEATURE_NAMES))  # fails loudly on any mismatch
    booster = XGBClassifier()
    booster.load_model(REGISTRY_PATH.parent / entry.artifact)
    return booster, entry


def export_fourlepton(key: str, label: str, rng, model, entry) -> list[EventPayload]:
    """Simulated four-lepton events, signal or background."""
    src = SOURCES[key]
    with uproot.open(f"{src['path']}:analysis") as tree:
        ev = tree.arrays([*READ_BRANCHES, "mcWeight", "runNumber", "eventNumber"])

    ev = ev[select_four_lepton(ev)]
    order = ak.argsort(ev.lep_pt, axis=1, ascending=False)
    pt = ak.to_numpy(ev.lep_pt[order]).astype(np.float64)
    eta = ak.to_numpy(ev.lep_eta[order]).astype(np.float64)
    phi = ak.to_numpy(ev.lep_phi[order]).astype(np.float64)
    en = ak.to_numpy(ev.lep_e[order]).astype(np.float64)
    q = ak.to_numpy(ev.lep_charge[order]).astype(np.int64)
    lt = ak.to_numpy(ev.lep_type[order]).astype(np.int64)

    px, py, pz = to_cartesian(pt, eta, phi)
    m2 = en.sum(1) ** 2 - (px.sum(1) ** 2 + py.sum(1) ** 2 + pz.sum(1) ** 2)
    m4l = np.sqrt(np.maximum(m2, 0.0))

    def pair_mass(ia, ib):
        ex, ey = px[:, ia] + px[:, ib], py[:, ia] + py[:, ib]
        ez, et = pz[:, ia] + pz[:, ib], en[:, ia] + en[:, ib]
        return np.sqrt(np.maximum(et**2 - (ex**2 + ey**2 + ez**2), 0.0))

    pm = np.stack(
        [np.stack([pair_mass(*p) for p in pairing], axis=1) for pairing in PAIRINGS], axis=1
    )
    mz1, mz2, valid = pair_into_z_candidates(lt, q, pm)

    pool = np.flatnonzero(valid)
    chosen = rng.choice(pool, size=min(N_PER_CATEGORY, len(pool)), replace=False)

    # Score every selected event once. Predictions are deterministic for a
    # fixed (event, model, feature-set), so precomputing them keeps the live
    # path a lookup rather than an inference call (ADR-0002).
    scores = None
    contribs = None
    if model is not None:
        built = build_features(ev)
        scores = np.full(len(pt), np.nan)
        scores[built["source_index"]] = model.predict_proba(built["features"])[:, 1]

        # SHAP contributions straight from the booster: additive log-odds
        # shifts per feature, plus a bias term in the final column. These are
        # per-event, unlike the global permutation importance in
        # ml/models/comparison.json.
        raw = model.get_booster().predict(xgb.DMatrix(built["features"]), pred_contribs=True)
        contribs = np.full((len(pt), raw.shape[1]), np.nan)
        contribs[built["source_index"]] = raw
        feature_values = np.full((len(pt), built["features"].shape[1]), np.nan)
        feature_values[built["source_index"]] = built["features"]

    met = ak.to_numpy(ev.met).astype(np.float64)
    met_phi = ak.to_numpy(ev.met_phi).astype(np.float64) if "met_phi" in ev.fields else None
    mcw = ak.to_numpy(ev.mcWeight).astype(np.float64)
    run = ak.to_numpy(ev.runNumber).astype(np.int64)
    evt = ak.to_numpy(ev.eventNumber).astype(np.int64)

    out = []
    for i in chosen:
        prediction = None
        reason = None
        if scores is not None and np.isfinite(scores[i]):
            score = float(scores[i])
            prediction = Prediction(
                model_id=entry.model_id,
                task=entry.task,
                score=round(score, 6),
                threshold=entry.threshold,
                classification=("signal-like" if score >= entry.threshold else "background-like"),
                feature_set_version=entry.feature_set_version,
                contributions=_top_contributions(contribs[i], feature_values[i], entry.features),
            )
        else:
            reason = "Model artifact unavailable at export time."
        out.append(
            EventPayload(
                event_id=f"mc-{label}-{i}",
                data_kind="simulated",
                mc_process=src["process"],
                truth_label="signal" if label == "signal" else "background",
                mc_weight=float(mcw[i]),
                run_number=int(run[i]),
                event_number=int(evt[i]),
                objects=make_objects(pt[i], eta[i], phi[i], en[i], q[i], lt[i]),
                missing_energy=MissingEnergy(
                    magnitude=round(float(met[i]), 3),
                    phi=round(float(met_phi[i]), 4) if met_phi is not None else 0.0,
                ),
                derived={
                    "m_4l": round(float(m4l[i]), 3),
                    "m_z1": round(float(mz1[i]), 3),
                    "m_z2": round(float(mz2[i]), 3),
                },
                prediction=prediction,
                prediction_unavailable_reason=reason,
                provenance=provenance_for(key),
            )
        )
    return out


def summarise(ev: EventPayload) -> EventSummary:
    leptons = [o for o in ev.objects if o.type in ("muon", "electron")]
    if ev.data_kind == "measured":
        category = "Z→μμ candidate (real data)"
    elif ev.truth_label == "signal":
        category = "H→ZZ→4ℓ (simulated signal)"
    else:
        category = "ZZ→4ℓ (simulated background)"
    return EventSummary(
        event_id=ev.event_id,
        data_kind=ev.data_kind,
        category=category,
        n_objects=len(ev.objects),
        n_leptons=len(leptons),
        score=ev.prediction.score if ev.prediction else None,
        headline=ev.derived,
    )


def main() -> None:
    for key, src in SOURCES.items():
        if not src["path"].exists():
            raise SystemExit(f"missing {src['path']} for '{key}'; see data/raw/README.md")

    rng = np.random.default_rng(SEED)
    model, entry = load_model()
    if model is None:
        print("WARNING: no model registry; events will be exported unscored")
    events = (
        export_dimuon(rng)
        + export_fourlepton("signal", "signal", rng, model, entry)
        + export_fourlepton("background", "background", rng, model, entry)
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    sizes = []
    for ev in events:
        path = OUTPUT / f"{ev.event_id}.json.gz"
        raw = ev.model_dump_json(exclude_none=True).encode()
        with gzip.open(path, "wb", compresslevel=9) as f:
            f.write(raw)
        sizes.append((len(raw), path.stat().st_size))

    index = [summarise(e).model_dump(exclude_none=True) for e in events]
    index_path = OUTPUT.parent / "index.json"
    index_path.write_text(json.dumps({"schema_version": SCHEMA_VERSION, "events": index}, indent=1))

    raw_sizes = np.array([s[0] for s in sizes])
    gz_sizes = np.array([s[1] for s in sizes])
    print(f"wrote {len(events)} events to {OUTPUT}")
    for kind in ("measured", "simulated"):
        n = sum(1 for e in events if e.data_kind == kind)
        print(f"  {kind:10s} {n}")
    print(
        f"\npayload size  raw  median {np.median(raw_sizes):6.0f} B  max {raw_sizes.max():6.0f} B"
    )
    print(f"              gzip median {np.median(gz_sizes):6.0f} B  max {gz_sizes.max():6.0f} B")
    print(f"index: {index_path} ({index_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
