import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
standard=B.parent/'public/models/complete-site.glb'
if not standard.exists():standard=B.parent/'public/models/complete-site-sealed.glb'
for key,path in [('high',B.parent/'public/models/high/complete-site-high.gltf'),('standard',standard)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
 vs=[];fs=[];offset=0
 for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
  m=o.data;v=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=v@mat[:3,:3].T+mat[:3,3]
  f=np.empty(len(m.polygons)*3,np.int32);m.polygons.foreach_get('vertices',f);f=f.reshape(-1,3)
  vs.append(v);fs.append(f+offset);offset+=len(v)
 np.savez(B/'work'/f'web-{key}-geometry.npz',vertices=np.concatenate(vs),faces=np.concatenate(fs));print('EXTRACTED',key,flush=True)
 if key=='standard':
  s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.device='CPU';s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
  for o in [o for o in s.objects if o.type=='MESH']:
   for mat in o.data.materials:
    if not mat:continue
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bs and bs.inputs['Base Color'].is_linked:
     em=mat.node_tree.nodes.new('ShaderNodeEmission');mat.node_tree.links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs[0]);out=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
  bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2;center=Vector((.53,-2.4,2.35));cam.location=center+Vector((-1,1,.9)).normalized()*10;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(B/'reports/web-sealed-roof.png');bpy.ops.render.render(write_still=True)
