"""Save the presentation-ready master and derive two web resolutions from it."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector, Matrix
BASE=Path(__file__).resolve().parents[1]
PUBLIC=BASE.parent/'public/models'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'output/Gate-of-Isis.blend'))
scene=bpy.context.scene
objects=[o for o in scene.objects if o.type=='MESH']
if '--web-only' not in sys.argv:
    points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
    center=(lo+hi)/2;size=max(hi-lo)
    bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='Complete site · overview';camera.data.type='ORTHO';camera.data.ortho_scale=size*.95
    camera.location=center+Vector((1,-1,.85)).normalized()*size*2;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
    scene.render.engine='CYCLES';scene.cycles.samples=64;scene.render.resolution_x=2400;scene.render.resolution_y=1800
    scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.68,.63,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.8
    bpy.ops.object.light_add(type='AREA',location=(0,-2,8));light=bpy.context.object;light.name='Broad studio light';light.data.energy=1400;light.data.shape='DISK';light.data.size=8
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_location=center
                area.spaces.active.region_3d.view_distance=size*1.25
                area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
                area.spaces.active.shading.type='MATERIAL'
                area.spaces.active.overlay.show_overlays=False
    # Include editable supporting captures as clearly identified reference scenes.
    archive=BASE/'output/Gate-of-Isis-Polycam-Archive.blend'
    registration=json.loads((BASE/'reports/registration.json').read_text())
    with bpy.data.libraries.load(str(archive),link=False) as (source,target):target.scenes=source.scenes
    for reference in target.scenes:
        key='site-b' if 'Gate —' in reference.name else 'site-a' if 'Columns' in reference.name else 'upper-stairs'
        reference.name='Reference · '+('Top of gate — unregistered' if key=='upper-stairs' else key+' — registered')
        if key!='upper-stairs':
            transform=Matrix(registration[key]['matrix'])
            for o in reference.objects:o.matrix_world=transform@o.matrix_world
            reference['registration']=json.dumps({k:registration[key][k] for k in ['inliers','rmse','scale']})
        else:reference['registration']='Insufficient common texture evidence. Do not assume this scan is aligned to the photographic reconstruction.'
    bpy.context.window.scene=scene
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'output/Gate-of-Isis.blend'),compress=True)
    print('MASTER_SAVED',flush=True)
# Web derivatives only: the saved master above retains the full captured mesh.
stats=[]
for o in objects:
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    modifier=o.modifiers.new('Web detail reduction','DECIMATE');modifier.ratio=min(1,900000/sum(len(x.data.polygons) for x in objects));modifier.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    print('HIGH_DETAIL_FACES',len(o.data.polygons),flush=True)
for resolution,name,ratio in [(4096,'complete-site-high',1),(2048,'complete-site',.27)]:
    for o in objects:
        if ratio<1:
            bpy.context.view_layer.objects.active=o
            modifier=o.modifiers.new('Standard web detail','DECIMATE');modifier.ratio=ratio;modifier.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
        for mat in o.data.materials:
            for node in mat.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image:
                    im=node.image
                    if max(im.size)>resolution:im.scale(resolution,resolution)
        o.select_set(True)
    # Remove diagnostic absolute source paths from public metadata.
    for o in objects:
        for key in list(o.keys()):del o[key]
    bpy.ops.export_scene.gltf(filepath=str(PUBLIC/f'{name}.glb'),export_format='GLB',use_selection=True,export_image_format='JPEG',export_image_quality=92,export_extras=False)
    stats.append({'file':f'{name}.glb','triangles':sum(len(o.data.polygons) for o in objects),'textureDimension':resolution,'bytes':(PUBLIC/f'{name}.glb').stat().st_size})
    print(stats[-1],flush=True)
(BASE/'reports/site-export.json').write_text(json.dumps(stats,indent=2))
