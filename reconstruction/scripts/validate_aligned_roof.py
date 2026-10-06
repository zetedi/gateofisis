"""Verify the aligned derivative preserves captured geometry, UVs and textures."""
import hashlib
import json
from pathlib import Path

import bpy
import numpy as np

BASE = Path(__file__).resolve().parents[1]

def digest_mesh(obj, selection=None):
    mesh = obj.data
    v = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get('co', v)
    v = v.reshape(-1, 3)
    f = np.empty(len(mesh.polygons) * 3, np.int32)
    mesh.polygons.foreach_get('vertices', f)
    f = f.reshape(-1, 3)
    uv = np.empty(len(mesh.loops) * 2, np.float32)
    mesh.uv_layers.active.data.foreach_get('uv', uv)
    uv = uv.reshape(-1, 3, 2)
    materials = np.empty(len(mesh.polygons), np.int32)
    mesh.polygons.foreach_get('material_index', materials)
    digest = hashlib.sha256()
    for begin in range(0, len(f), 100000):
        end = min(begin + 100000, len(f))
        keep = np.ones(end - begin, bool) if selection is None else selection[begin:end]
        digest.update(v[f[begin:end][keep]].tobytes())
    digest.update((uv if selection is None else uv[selection]).tobytes())
    digest.update((materials if selection is None else materials[selection]).tobytes())
    return digest.hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(BASE / 'output/Gate-of-Isis-Roof-Study.blend'))
roof = next(o for o in bpy.context.scene.objects if o.name.startswith('Roof ·'))
main = next(o for o in bpy.context.scene.objects if o.type == 'MESH' and o != roof)
sky_ids = np.load(BASE / 'work/roof-sky-faces.npz')['cleanFaceIds']
keep = np.ones(len(main.data.polygons), bool)
keep[sky_ids] = False
expected_main = digest_mesh(main, keep)
expected_roof = digest_mesh(roof)
original_roof_matrix = np.array(roof.matrix_world)
original_main_matrix = np.array(main.matrix_world)

bpy.ops.wm.open_mainfile(filepath=str(BASE / 'output/Gate-of-Isis-Roof-Aligned.blend'))
scene = bpy.context.scene
roof = scene.objects['Roof · aligned to the gate rim']
main = next(o for o in scene.objects if o.type == 'MESH' and o.name.startswith('Gate, approach'))
assert digest_mesh(main) == expected_main, 'Retained captured surfaces changed'
assert digest_mesh(roof) == expected_roof, 'Roof geometry or UVs changed'
assert np.array_equal(np.array(main.matrix_world), original_main_matrix)
correction = np.array(json.loads((BASE / 'reports/roof-rim-alignment.json').read_text())['correctionMatrix'])
assert np.allclose(np.array(roof.matrix_world), correction @ original_roof_matrix, atol=1e-6)
archive = bpy.data.collections['Capture artifacts · hidden, retained for reversibility']
assert archive.hide_render and archive.hide_viewport
assert sum(len(o.data.polygons) for o in archive.objects) == len(sky_ids)
assert len(main.data.polygons) + len(sky_ids) == 12699647
images = {n.image for obj in [main, roof] for mat in obj.data.materials if mat
          for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image}
assert all(image.packed_file or image.packed_files for image in images)
report = {
    'retainedMainTriangles': len(main.data.polygons),
    'roofTriangles': len(roof.data.polygons),
    'hiddenSkyTriangles': len(sky_ids),
    'retainedMainCoordinatesUvsAndMaterialsIdentical': True,
    'roofCoordinatesUvsAndMaterialsIdentical': True,
    'mainTransformUnchanged': True,
    'roofTransformMatchesCorrection': True,
    'allUsedTexturesPacked': True,
    'skyCleanupReversible': True,
}
(BASE / 'reports/roof-alignment-validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
