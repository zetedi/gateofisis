"""Preserve the photo-derived monument and ground; remove capture background."""
import bpy, json, numpy as np, sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
preview='--preview' in sys.argv
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
if preview:
    bpy.ops.wm.usd_import(filepath=str(BASE/'output/photogrammetry/gate-preview.usdz'))
else:
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'output/Gate-of-Isis-Raw.blend'))
scene=bpy.context.scene;scene.name='Gate and surroundings · photographic reconstruction'
stats=[]
for o in [o for o in scene.objects if o.type=='MESH']:
    mesh=o.data;mesh.calc_loop_triangles()
    v=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
    matrix=np.array(o.matrix_world);world=v@matrix[:3,:3].T+matrix[:3,3]
    f=np.empty(len(mesh.loop_triangles)*3,np.int32);mesh.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3)
    loops=np.empty(len(mesh.loop_triangles)*3,np.int32);mesh.loop_triangles.foreach_get('loops',loops)
    uv=np.empty(len(mesh.loops)*2,np.float32);mesh.uv_layers.active.data.foreach_get('uv',uv);uv=uv.reshape(-1,2)[loops].reshape(-1,3,2)
    mid=np.empty(len(mesh.loop_triangles),np.int32);mesh.loop_triangles.foreach_get('material_index',mid)
    # The isolated reconstructed sky sheets are disconnected from the physical site.
    if preview:
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
        _,labels=connected_components(coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))),directed=False)
    else:labels=np.load(BASE/'work/raw-components.npy')
    center=world[f].mean(1)
    largest=np.bincount(labels).argmax()
    keep=(labels[f[:,0]]==largest)&(center[:,1]<=2.70)&~((center[:,1]>2.15)&(center[:,2]>1.10))
    newfaces=f[keep];used,inverse=np.unique(newfaces,return_inverse=True)
    inverse=inverse.ravel()
    data=bpy.data.meshes.new('Captured stone and terrain')
    data.vertices.add(len(used));data.vertices.foreach_set('co',v[used].ravel())
    data.loops.add(len(inverse));data.loops.foreach_set('vertex_index',inverse.astype(np.int32))
    data.polygons.add(len(newfaces));data.polygons.foreach_set('loop_start',np.arange(len(newfaces),dtype=np.int32)*3);data.polygons.foreach_set('loop_total',np.full(len(newfaces),3,dtype=np.int32))
    data.uv_layers.new(name=mesh.uv_layers.active.name);data.uv_layers.active.data.foreach_set('uv',uv[keep].ravel())
    for m in mesh.materials:data.materials.append(m)
    data.polygons.foreach_set('material_index',mid[keep]);data.update()
    o.data=data;bpy.data.meshes.remove(mesh)
    o.name='Gate, approach, columns, pavement and surrounding stones'
    o['source']='1,054 registered photographs; RealityKit Object Capture raw reconstruction'
    o['processing']='Detached sky/capture fragments and incomplete background vegetation removed; original stone vertices and UVs retained. No generated stone geometry.'
    stats.append({'inputFaces':len(f),'retainedFaces':int(keep.sum()),'vertices':len(used)})
    print(stats[-1],flush=True)
    del v,world,f,uv,mid,center,newfaces,used,inverse,keep,loops,labels
if not preview:
    scene['scale']='Relative reconstruction units. No independent survey-control distances supplied.'
    scene['registeredPhotographs']=1054
    scene['inputPhotographs']=1055
    note=bpy.data.texts.new('READ ME · Gate of Isis')
    note.write('GATE OF ISIS — PHOTOGRAMMETRY MASTER\n\n1,054 registered cameras from 1,055 unique survey photographs.\n11 original 8192 × 8192 texture atlases. All textures packed.\nGate, approach stairs, columns, pavement and loose stones share one coordinate system.\nSky sheets and incomplete vegetation were cropped; no stone surfaces were invented.\nDimensions are relative: no independent survey control was supplied.\nSee reconstruction/reports and reconstruction/README.md for processing details.\nThe top-of-gate Polycam capture remains a separate reference until registration can be validated.\n')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'output/Gate-of-Isis.blend'),compress=True)
    (BASE/'reports/photogrammetry-cleanup.json').write_text(json.dumps(stats,indent=2))
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.device='CPU'
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard'
for o in [o for o in scene.objects if o.type=='MESH']:
    for m in o.data.materials:
        bsdf=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bsdf and bsdf.inputs['Base Color'].is_linked:
            em=m.node_tree.nodes.new('ShaderNodeEmission');m.node_tree.links.new(bsdf.inputs['Base Color'].links[0].from_socket,em.inputs[0])
            out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL');m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
points=[o.matrix_world@Vector(v) for o in scene.objects if o.type=='MESH' for v in o.bound_box]
lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
center=(lo+hi)/2;size=max(hi-lo)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.0;scene.camera=cam
for i,d in enumerate([(1,-1,.85),(-1,-1,.9),(0,0,1)]):
    cam.location=center+Vector(d).normalized()*size*2;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(BASE/'reports'/f'clean-photo-{i}.png');bpy.ops.render.render(write_still=True)
