"""Stage unique originals, develop RAW files, and make inspection contact sheets."""
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import rawpy
from PIL import Image, ImageOps, ImageDraw

BASE = Path(__file__).resolve().parents[1]
inventory = json.loads((BASE / 'reports/photo-inventory.json').read_text())
root = Path(inventory['root'])
target = BASE / 'work/photos'
target.mkdir(parents=True, exist_ok=True)
photos = [p for p in inventory['photos'] if '/Others/' not in p['source']]

def stage(p):
    source = root / p['source']
    dest = target / (p['id'] + '.jpg')
    if not dest.exists():
        if source.suffix.lower() == '.cr2':
            with rawpy.imread(str(source)) as raw:
                rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
            image = Image.fromarray(rgb)
            # Preserve the camera's EXIF calibration hints through RAW development.
            try:
                with Image.open(source) as original:
                    exif = original.getexif()
                    exif[274] = 1
                    image.save(dest, quality=98, subsampling=0, exif=exif)
            except Exception:
                image.save(dest, quality=98, subsampling=0)
        else:
            try: os.link(source, dest)
            except OSError:
                import shutil
                shutil.copy2(source, dest)
    with Image.open(dest) as img:
        p['size'] = list(img.size)
    p['staged'] = dest.name
    return p

with ThreadPoolExecutor(max_workers=4) as pool:
    staged = []
    for p in pool.map(stage, photos):
        staged.append(p)
        if len(staged) % 50 == 0: print('Staged', len(staged), flush=True)
(BASE / 'reports/staged-photos.json').write_text(json.dumps(staged, indent=2))

groups = {}
for p in staged:
    group = p['source'].split('/')[0]
    groups.setdefault(group, []).append(p)
for group, items in groups.items():
    sampled = items[::max(1, len(items)//40)]
    canvas = Image.new('RGB', (1200, ((len(sampled)+5)//6)*164), '#ece9e1')
    draw = ImageDraw.Draw(canvas)
    for i,p in enumerate(sampled):
        with Image.open(target / p['staged']) as img:
            thumb = ImageOps.contain(ImageOps.exif_transpose(img), (196,138))
        x,y = (i%6)*200, (i//6)*164
        canvas.paste(thumb,(x,y))
        draw.text((x+3,y+140),p['id']+' '+Path(p['source']).name[:20],fill='#242c26')
    canvas.save(BASE/'reports'/f'contact-{group}.jpg', quality=85)
print('Ready:',len(staged),flush=True)
