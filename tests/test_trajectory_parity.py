"""The TypeScript trajectory port must match the Python reference exactly.

`web/lib/trajectory.ts` reimplements `collider.physics.trajectory` so the
browser can recompute geometry when the user changes the curvature scale,
without a round trip for arithmetic this cheap.

Two implementations of the same physics will drift. Python is the reference --
it is the one tested against known values -- and this test runs the TypeScript
through node and compares the output numerically. A port that silently
diverges is worse than no port, because the displayed geometry would stop
matching the documented physics while both look fine in isolation.
"""

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from collider.physics.trajectory import helix_points, helix_radius

ROOT = Path(__file__).resolve().parents[1]
TS_SOURCE = ROOT / "web" / "lib" / "trajectory.ts"

# (pt, eta, phi, charge) spanning stiff and soft tracks, both charges, forward
# and central, plus a neutral object.
CASES = [
    (45.0, 0.0, 0.0, -1),
    (45.0, 0.0, 0.0, 1),
    (10.0, 1.2, 2.1, -1),
    (90.0, -0.8, -1.4, 1),
    (1.0, 0.0, 0.5, -1),
    (25.0, 2.4, 3.0, 1),
    (50.0, 0.3, 1.0, 0),
]
SCALES = [1.0, 40.0]


def _node() -> str:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    return node


@pytest.fixture(scope="module")
def ts_results(tmp_path_factory) -> dict:
    """Run the actual TypeScript module through node and collect its output.

    Node 22+ strips TypeScript types natively, so the real source file is
    imported and executed rather than a transformed copy. Testing a
    transformation of the source would leave open the possibility that the
    transformation, not the code, is what passes.
    """
    if not TS_SOURCE.exists():
        pytest.skip("frontend not present")

    node = _node()
    work = tmp_path_factory.mktemp("traj")
    script = work / "run.ts"
    script.write_text(
        f"import {{ helixPoints, helixRadius }} from {str(TS_SOURCE)!r};\n"
        f"const cases = {json.dumps(CASES)};\n"
        f"const scales = {json.dumps(SCALES)};\n"
        "const out = [];\n"
        "for (const [pt, eta, phi, charge] of cases) {\n"
        "  for (const scale of scales) {\n"
        "    out.push({ pt, eta, phi, charge, scale,\n"
        "      radius: helixRadius(pt, charge),\n"
        "      points: Array.from(helixPoints({ pt, eta, phi, charge },\n"
        "        { nPoints: 32, curvatureScale: scale })) });\n"
        "  }\n}\n"
        "console.log(JSON.stringify(out));\n"
    )
    proc = subprocess.run(
        [node, "--experimental-strip-types", str(script)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.fail(f"node failed: {proc.stderr[:600]}")
    return {
        (r["pt"], r["eta"], r["phi"], r["charge"], r["scale"]): r for r in json.loads(proc.stdout)
    }


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("scale", SCALES)
def test_points_match_the_python_reference(ts_results, case, scale):
    pt, eta, phi, charge = case
    ts = ts_results[(pt, eta, phi, charge, scale)]

    expected = helix_points(pt, eta, phi, charge, n_points=32, curvature_scale=scale)
    actual = np.asarray(ts["points"], dtype=np.float64).reshape(-1, 3)

    assert actual.shape == expected.shape
    # float32 storage on the TS side sets the tolerance floor.
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-6)


@pytest.mark.parametrize("case", CASES)
def test_radius_matches_the_python_reference(ts_results, case):
    pt, eta, phi, charge = case
    ts = ts_results[(pt, eta, phi, charge, SCALES[0])]
    expected = float(helix_radius(pt, charge))

    if np.isinf(expected):
        assert ts["radius"] is None or ts["radius"] > 1e30
    else:
        assert ts["radius"] == pytest.approx(expected, rel=1e-9)
