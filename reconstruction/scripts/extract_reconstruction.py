import bpy, json, numpy as np
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.usd_import(filepath=str(BASE/'output/photogrammetry/gate-raw.usdz'))
scene=bpy.context.scene;scene.name='Photogrammetry · original full detail'
info=[]
for i,o in enumerate([o for o in scene.objects if o.type=='MESH']):
    mesh=o.data;mesh.calc_loop_triangles()
    v=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
    mat=np.array(o.matrix_world,dtype=np.float32);v=v@mat[:3,:3].T+mat[:3,3]
    f=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3)
    loops=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('loops',loops)
    uv=np.empty(len(mesh.loops)*2,dtype=np.float32);mesh.uv_layers.active.data.foreach_get('uv',uv);uv=uv.reshape(-1,2)[loops].reshape(-1,3,2)
    mid=np.empty(len(mesh.loop_triangles),dtype=np.int32);mesh.loop_triangles.foreach_get('material_index',mid)
    np.savez(BASE/'work'/f'raw-mesh-{i}.npz',vertices=v,faces=f,uv=uv,materials=mid)
    textures=[]
    for m in mesh.materials:
        bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        tex=bsdf.inputs['Base Color'].links[0].from_node.image
        target=BASE/'work/raw-textures'/tex.name;target.parent.mkdir(exist_ok=True)
        tex.filepath_raw=str(target);tex.save()
        textures.append({'name':m.name,'image':str(target),'size':list(tex.size)})
    info.append({'name':o.name,'vertices':len(v),'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'textures':textures})
    print(json.dumps(info[-1]),flush=True)
(BASE/'reports/raw-mesh.json').write_text(json.dumps(info,indent=2))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'output/Gate-of-Isis-Raw.blend'),compress=True)
