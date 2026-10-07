"""Reuse the original 8K atlases and add the native roof texture to the new detail model."""
import json, shutil, subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[1]
source=B/'work/sealed-detail/gate-detail.gltf'
target=B.parent/'public/models/detail'
roof=B/'work/detail-textures/roof-atlas.ktx2'
if not roof.exists():
    subprocess.run(['basisu','-file',str(B/'work/polycam/upper-stairs/textures/d228023574d9e8de4df6133b2f2143bf.jpg'),
                    '-q','255','-comp_level','2','-mipmap','-no_alpha','-srgb','-max_threads','8','-output_file',str(roof)],check=True)
shutil.copy2(roof,target/roof.name)
doc=json.loads(source.read_text())
for image in doc['images']:
    image['uri']=f"atlas-{int(image['uri'].split('_tex')[1].split('.')[0])}.ktx2" if '_tex' in image['uri'] else roof.name
    image['mimeType']='image/ktx2'
for texture in doc['textures']:
    texture.setdefault('extensions',{})['KHR_texture_basisu']={'source':texture.pop('source')}
for key in ['extensionsUsed','extensionsRequired']:
    doc.setdefault(key,[])
    if 'KHR_texture_basisu' not in doc[key]:doc[key].append('KHR_texture_basisu')
for buffer in doc['buffers']:
    old=buffer['uri'];buffer['uri']='gate-detail-sealed.bin'
    shutil.copy2(source.parent/old,target/buffer['uri'])
output=target/'gate-detail-sealed.gltf';output.write_text(json.dumps(doc,separators=(',',':')))
report=json.loads((B/'reports/detail-export.json').read_text())
report['textureCompression']='Original eleven 8K KTX2 atlases reused unchanged; native 4096×2880 roof atlas encoded as KTX2 ETC1S quality 255.'
report['totalBytes']=output.stat().st_size+sum((target/x['uri']).stat().st_size for x in doc['buffers']+doc['images'])
(B/'reports/detail-export.json').write_text(json.dumps(report,indent=2))
# Retire obsolete derived detail resources after the replacements have been written.
for name in ['gate-detail.gltf','gate-detail.bin']:
    old=target/name
    if old.exists():old.unlink()
print(report['totalBytes'],flush=True)
