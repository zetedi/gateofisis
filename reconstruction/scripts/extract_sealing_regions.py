import bpy,numpy as np,json
from pathlib import Path
B=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'output/Gate-of-Isis-Roof-Aligned.blend'))
s=bpy.context.scene
for key,o in [('roof',s.objects['Roof · aligned to the gate rim']),('main',next(o for o in s.objects if o.type=='MESH' and o.name.startswith('Gate, approach')))]:
 m=o.data;v=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=v@mat[:3,:3].T+mat[:3,3]
 f=np.empty(len(m.polygons)*3,np.int32);m.polygons.foreach_get('vertices',f);f=f.reshape(-1,3)
 if key=='main':
  c=v[f].mean(1);sel=(c[:,0]>-.25)&(c[:,0]<1.3)&(c[:,1]>-3.0)&(c[:,1]<-1.85)&(c[:,2]>2.20);ids=np.flatnonzero(sel);f=f[sel]
 else:ids=np.arange(len(f))
 uv=np.empty(len(m.loops)*2,np.float32);m.uv_layers.active.data.foreach_get('uv',uv);uv=uv.reshape(-1,3,2)[ids]
 mids=np.empty(len(m.polygons),np.int32);m.polygons.foreach_get('material_index',mids);mids=mids[ids]
 used,inv=np.unique(f,return_inverse=True);f=inv.reshape(-1,3);v=v[used]
 np.savez(B/'work'/f'seal-{key}.npz',vertices=v,faces=f,uv=uv,materials=mids,originalFaceIds=ids,originalVertexIds=used)
 print(key,len(v),len(f),flush=True)
