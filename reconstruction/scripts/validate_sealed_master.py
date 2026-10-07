"""Validate the packed sealed master and unchanged captured surface meshes."""
import bpy,json,hashlib
import numpy as np
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def meshes():
 return {o.name:o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('Gate, approach') or o.name.startswith('Roof ·'))}
def digest(o):
 h=hashlib.sha256();m=o.data
 for collection,attribute,n,dtype in [(m.vertices,'co',3,np.float32),(m.polygons,'vertices',3,np.int32),(m.uv_layers.active.data,'uv',2,np.float32)]:
  a=np.empty(len(collection)*n,dtype);collection.foreach_get(attribute,a);h.update(a.tobytes())
 h.update(np.array(o.matrix_world).tobytes());return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(B/'output/Gate-of-Isis-Roof-Aligned.blend'))
original={name:digest(o) for name,o in meshes().items()}
bpy.ops.wm.open_mainfile(filepath=str(B/'output/Gate-of-Isis-Sealed.blend'))
assert original=={name:digest(o) for name,o in meshes().items()}
patch=bpy.context.scene.objects['Repaired capture gaps · roof seam and small holes']
assert len(patch.data.polygons)==19593
assert patch.data.color_attributes.active_color
colors=np.empty(len(patch.data.vertices)*4,np.float32);patch.data.color_attributes.active_color.data.foreach_get('color',colors)
assert np.isfinite(colors).all() and colors.min()>=0 and colors.max()<=1
used=[*meshes().values(),patch]
images={n.image for o in used for m in o.data.materials if m for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
assert all(i.packed_file or i.packed_files for i in images)
r={'capturedGeometryUvsTransformsUnchanged':True,'allTexturesPacked':True,'repairTriangles':len(patch.data.polygons),'repairSeparateEditableMesh':True,'repairColorsFinite':True}
(B/'reports/sealed-master-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
