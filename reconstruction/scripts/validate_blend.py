import bpy,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(BASE/'output/Gate-of-Isis.blend'))
main=bpy.context.scene
meshes=[o for o in main.objects if o.type=='MESH']
faces=sum(len(o.data.polygons) for o in meshes)
assert faces==12699647, faces
images=[i for i in bpy.data.images if i.source=='FILE']
missing=[i.name for i in images if not i.packed_file and not i.packed_files]
assert not missing, missing
atlas=[i for i in images if tuple(i.size)==(8192,8192)]
assert len(atlas)==11,len(atlas)
assert len(bpy.data.scenes)==4,len(bpy.data.scenes)
uv_issues=[]
for o in meshes:
    for m in o.data.materials:
        for node in m.node_tree.nodes:
            if node.type=='UVMAP' and node.uv_map and node.uv_map not in o.data.uv_layers:uv_issues.append(node.uv_map)
assert not uv_issues,uv_issues
report={'mainScene':main.name,'mainTriangles':faces,'packedImages':len(images),'fullResolutionAtlases':len(atlas),'scenes':[s.name for s in bpy.data.scenes],'missingExternalImages':missing,'uvLayerIssues':uv_issues,'bytes':(BASE/'output/Gate-of-Isis.blend').stat().st_size}
(BASE/'reports/blender-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
