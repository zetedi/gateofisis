"""Reproduce the user-guided roof-rim correction and conservative sky selection.

Requires the meshes/caches from register_roof_geometry.py. Run this with the
reconstruction Python environment, then export_aligned_roof.py inside Blender.
Only derived reports and local work files are written.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from register_scans import obj_data

BASE = Path(__file__).resolve().parents[1]
initial = np.array(json.loads((BASE / 'reports/roof-registration.json').read_text())['candidate']['matrix'])
vertices, faces, *_ = obj_data('upper-stairs')
unique, inverse = np.unique(np.round(vertices, 5), axis=0, return_inverse=True)
welded = inverse[faces]
edges = np.sort(np.concatenate([welded[:, [0, 1]], welded[:, [1, 2]], welded[:, [2, 0]]]), axis=1)
unique_edges, counts = np.unique(edges, axis=0, return_counts=True)
boundary = unique[np.unique(unique_edges[counts == 1])]
boundary = boundary[boundary[:, 2] > .05]  # Exclude the detached capture fragment.
world = boundary @ initial[:3, :3].T + initial[:3, 3]
target = np.load(BASE / 'work/roof-target.npz')
points = target['points']
points = points[points[:, 2] < 2.7]
neighbors = cKDTree(points[:, :2]).query_ball_point(world[:, :2], .025)
comparisons = []
for index, ids in enumerate(neighbors):
    if len(ids) > 8:
        height = np.quantile(points[ids, 2], .95)
        comparisons.append([*world[index], height, height - world[index, 2]])
comparison = np.array(comparisons)
pivot = np.array([.53, -2.38, 2.52])
relative = comparison[:, :3] - pivot
fit = least_squares(lambda p: relative[:, :2] @ p[:2] + p[2] - comparison[:, 4],
                    np.zeros(3), loss='soft_l1', f_scale=.012)
slope_x, slope_y, rise = fit.x
angles = [np.arctan(slope_y), -np.arctan(slope_x), 0]
rotation = Rotation.from_euler('xyz', angles).as_matrix()
correction = np.eye(4)
correction[:3, :3] = rotation
correction[:3, 3] = pivot - rotation @ pivot + [0, 0, rise]
corrected_boundary = comparison[:, :3] @ rotation.T + correction[:3, 3]
report = {
    'status': 'User-guided visual alignment to the upper rim',
    'date': '2026-10-06',
    'method': 'Matching stone joint retains the existing horizontal correspondence. Robust upper-rim fit supplies a rigid height and tilt correction; no scaling or mesh deformation.',
    'pivot': pivot.tolist(),
    'heightChange': float(rise),
    'rotationDegrees': np.rad2deg(angles).tolist(),
    'correctionMatrix': correction.tolist(),
    'combinedRegistrationMatrix': (correction @ initial).tolist(),
    'boundaryComparisonPoints': len(comparison),
    'boundaryMedianAbsoluteHeightDifferenceBefore': float(np.median(np.abs(comparison[:, 4]))),
    'boundaryMedianAbsoluteHeightDifferenceAfter': float(np.median(np.abs(comparison[:, 3] - corrected_boundary[:, 2]))),
    'units': 'Relative reconstruction units. Visual alignment, not independently measured survey accuracy.',
}

# Test the central ceiling overlap separately from the boundary fit.
source = np.load(BASE / 'work/roof-source.npz')
selection = (source['points'][:, 2] > .05) & (source['normals'][:, 2] > .5)
roof = source['points'][selection] @ initial[:3, :3].T + initial[:3, 3]
corrected_roof = roof @ rotation.T + correction[:3, 3]
ceiling = target['points']
normals = target['normals']
selection = ((ceiling[:, 0] > .15) & (ceiling[:, 0] < .90) & (ceiling[:, 1] > -2.65)
             & (ceiling[:, 1] < -2.10) & (ceiling[:, 2] < 2.7) & (normals[:, 2] < -.7))
ceiling = ceiling[selection]
report['sampledCeilingClearance'] = {}
for label, surface in [('before', roof), ('after', corrected_roof)]:
    distance, indices = cKDTree(surface[:, :2]).query(ceiling[:, :2])
    overlapping = distance < .012
    clearance = surface[indices[overlapping], 2] - ceiling[overlapping, 2]
    report['sampledCeilingClearance'][label] = {
        'samples': len(clearance),
        'roofAboveCeilingFraction': float((clearance >= 0).mean()),
        'minimum': float(clearance.min()),
        'median': float(np.median(clearance)),
    }
report['sampledCeilingClearance']['method'] = 'Nearest XY roof-face-center height at sampled downward-facing central ceiling faces; a local overlap check, not a complete solid-intersection proof.'

# Identify blue sky fragments at the seam from original texture pixels.
raw = np.load(BASE / 'work/raw-mesh-0.npz')
v = raw['vertices']
f = raw['faces']
centers = v[f].mean(1)
roi = ((centers[:, 0] > -.2) & (centers[:, 0] < 1.25) & (centers[:, 1] > -2.9)
       & (centers[:, 1] < -1.9) & (centers[:, 2] > 2.35) & (centers[:, 2] < 2.7))
ids = np.flatnonzero(roi)
uv = raw['uv'][ids].mean(1)
materials = raw['materials'][ids]
textures = json.loads((BASE / 'reports/raw-mesh.json').read_text())[0]['textures']
colors = np.zeros((len(ids), 3))
for material in np.unique(materials):
    pixels = np.asarray(Image.open(textures[int(material)]['image']).convert('RGB'))
    height, width = pixels.shape[:2]
    selected = materials == material
    coordinates = uv[selected]
    xx = np.clip((coordinates[:, 0] * width).astype(int), 0, width - 1)
    yy = np.clip(((1 - coordinates[:, 1]) * height).astype(int), 0, height - 1)
    colors[selected] = pixels[yy, xx] / 255
sky = ((colors[:, 2] - colors[:, 0] > .025) & (colors[:, 1] - colors[:, 0] > .01)
       & (colors[:, 2] > colors[:, 1] * .985) & (colors[:, 2] > .25))
labels = np.load(BASE / 'work/raw-components.npy')
keep = ((labels[f[:, 0]] == np.bincount(labels).argmax()) & (centers[:, 1] <= 2.7)
        & ~((centers[:, 1] > 2.15) & (centers[:, 2] > 1.10)))
raw_ids = ids[sky & keep[ids]]
clean_ids = (np.cumsum(keep) - 1)[raw_ids]
np.savez(BASE / 'work/roof-sky-faces.npz', cleanFaceIds=clean_ids, rawFaceIds=raw_ids)
report['seamCleanup'] = {
    'skyColoredTriangles': len(clean_ids),
    'handling': 'Visually inspected in magenta diagnostic renders. Isolated in a hidden collection in the aligned derivative; original vertex coordinates and UVs retained.',
    'stoneGeometry': 'No invented surfaces, smoothing, welding or hole filling.',
}
report['artifacts'] = {
    'blender': 'output/Gate-of-Isis-Roof-Aligned.blend',
    'earlierStudyPreserved': 'output/Gate-of-Isis-Roof-Study.blend',
    'renders': [f'reports/roof-aligned-{name}.png' for name in ['end', 'opposite-end', 'reverse', 'front', 'above']],
}
(BASE / 'reports/roof-rim-alignment.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: report[k] for k in ['heightChange', 'rotationDegrees', 'boundaryMedianAbsoluteHeightDifferenceAfter', 'sampledCeilingClearance', 'seamCleanup']}, indent=2))
