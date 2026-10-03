"""Create GLBs and a packed archive after documented transient-fragment removal."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parents[1]
PUBLIC = BASE.parent/'public'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.name='01 · Gate — Polycam'
entries=[('site-b','Gate and waterside platform'),('site-a','Columns, pavement and loose stones'),('upper-stairs','Top of the gate')]
stats=[]
for idx,(key,title) in enumerate(entries):
    if idx:
        scene=bpy.data.scenes.new(f'{idx+1:02} · {title}')
        bpy.context.window.scene=scene
    bpy.ops.wm.obj_import(filepath=str(BASE/'work/polycam-clean'/key/'28_9_2026.obj'))
    objects=[o for o in bpy.context.selected_objects if o.type=='MESH']
    for o in objects:
        o.name=title
        o['source_archive']=['28_9_2026 3.zip','28_9_2026.zip','28_9_2026 2.zip'][idx]
        o['processing']='Transient human/capture fragments removed as recorded in polycam-cleanup.json. Remaining vertices, faces, UVs and full-resolution textures retained. Material metalness corrected to 0 for stone.'
        for mat in o.data.materials:
            if not mat:continue
            principled=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if principled:
                principled.inputs['Metallic'].default_value=0
                principled.inputs['Roughness'].default_value=1
    bpy.ops.export_scene.gltf(filepath=str(PUBLIC/'models'/f'{key}.glb'),export_format='GLB',use_selection=True,export_extras=True,export_image_format='AUTO')
    points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    center=(lo+hi)/2
    size=max(hi-lo)
    stats.append({'key':key,'title':title,'vertices':sum(len(o.data.vertices) for o in objects),'triangles':sum(len(p.vertices)-2 for o in objects for p in o.data.polygons),'textures':[{'name':i.name,'size':list(i.size)} for i in bpy.data.images if i.source=='FILE'],'bytes':(PUBLIC/'models'/f'{key}.glb').stat().st_size})
    bpy.ops.object.camera_add(location=center+Vector((-1,1,.65)).normalized()*size*1.8)
    camera=bpy.context.object
    camera.name='Survey overview'
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=size*1.15
    scene.camera=camera
    scene.world=bpy.data.worlds.new(f'{key} world')
    scene.world.color=(.65,.65,.65)
    scene['provenance']='Independent source scan, original Polycam coordinates. Cross-scan registration is not assumed.'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=size*1.4
                area.spaces.active.region_3d.view_location=center
                area.spaces.active.shading.type='MATERIAL'
bpy.context.window.scene=bpy.data.scenes['01 · Gate — Polycam']
readme=bpy.data.texts.new('READ ME · Source scans')
readme.write('GATE OF ISIS — BÎGEH\n\nThree Polycam surveys, captured 28 September 2026.\nEach scan is in its own named scene. Switch scenes in the top bar.\nThe scanned person and disconnected human/capture artifacts were removed.\nSee reconstruction/reports/polycam-cleanup.json for face counts and component IDs.\nAll remaining geometry, original UVs and original-resolution textures are preserved.\nAll images are packed; this file is self-contained.\nThe third scan is the TOP OF THE GATE, not the approach stairs.\nSource scans have independent coordinates: no unverified alignment is implied.\nA separate photogrammetry master is built from the photographs.\n')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'output/Gate-of-Isis-Polycam-Archive.blend'),compress=True)
(BASE/'reports/polycam-export.json').write_text(json.dumps(stats,indent=2))
