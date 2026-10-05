"""Encode original 8K atlases for GPU delivery and package the detailed glTF."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, subprocess, shutil
BASE=Path(__file__).resolve().parents[1]
DEST=BASE.parent/'public/models/detail'
DEST.mkdir(parents=True,exist_ok=True)
WORK=BASE/'work/detail-textures'
WORK.mkdir(exist_ok=True)
def compress(i):
    target=WORK/f'atlas-{i}.ktx2'
    if not target.exists():
        args=['basisu','-file',str(BASE/f'work/raw-textures/baked_mesh_248b9bf8_tex{i}.png'),
              '-q','255','-comp_level','2','-mipmap','-no_alpha','-srgb','-max_threads','8','-output_file',str(target)]
        with (BASE/f'reports/texture-{i}.log').open('w') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
    shutil.copy2(target,DEST/target.name)
    print(f'Atlas {i}: {target.stat().st_size:,} bytes',flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(compress,range(11)))
source=BASE/'work/detail-export/gate-detail.gltf'
doc=json.loads(source.read_text())
for im in doc['images']:
    name=im['uri'];index=int(name.split('_tex')[1].split('.')[0])
    im['uri']=f'atlas-{index}.ktx2';im['mimeType']='image/ktx2'
for tex in doc['textures']:
    tex.setdefault('extensions',{})['KHR_texture_basisu']={'source':tex.pop('source')}
for key in ['extensionsUsed','extensionsRequired']:
    doc.setdefault(key,[])
    if 'KHR_texture_basisu' not in doc[key]:doc[key].append('KHR_texture_basisu')
for buffer in doc['buffers']:shutil.copy2(source.parent/buffer['uri'],DEST/buffer['uri'])
(DEST/'gate-detail.gltf').write_text(json.dumps(doc,separators=(',',':')))
report=json.loads((BASE/'reports/detail-export.json').read_text())
report['textureCompression']='KTX2 ETC1S, quality 255, original 8192 px, sRGB mipmaps'
report['totalBytes']=sum(p.stat().st_size for p in DEST.iterdir())
(BASE/'reports/detail-export.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
