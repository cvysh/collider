/**
 * Helical trajectories in the ATLAS solenoidal field.
 *
 * A direct port of `collider/physics/trajectory.py`. The Python version is the
 * reference implementation and is tested against known values; this port is
 * checked against it by `tests/test_trajectory_parity.py`, so the two cannot
 * drift.
 *
 * Why a port rather than sending points from the server: the geometry depends
 * on the curvature scale, which the user can change interactively. Round
 * tripping to the API on every toggle would be absurd for arithmetic this
 * cheap.
 *
 * The important physical fact, which is not what most event displays suggest:
 * at 10-90 GeV these tracks are nearly straight. A 45 GeV muon deviates about
 * 8 mm across the 1.1 m inner detector. That is precisely why curvature
 * measures momentum -- less bend means a stiffer track.
 */

/** ATLAS central solenoid, tesla. */
export const SOLENOID_TESLA = 2.0;

/** Outer radius of the inner detector, metres. Beyond it the field is the
 *  toroid and this model no longer applies. */
export const INNER_DETECTOR_RADIUS_M = 1.1;

/** c in the GeV / metre / tesla unit system. */
const C_FACTOR = 0.299792458;

export interface TrackInput {
  pt: number;
  eta: number;
  phi: number;
  charge: number | null | undefined;
}

/** Radius of curvature in metres. `Infinity` for neutral particles. */
export function helixRadius(
  pt: number,
  charge: number,
  field = SOLENOID_TESLA,
): number {
  const q = Math.abs(charge);
  if (q === 0) return Infinity;
  return pt / (C_FACTOR * q * field);
}

/**
 * Sample a trajectory from the interaction point.
 *
 * @param curvatureScale 1 is the true trajectory. Larger values exaggerate the
 *   bend and must be labelled as a visual aid wherever shown.
 * @returns Flat `[x,y,z, x,y,z, ...]` in metres, ready for a BufferAttribute.
 */
export function helixPoints(
  { pt, eta, phi, charge }: TrackInput,
  {
    maxRadius = INNER_DETECTOR_RADIUS_M,
    nPoints = 48,
    field = SOLENOID_TESLA,
    curvatureScale = 1,
  } = {},
): Float32Array {
  const out = new Float32Array(nPoints * 3);
  const slope = Math.sinh(eta); // pz/pt, same relation as to_cartesian()
  const q = charge ?? 0;
  const radius = helixRadius(pt, q, field);

  // Neutral, or so stiff that the helix is numerically a straight line.
  if (!Number.isFinite(radius)) {
    for (let i = 0; i < nPoints; i++) {
      const s = (maxRadius * i) / (nPoints - 1);
      out[i * 3] = s * Math.cos(phi);
      out[i * 3 + 1] = s * Math.sin(phi);
      out[i * 3 + 2] = s * slope;
    }
    return out;
  }

  const effectiveRadius = radius / Math.max(curvatureScale, 1e-9);
  const ratio = Math.min(Math.max(maxRadius / (2 * effectiveRadius), -1), 1);
  const maxAngle = 2 * Math.asin(ratio);
  const sign = Math.sign(q);

  for (let i = 0; i < nPoints; i++) {
    const a = (maxAngle * i) / (nPoints - 1);
    // In the frame where u runs along the initial momentum direction:
    //   u = r sin(a),  v = -q r (1 - cos a)
    const u = effectiveRadius * Math.sin(a);
    const v = -sign * effectiveRadius * (1 - Math.cos(a));
    out[i * 3] = u * Math.cos(phi) - v * Math.sin(phi);
    out[i * 3 + 1] = u * Math.sin(phi) + v * Math.cos(phi);
    out[i * 3 + 2] = effectiveRadius * a * slope;
  }
  return out;
}
