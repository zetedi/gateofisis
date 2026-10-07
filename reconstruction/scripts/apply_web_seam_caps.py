"""Close tiny simplification gaps in the actual decoded presentation exports."""
import bpy, json, shutil, numpy as np
from pathlib import Path
B=Path(__file__).resolve().parents[1];P=B.parent/'public/models'
site=json.loads((B/'reports/site-export.json').read_text())
for key,entry in zip(['high','standard'],site):
    source=P/entry['file']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    data=np.load(B/'work'/f'web-{key}-microcaps.npz')
    mesh=bpy.data.meshes.new('Tiny web seam repairs')
    mesh.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist());mesh.update()
    obj=bpy.data.objects.new('Tiny web seam repairs',mesh);bpy.context.scene.collection.objects.link(obj)
    mat=bpy.data.materials.new('Interpolated stone · web seam');mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.46,.39,.29,1)
    shader.inputs['Roughness'].default_value=1
    mat.diffuse_color=(.46,.39,.29,1);mesh.materials.append(mat)
    color=mesh.color_attributes.new(name='RepairStone',type='FLOAT_COLOR',domain='POINT')
    color.data.foreach_set('color',np.tile([.46,.39,.29,1],len(mesh.vertices)))
    mesh.color_attributes.active_color=color
    node=mat.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='RepairStone'
    mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    temp=B/'work'/f'capped-{key}';temp.mkdir(exist_ok=True)
    destination=temp/source.name
    bpy.ops.export_scene.gltf(filepath=str(destination),export_format='GLTF_SEPARATE' if key=='high' else 'GLB',
        export_image_format='AUTO',export_extras=False,
        export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,
        export_draco_position_quantization=20,export_draco_texcoord_quantization=18,
        export_draco_normal_quantization=12,export_draco_color_quantization=10)
    entry['triangles']=sum(len(o.data.polygons) for o in bpy.context.scene.objects if o.type=='MESH')
    if key=='high':
        doc=json.loads(destination.read_text())
        files={destination.name}|{x['uri'] for x in doc.get('buffers',[])+doc.get('images',[])}
        for name in files:shutil.copy2(temp/name,source.parent/name)
        for old in source.parent.iterdir():
            if old.is_file() and old.name not in files:old.unlink()
        entry['bytes']=sum((source.parent/n).stat().st_size for n in files)
    else:
        shutil.copy2(destination,source);entry['bytes']=source.stat().st_size
    entry['webSeamCapTriangles']=len(data['faces'])
    print('CAPPED',key,entry,flush=True)
(B/'reports/site-export.json').write_text(json.dumps(site,indent=2))
