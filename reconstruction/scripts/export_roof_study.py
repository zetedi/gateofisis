"""Save an editable, explicitly provisional roof placement in a separate Blender file.

Run register_roof_geometry.py first, then invoke this script inside Blender.
The archival master, source scans and published models are not overwritten.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'output/Gate-of-Isis.blend'))
s=bpy.context.scene
# Keep all main captured geometry unchanged. Roof remains an independent editable object.
bpy.ops.wm.obj_import(filepath=str(B/'work/polycam-clean/upper-stairs/28_9_2026.obj'))
roof=[o for o in bpy.context.selected_objects if o.type=='MESH']
m=Matrix(json.loads((B/'work/roof-candidate.json').read_text())['matrix'])
for o in roof:
 # Disconnected capture fragment below the roof; use connected component identity, not a surface crop.
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=[v for v in bm.verts if v.co.y<0]
 assert bad and max(v.co.y for v in bad)<-.08, 'Unexpected roof fragment bounds'
 assert min(v.co.y for v in bm.verts if v.co.y>=0)>.07, 'Unexpected roof surface bounds'
 bmesh.ops.delete(bm,geom=bad,context='VERTS');bm.to_mesh(o.data);bm.free()
 o.matrix_world=m@o.matrix_world;o.name='Roof · provisional geometric alignment';o['alignment']='Geometric candidate only; not independently validated. Source roof retained as a separate editable object.'
# Save an inspectable file first, using original material shaders.
s['roofAlignmentStatus']='PROVISIONAL. Geometric overlap; no validated texture landmarks or survey control.'
notes=bpy.data.texts.new('READ ME · Roof alignment study');notes.write('ROOF ALIGNMENT STUDY — PROVISIONAL\n\nThe top scan is placed above the gate using constrained surface registration.\nOriginal capture vertices and UVs are preserved; no surfaces are filled or welded.\nThe detached capture fragment below the roof is excluded from this candidate only.\nThe source archive remains unchanged.\nThis is an inspection study, not a validated archival fusion.\nSee reports/roof-registration.json for overlap and stability checks.\n')
center=Vector((.52,-2.40,2.35))
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=2.05;cam.location=center+Vector((1,-1,.7)).normalized()*10;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_location=(.5,-2.8,1.7);area.spaces.active.region_3d.view_distance=4;area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
   area.spaces.active.shading.type='MATERIAL'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(B/'output/Gate-of-Isis-Roof-Study.blend'),compress=True);print('STUDY_SAVED',flush=True)
bpy.ops.object.select_all(action='DESELECT')
for o in roof:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(B/'work/roof-candidate.glb'),export_format='GLB',use_selection=True,export_image_format='JPEG',export_image_quality=95,export_extras=False)
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.device='CPU';s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
for o in [o for o in s.objects if o.type=='MESH']:
 for mat in o.data.materials:
  if not mat:continue
  bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bsdf and bsdf.inputs['Base Color'].is_linked:
   em=mat.node_tree.nodes.new('ShaderNodeEmission');mat.node_tree.links.new(bsdf.inputs['Base Color'].links[0].from_socket,em.inputs[0]);out=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
for name,d in [('above',(0,0,1)),('front',(1,-1,.6)),('reverse',(-1,1,.6)),('end',(1,0,.1))]:
 cam.location=center+Vector(d).normalized()*10;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(B/'reports'/f'roof-candidate-{name}.png');bpy.ops.render.render(write_still=True)
