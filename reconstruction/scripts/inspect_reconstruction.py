import bpy, json, sys
from pathlib import Path
from mathutils import Vector
import numpy as np
BASE=Path(__file__).resolve().parents[1]
source=BASE/'output/photogrammetry/gate-preview.usdz'
if '--' in sys.argv: source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.usd_import(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
stats=[]
for o in meshes:
    p=np.array([o.matrix_world@v.co for v in o.data.vertices])
    stats.append({'name':o.name,'vertices':len(p),'faces':len(o.data.polygons),'bounds':[p.min(0).tolist(),p.max(0).tolist()],'quantiles':np.quantile(p,[.01,.05,.5,.95,.99],axis=0).tolist()})
    print(stats[-1],flush=True)
print('IMAGES',[(i.name,list(i.size),i.filepath) for i in bpy.data.images],flush=True)
(BASE/'reports'/f'{source.stem}-inspection.json').write_text(json.dumps(stats,indent=2))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.device='CPU'
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG'
for o in meshes:
    for m in o.data.materials:
        if not m:continue
        textures=[n for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
        print('MATERIAL',m.name,[(t.name,t.image.name if t.image else None) for t in textures],flush=True)
        bsdf=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bsdf and bsdf.inputs['Base Color'].is_linked:
            source_socket=bsdf.inputs['Base Color'].links[0].from_socket
            out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
            em=m.node_tree.nodes.new('ShaderNodeEmission')
            m.node_tree.links.new(source_socket,em.inputs[0]);m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
center=(lo+hi)/2;size=max(hi-lo)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.1
for i,d in enumerate([(1,-1,.8),(-1,1,.8),(0,-1,.2),(0,0,1)]):
    cam.location=center+Vector(d).normalized()*size*2
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(BASE/'reports'/f'{source.stem}-{i}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.obj_export(filepath=str(BASE/'work'/f'{source.stem}.obj'),export_selected_objects=False,export_materials=True,path_mode='COPY')
