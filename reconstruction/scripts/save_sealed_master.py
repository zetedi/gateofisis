import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'output/Gate-of-Isis-Roof-Aligned.blend'))
a=np.load(B/'work/seal-patch.npz');mesh=bpy.data.meshes.new('Interpolated seam closure');mesh.from_pydata(a['vertices'].tolist(),[],a['faces'].tolist());mesh.update()
colors=mesh.color_attributes.new(name='RepairStone',type='FLOAT_COLOR',domain='POINT');rgba=np.column_stack([a['colors'],np.ones(len(a['vertices']))]).astype(np.float32);colors.data.foreach_set('color',rgba.ravel());mesh.color_attributes.active_color=colors
mat=bpy.data.materials.new('Repair · adjacent captured stone colors');mat.use_nodes=True;node=mat.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='RepairStone';bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.95;mesh.materials.append(mat)
patch=bpy.data.objects.new('Repaired capture gaps · roof seam and small holes',mesh);bpy.context.scene.collection.objects.link(patch);patch['provenance']='Interpolated closure geometry, not a captured surface. Colors sampled from adjacent captured stone. No generated inscriptions.'
s=bpy.context.scene;s['roofAlignmentStatus']='Roof aligned to the upper rim; roof perimeter and small upper capture gaps sealed with identifiable repair geometry.'
n=bpy.data.texts.new('READ ME · Sealed roof');n.write('SEALED ROOF PRESENTATION MASTER\n\nThe gate, aligned top scan and repair mesh share one coordinate frame.\nThe roof perimeter and small upper capture holes are closed with a separate repair mesh.\nOriginal stone coordinates and UVs remain unchanged. No carved details were generated.\nRepair colors come from adjacent captured stone textures.\nDoorway, real recesses and terrain capture perimeter remain open.\nThe original photographic master and aligned study remain separate files.\nSee roof-sealing.json for edge-closure verification.\n')
bpy.ops.object.select_all(action='DESELECT');patch.select_set(True);bpy.context.view_layer.objects.active=patch
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(B/'output/Gate-of-Isis-Sealed.blend'),compress=True);print('SEALED_MASTER_SAVED',flush=True)
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.device='CPU';s.render.resolution_x=1300;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
for o in [o for o in s.objects if o.type=='MESH' and not o.hide_get()]:
 for m in o.data.materials:
  if not m:continue
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs and bs.inputs['Base Color'].is_linked:
   em=m.node_tree.nodes.new('ShaderNodeEmission');m.node_tree.links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs[0]);out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL');m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
cam=s.camera;cam.data.ortho_scale=1.9;center=Vector((.53,-2.4,2.4))
for name,d in [('end',(-1,0,.65)),('reverse',(-1,1,.75)),('above',(0,0,1))]:
 cam.location=center+Vector(d).normalized()*10;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(B/'reports'/f'roof-sealed-{name}.png');bpy.ops.render.render(write_still=True)
