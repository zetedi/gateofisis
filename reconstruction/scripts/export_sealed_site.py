"""Export every website detail level from the same sealed presentation master."""
import bpy, json, gc
import numpy as np
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
PUBLIC = BASE.parent / 'public/models'
bpy.ops.wm.open_mainfile(filepath=str(BASE / 'output/Gate-of-Isis-Sealed.blend'))
scene = bpy.context.scene
main = next(o for o in scene.objects if o.type == 'MESH' and o.name.startswith('Gate, approach'))
roof = scene.objects['Roof · aligned to the gate rim']
repair = scene.objects['Repaired capture gaps · roof seam and small holes']
extras = [roof, repair]

def export(objects, destination, format):
    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(destination), export_format=format, use_selection=True,
        export_image_format='JPEG', export_image_quality=92, export_extras=False,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=20, export_draco_texcoord_quantization=18,
        export_draco_normal_quantization=12, export_draco_color_quantization=10)

def decimate(obj, target):
    bpy.context.view_layer.objects.active=obj
    modifier=obj.modifiers.new('Web context reduction','DECIMATE')
    modifier.ratio=min(1, target/len(obj.data.polygons))
    modifier.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)

def resize_textures(objects, size):
    images={n.image for obj in objects for mat in obj.data.materials if mat
            for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for image in images:
        width,height=image.size
        if max(width,height)>size:
            ratio=size/max(width,height)
            image.scale(round(width*ratio),round(height*ratio))

mesh=main.data
v=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
matrix=np.array(main.matrix_world);world=v@matrix[:3,:3].T+matrix[:3,3]
f=np.empty(len(mesh.polygons)*3,np.int32);mesh.polygons.foreach_get('vertices',f);f=f.reshape(-1,3)
c=world[f].mean(1);gate=(c[:,0]>-.6)&(c[:,0]<1.65)&(c[:,1]>-4.2)&(c[:,1]<-1.8)
uv=np.empty(len(mesh.loops)*2,np.float32);mesh.uv_layers.active.data.foreach_get('uv',uv);uv=uv.reshape(-1,3,2)
mids=np.empty(len(mesh.polygons),np.int32);mesh.polygons.foreach_get('material_index',mids)
parts=[]
for name,mask in [('Gate · captured native detail',gate),('Surroundings · web detail',~gate)]:
    faces=f[mask];used,inverse=np.unique(faces,return_inverse=True);inverse=inverse.ravel().astype(np.int32)
    data=bpy.data.meshes.new(name);data.vertices.add(len(used));data.vertices.foreach_set('co',v[used].ravel())
    data.loops.add(len(inverse));data.loops.foreach_set('vertex_index',inverse)
    data.polygons.add(len(faces));data.polygons.foreach_set('loop_start',np.arange(len(faces),dtype=np.int32)*3)
    data.polygons.foreach_set('loop_total',np.full(len(faces),3,dtype=np.int32));data.uv_layers.new(name=mesh.uv_layers.active.name)
    data.uv_layers.active.data.foreach_set('uv',uv[mask].ravel())
    for mat in mesh.materials:data.materials.append(mat)
    data.polygons.foreach_set('material_index',mids[mask]);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.matrix_world=main.matrix_world.copy();parts.append(obj)
    if name.startswith('Surroundings'):decimate(obj,300000)
report={'nativeGateTriangles':int(gate.sum()),'contextTriangles':len(parts[1].data.polygons),
        'roofTriangles':len(roof.data.polygons),'repairTriangles':len(repair.data.polygons),
        'textureDimension':8192,'textureAtlases':11,'roofTextureDimension':[4096,2880],
        'geometry':'Captured gate and roof geometry retained. Surroundings reduced. Separate interpolated repair surfaces seal the upper scan gaps.',
        'gateRegion':{'x':[-.6,1.65],'y':[-4.2,-1.8]}}
export(parts+extras,BASE/'work/sealed-detail/gate-detail.gltf','GLTF_SEPARATE')
report['triangles']=sum(len(o.data.polygons) for o in parts+extras)
(BASE/'reports/detail-export.json').write_text(json.dumps(report,indent=2))
for obj in parts:
    data=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(data)
del v,world,f,c,uv,mids,gate,faces,used,inverse,mask,parts
gc.collect()
print('NATIVE_DETAIL_EXPORTED',flush=True)
# Weld the presentation assembly before simplification, so the shared seam cannot
# separate when a lower-detail mesh is generated. Per-corner UVs/colors survive.
combined_v=[];combined_f=[];combined_uv=[];combined_color=[];combined_mids=[];all_materials=[]
offset=0
for obj in [main]+extras:
    me=obj.data
    vv=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',vv);vv=vv.reshape(-1,3)
    mm=np.array(obj.matrix_world);vv=vv@mm[:3,:3].T+mm[:3,3]
    ff=np.empty(len(me.polygons)*3,np.int32);me.polygons.foreach_get('vertices',ff);ff=ff.reshape(-1,3)
    uu=np.zeros((len(me.polygons),3,2),np.float32)
    if me.uv_layers.active:me.uv_layers.active.data.foreach_get('uv',uu.ravel())
    cc=np.ones((len(me.polygons),3,4),np.float32)
    if obj==repair:
        vc=np.empty((len(me.vertices),4),np.float32)
        me.color_attributes.active_color.data.foreach_get('color',vc.ravel());cc=vc[ff]
    mid=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('material_index',mid)
    combined_v.append(vv);combined_f.append(ff+offset);combined_uv.append(uu);combined_color.append(cc)
    combined_mids.append(mid+len(all_materials));all_materials.extend(me.materials);offset+=len(vv)
v=np.concatenate(combined_v);f=np.concatenate(combined_f)
_,used,inverse=np.unique(np.round(v,6),axis=0,return_index=True,return_inverse=True)
f=inverse[f].astype(np.int32);v=v[used].astype(np.float32)
data=bpy.data.meshes.new('Sealed presentation surface')
data.vertices.add(len(v));data.vertices.foreach_set('co',v.ravel())
data.loops.add(f.size);data.loops.foreach_set('vertex_index',f.ravel())
data.polygons.add(len(f));data.polygons.foreach_set('loop_start',np.arange(len(f),dtype=np.int32)*3)
data.polygons.foreach_set('loop_total',np.full(len(f),3,dtype=np.int32))
data.uv_layers.new(name='UVMap');data.uv_layers.active.data.foreach_set('uv',np.concatenate(combined_uv).ravel())
color=data.color_attributes.new(name='RepairStone',type='FLOAT_COLOR',domain='CORNER')
color.data.foreach_set('color',np.concatenate(combined_color).ravel());data.color_attributes.active_color=color
for mat in all_materials:data.materials.append(mat)
data.polygons.foreach_set('material_index',np.concatenate(combined_mids));data.update()
combined=bpy.data.objects.new('Gate, roof and surroundings · sealed',data);scene.collection.objects.link(combined)
for obj in [main]+extras:
    me=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
    if me.users==0:bpy.data.meshes.remove(me)
del combined_v,combined_f,combined_uv,combined_color,combined_mids,v,f,used,inverse,vv,ff,uu,cc
main=combined;objects=[combined];gc.collect()
def upper_boundary_count(obj):
    me=obj.data;vv=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',vv);vv=vv.reshape(-1,3)
    ff=np.empty(len(me.polygons)*3,np.int32);me.polygons.foreach_get('vertices',ff);ff=ff.reshape(-1,3)
    edges=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1)
    edges,count=np.unique(edges,axis=0,return_counts=True);edges=edges[count==1];points=vv[edges]
    return int(np.all((points[:,:,0]>-.25)&(points[:,:,0]<1.3)&(points[:,:,1]>-3)&(points[:,:,1]<-1.85)&(points[:,:,2]>2.3)&(points[:,:,2]<2.8),axis=1).sum())
def close_web_seams(obj):
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data)
    def upper(vertex):
        x,y,z=vertex.co
        return -.25<x<1.3 and -3<y<-1.85 and 2.3<z<2.8
    # Resolve floating-point duplicates and tiny openings from simplification.
    bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if upper(v)],dist=.00002)
    edges=[e for e in bm.edges if e.is_boundary and all(upper(v) for v in e.verts)]
    made=bmesh.ops.holes_fill(bm,edges=edges,sides=0)['faces'] if edges else []
    color=bm.loops.layers.float_color.get('RepairStone')
    for face in made:
        face.material_index=len(obj.data.materials)-1
        for loop in face.loops:
            if color:loop[color]=(.46,.39,.29,1)
    if made:bmesh.ops.triangulate(bm,faces=made)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    print('WEB_SEAM_CAPS',len(made),flush=True)
decimate(main,1000000)
close_web_seams(main)
resize_textures(objects,4096)
export(objects,PUBLIC/'high/complete-site-high.gltf','GLTF_SEPARATE')
high={'file':'high/complete-site-high.gltf','triangles':len(main.data.polygons),'textureDimension':4096,
      'bytes':sum(p.stat().st_size for p in (PUBLIC/'high').iterdir()),'openUpperBoundaryEdges':upper_boundary_count(main)}
print('HIGH_EXPORTED',high,flush=True)
decimate(main,300000)
close_web_seams(main)
resize_textures(objects,2048)
export(objects,PUBLIC/'complete-site.glb','GLB')
standard={'file':'complete-site.glb','triangles':len(main.data.polygons),'textureDimension':2048,
          'bytes':(PUBLIC/'complete-site.glb').stat().st_size,'openUpperBoundaryEdges':upper_boundary_count(main)}
(BASE/'reports/site-export.json').write_text(json.dumps([high,standard],indent=2))
print('STANDARD_EXPORTED',standard,flush=True)
# Decimation at pinched source junctions needs the decoded seam-cap stage.
# inspect_web_roof.py -> prepare_web_seam_caps.py -> apply_web_seam_caps.py,
# followed by inspect_web_roof.py and validate_web_roof.py, verifies final closure.
print('RAW_DERIVATIVES_READY: run the decoded seam-cap stage before publication.',flush=True)
