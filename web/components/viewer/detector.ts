/**
 * Schematic ATLAS detector geometry.
 *
 * Radii and half-lengths are the published approximate dimensions of the real
 * subsystems, in metres. They are drawn schematically -- SPEC section 19.2 is
 * explicit that this is a stylised event display, not a CAD model -- but the
 * proportions are not invented, because a detector drawn to made-up dimensions
 * teaches the wrong thing about where particles stop.
 *
 * Dimensions are rounded from the ATLAS technical design reports; the real
 * subsystems have segmentation this does not attempt to reproduce.
 */

export interface Subsystem {
  id: string;
  label: string;
  /** Inner and outer barrel radius, metres. */
  r: [number, number];
  /** Barrel half-length along the beam, metres. */
  halfZ: number;
  colour: number;
  opacity: number;
  note: string;
}

export const SUBSYSTEMS: Subsystem[] = [
  {
    id: "pixel",
    label: "Pixel",
    r: [0.033, 0.123],
    halfZ: 0.4,
    colour: 0x8fe04a,
    opacity: 0.9,
    note: "Silicon pixels. Finds the collision point.",
  },
  {
    id: "sct",
    label: "SCT",
    r: [0.299, 0.514],
    halfZ: 0.75,
    colour: 0x6fc23c,
    opacity: 0.55,
    note: "Silicon strips. Measures track curvature.",
  },
  {
    id: "trt",
    label: "TRT",
    r: [0.554, 1.082],
    halfZ: 0.78,
    colour: 0x3fd4ef,
    opacity: 0.38,
    note: "Straw tubes. Extends the track and helps identify electrons.",
  },
  {
    id: "solenoid",
    label: "Solenoid",
    r: [1.2, 1.3],
    halfZ: 2.65,
    colour: 0xf0b429,
    opacity: 0.2,
    note: "2 T superconducting magnet. This is what bends the tracks.",
  },
  {
    id: "ecal",
    label: "EM calorimeter",
    r: [1.5, 2.0],
    halfZ: 3.2,
    colour: 0x3fd4ef,
    opacity: 0.1,
    note: "Liquid argon. Electrons and photons stop here.",
  },
  {
    id: "hcal",
    label: "Hadronic calorimeter",
    r: [2.28, 4.25],
    halfZ: 6.1,
    colour: 0x8b6bc4,
    opacity: 0.055,
    note: "Steel and scintillator. Jets stop here.",
  },
  {
    id: "muon",
    label: "Muon spectrometer",
    r: [5.0, 10.0],
    halfZ: 11.0,
    colour: 0xef5b4c,
    opacity: 0.03,
    note: "Drift tubes in a toroidal field. Only muons reach this far.",
  },
];

/**
 * Where each particle type stops, in metres.
 *
 * Real physics rather than styling: electrons and photons deposit their energy
 * in the electromagnetic calorimeter, hadronic jets penetrate to the hadronic
 * calorimeter, and muons pass through everything -- which is exactly why the
 * outermost subsystem is called the muon spectrometer.
 */
export const STOPPING_RADIUS: Record<string, number> = {
  electron: 2.0,
  photon: 2.0,
  jet: 4.25,
  muon: 7.5,
};

/**
 * Radius beyond which the helix model stops being valid.
 *
 * The helix assumes the uniform 2 T solenoidal field, which ends at the
 * solenoid. Outside it the field is the toroid, whose geometry we do not model.
 * Track segments drawn beyond this are straight extrapolations along the exit
 * direction, and the viewer legend says so.
 */
export const SOLENOID_OUTER_M = 1.3;

/** Standard viewing angles used in real event displays. */
export interface CameraPreset {
  id: string;
  label: string;
  theta: number;
  phi: number;
  distance: number;
  hint: string;
}

export const CAMERA_PRESETS: CameraPreset[] = [
  {
    id: "iso",
    label: "3D",
    theta: Math.PI / 4,
    phi: Math.PI / 3,
    distance: 5.2,
    hint: "Perspective view",
  },
  {
    id: "xy",
    label: "x-y",
    // Looking down the beam. Not exactly zero, which is a degenerate camera.
    theta: Math.PI / 2,
    phi: 0.001,
    distance: 4.6,
    hint: "Down the beam. Shows azimuth and curvature.",
  },
  {
    id: "rz",
    label: "r-z",
    theta: 0,
    phi: Math.PI / 2,
    distance: 6.5,
    hint: "Side on. Shows how far forward tracks go.",
  },
];
