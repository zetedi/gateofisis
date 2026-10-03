"""Render the source scans without altering their geometry or texture resolution."""
import bpy
import math
import json
import sys
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parents[1]
VARIANT = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'polycam'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 8
scene.cycles.device = 'CPU'
scene.render.resolution_x = 900
scene.render.resolution_y = 760
scene.render.resolution_percentage = 100
scene.world.color = (.7,.7,.7)
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.type = 'ORTHO'
stats = {}
for key in ['site-a','upper-stairs','site-b']:
    bpy.ops.wm.obj_import(filepath=str(BASE/'work'/VARIANT/key/'28_9_2026.obj'))
    objects = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if not objects: continue
    points = [o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    center=(lo+hi)/2
    size=max(hi-lo)
    stats[key]={'bounds':[list(lo),list(hi)],'vertices':sum(len(o.data.vertices) for o in objects),'faces':sum(len(o.data.polygons) for o in objects)}
    for o in objects:
        for mat in o.data.materials:
            if not mat:continue
            mat.use_nodes=True
            nodes=mat.node_tree.nodes
            tex=next((n for n in nodes if n.type=='TEX_IMAGE'),None)
            out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
            if tex:
                emission=nodes.new('ShaderNodeEmission')
                mat.node_tree.links.new(tex.outputs['Color'],emission.inputs['Color'])
                mat.node_tree.links.new(emission.outputs[0],out.inputs['Surface'])
    camera.data.ortho_scale=size*1.2
    for n, direction in enumerate([(1,-1,.7),(-1,1,.7),(0,-1,.15),(0,0,1)]):
        camera.location=center+Vector(direction).normalized()*size*2
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(BASE/'reports'/f'{VARIANT}-{key}-{n}.png')
        bpy.ops.render.render(write_still=True)
    for o in objects: bpy.data.objects.remove(o,do_unlink=True)
(BASE/'reports/polycam-stats.json').write_text(json.dumps(stats,indent=2))
