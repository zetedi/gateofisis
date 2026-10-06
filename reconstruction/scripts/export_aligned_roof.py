"""Apply the reviewed rim correction and save a packed, editable roof alignment.

Uses the existing roof study. The original archival model and the earlier study
remain unchanged. Sky-colored rim artifacts are retained in a hidden collection.
"""
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

BASE = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(BASE / 'output/Gate-of-Isis-Roof-Study.blend'))
scene = bpy.context.scene
roof = next(o for o in scene.objects if o.name.startswith('Roof ·'))
main = next(o for o in scene.objects if o.type == 'MESH' and o != roof)
correction = json.loads((BASE / 'reports/roof-rim-alignment.json').read_text())
roof.matrix_world = Matrix(correction['correctionMatrix']) @ roof.matrix_world
roof.name = 'Roof · aligned to the gate rim'
roof['alignment'] = 'Height and tilt adjusted to the upper rim, guided by the matching stone joint. Rigid transform; no deformation or generated surfaces.'

mesh = main.data
faces = np.empty(len(mesh.polygons) * 3, np.int32)
mesh.polygons.foreach_get('vertices', faces)
faces = faces.reshape(-1, 3)
vertices = np.empty(len(mesh.vertices) * 3, np.float32)
mesh.vertices.foreach_get('co', vertices)
vertices = vertices.reshape(-1, 3)
uv = np.empty(len(mesh.loops) * 2, np.float32)
mesh.uv_layers.active.data.foreach_get('uv', uv)
uv = uv.reshape(-1, 3, 2)
material_ids = np.empty(len(mesh.polygons), np.int32)
mesh.polygons.foreach_get('material_index', material_ids)
sky_ids = np.load(BASE / 'work/roof-sky-faces.npz')['cleanFaceIds']
sky = np.zeros(len(faces), bool)
sky[sky_ids] = True
assert len(faces) == 12699647 and len(sky_ids) == 8854

# Split the inspected sky fragments without moving any retained vertex or UV.
def subset(name, selection):
    selected = faces[selection]
    used, inverse = np.unique(selected, return_inverse=True)
    inverse = inverse.ravel().astype(np.int32)
    data = bpy.data.meshes.new(name)
    data.vertices.add(len(used))
    data.vertices.foreach_set('co', vertices[used].ravel())
    data.loops.add(len(inverse))
    data.loops.foreach_set('vertex_index', inverse)
    data.polygons.add(len(selected))
    data.polygons.foreach_set('loop_start', np.arange(len(selected), dtype=np.int32) * 3)
    data.polygons.foreach_set('loop_total', np.full(len(selected), 3, np.int32))
    data.uv_layers.new(name=mesh.uv_layers.active.name)
    data.uv_layers.active.data.foreach_set('uv', uv[selection].ravel())
    for material in mesh.materials:
        data.materials.append(material)
    data.polygons.foreach_set('material_index', material_ids[selection])
    data.update()
    return data

artifact_data = subset('Original sky-colored rim fragments', sky)
visible_data = subset('Captured gate and site · sky rim isolated', ~sky)
main.data = visible_data
archive = bpy.data.collections.new('Capture artifacts · hidden, retained for reversibility')
scene.collection.children.link(archive)
artifacts = bpy.data.objects.new('Sky-colored roof rim · original capture', artifact_data)
archive.objects.link(artifacts)
artifacts.matrix_world = main.matrix_world.copy()
archive.hide_render = True
archive.hide_viewport = True
bpy.data.meshes.remove(mesh)
main['processing'] += ' In this derivative, 8,854 inspected sky-colored rim triangles are isolated in a hidden collection; retained stone coordinates and UVs are unchanged.'
scene['roofAlignmentStatus'] = 'Rim-aligned visual assembly. Height and tilt corrected; original captured surfaces retained. No independent metric control.'

old = bpy.data.texts.get('READ ME · Roof alignment study')
if old:
    bpy.data.texts.remove(old)
note = bpy.data.texts.new('READ ME · Aligned roof')
note.write('GATE OF ISIS — ALIGNED ROOF\n\nThe matching stone joint identified by the user anchors the existing horizontal placement.\nA rigid correction raises the roof and adjusts its tilt to the captured upper rim.\nThe roof remains a separate, editable object with its original mesh and UVs.\nSky-colored rim fragments are retained in the hidden Capture artifacts collection.\nThe original photographic master and earlier roof study remain separate files.\nNo replacement stone, artificial inscriptions, smoothing or hole filling was used.\nSee reports/roof-rim-alignment.json for the transform and overlap checks.\n')

camera = scene.camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 1.9
center = Vector((.53, -2.40, 2.40))
camera.location = center + Vector((-1, .2, .75)).normalized() * 10
camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.region_3d.view_location = center
            space.region_3d.view_distance = 3.0
            space.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
            space.shading.type = 'MATERIAL'
            space.overlay.show_overlays = False

bpy.ops.object.select_all(action='DESELECT')
roof.select_set(True)
bpy.context.view_layer.objects.active = roof
bpy.ops.file.pack_all()
output = BASE / 'output/Gate-of-Isis-Roof-Aligned.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('ALIGNED_FILE_SAVED', output, flush=True)
# A small, positioned roof derivative is available for future website integration.
bpy.ops.export_scene.gltf(filepath=str(BASE / 'work/roof-aligned.glb'), export_format='GLB', use_selection=True,
                          export_image_format='JPEG', export_image_quality=95, export_extras=False)

# Inspection renders only; preserve original material shaders in the saved file.
scene.render.engine = 'CYCLES'
scene.cycles.samples = 8
scene.cycles.device = 'CPU'
scene.render.resolution_x = 1300
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
for obj in [main, roof]:
    for material in obj.data.materials:
        if not material:
            continue
        bsdf = next((n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf and bsdf.inputs['Base Color'].is_linked:
            emission = material.node_tree.nodes.new('ShaderNodeEmission')
            material.node_tree.links.new(bsdf.inputs['Base Color'].links[0].from_socket, emission.inputs[0])
            out = next(n for n in material.node_tree.nodes if n.type == 'OUTPUT_MATERIAL')
            material.node_tree.links.new(emission.outputs[0], out.inputs['Surface'])
for name, direction in [('end', (-1, 0, .65)), ('opposite-end', (1, 0, .65)),
                        ('reverse', (-1, 1, .75)), ('front', (1, -1, .75)), ('above', (0, 0, 1))]:
    camera.location = center + Vector(direction).normalized() * 10
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(BASE / 'reports' / f'roof-aligned-{name}.png')
    bpy.ops.render.render(write_still=True)
