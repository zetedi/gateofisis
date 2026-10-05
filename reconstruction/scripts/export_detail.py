"""Keep native gate geometry and all 8K UVs; simplify only its wider context."""
import bpy, json, numpy as np
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'work/detail-export'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE / 'output/Gate-of-Isis.blend'))
source = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
mesh = source.data
mesh.calc_loop_triangles()
vertices = np.empty(len(mesh.vertices)*3, np.float32)
mesh.vertices.foreach_get('co', vertices)
vertices = vertices.reshape(-1,3)
matrix = np.array(source.matrix_world)
world = vertices @ matrix[:3,:3].T + matrix[:3,3]
faces = np.empty(len(mesh.loop_triangles)*3, np.int32)
mesh.loop_triangles.foreach_get('vertices', faces)
faces = faces.reshape(-1,3)
centers = world[faces].mean(1)
gate = (centers[:,0] > -.6) & (centers[:,0] < 1.65) & (centers[:,1] < -1.8) & (centers[:,1] > -4.2)
loops = np.empty(len(mesh.loop_triangles)*3, np.int32)
mesh.loop_triangles.foreach_get('loops', loops)
uv = np.empty(len(mesh.loops)*2, np.float32)
mesh.uv_layers.active.data.foreach_get('uv',uv)
uv = uv.reshape(-1,2)[loops].reshape(-1,3,2)
materials = np.empty(len(mesh.loop_triangles),np.int32)
mesh.loop_triangles.foreach_get('material_index',materials)
objects=[]
for name,mask in [('Gate · native captured detail',gate),('Surroundings · web detail',~gate)]:
    f=faces[mask];used,inverse=np.unique(f,return_inverse=True);inverse=inverse.ravel()
    data=bpy.data.meshes.new(name)
    data.vertices.add(len(used));data.vertices.foreach_set('co',vertices[used].ravel())
    data.loops.add(len(inverse));data.loops.foreach_set('vertex_index',inverse.astype(np.int32))
    data.polygons.add(len(f));data.polygons.foreach_set('loop_start',np.arange(len(f),dtype=np.int32)*3)
    data.polygons.foreach_set('loop_total',np.full(len(f),3,dtype=np.int32))
    data.uv_layers.new(name=mesh.uv_layers.active.name);data.uv_layers.active.data.foreach_set('uv',uv[mask].ravel())
    for mat in mesh.materials:data.materials.append(mat)
    data.polygons.foreach_set('material_index',materials[mask]);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.matrix_world=source.matrix_world.copy()
    objects.append(obj)
    print(name,len(f),flush=True)
    if 'Surroundings' in name:
        bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Context reduction','DECIMATE');mod.ratio=min(1,300000/len(f));mod.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'gate-detail.gltf'),export_format='GLTF_SEPARATE',use_selection=True,
    export_image_format='JPEG',export_image_quality=96,export_extras=False,
    export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,
    export_draco_position_quantization=20,export_draco_texcoord_quantization=18,export_draco_normal_quantization=12)
report={'nativeGateTriangles':int(gate.sum()),'contextTriangles':len(objects[1].data.polygons),
    'textureDimension':8192,'textureAtlases':11,'geometry':'Original gate vertices and UVs retained; context decimated. Draco position quantization: 20 bits.',
    'gateRegion':{'x':[-.6,1.65],'y':[-4.2,-1.8]}}
(BASE/'reports/detail-export.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
