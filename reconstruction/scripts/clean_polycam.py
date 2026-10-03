"""Remove inspected transient capture fragments without retopology or UV changes.

Weld coordinates only for connected-component analysis; exported vertices keep
their original coordinates and per-corner UVs. Originals remain in assets/*.zip.
"""
import json
import shutil
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

BASE = Path(__file__).resolve().parents[1]
# Components were identified against orthographic textured inspection renders.
# Gate: the blue-shirted figure and four suspended capture fragments.
# Court: two incomplete floating human-shaped fragments.
REMOVE = {'site-b': {1, 2, 5, 8, 9}, 'site-a': {2, 3}, 'upper-stairs': set()}
report = []
for key, removed in REMOVE.items():
    source = BASE / 'work/polycam' / key
    lines = (source / '28_9_2026.obj').read_text().splitlines()
    vertices = np.array([list(map(float, l.split()[1:4])) for l in lines if l.startswith('v ')])
    faces = np.array([[int(t.split('/')[0])-1 for t in l.split()[1:]] for l in lines if l.startswith('f ')])
    unique, inverse = np.unique(np.round(vertices, 5), axis=0, return_inverse=True)
    welded = inverse[faces]
    edges = np.concatenate([welded[:, [0,1]], welded[:, [1,2]], welded[:, [2,0]]])
    graph = coo_matrix((np.ones(len(edges)), (edges[:,0],edges[:,1])), shape=(len(unique),len(unique)))
    _, welded_labels = connected_components(graph, directed=False)
    labels = welded_labels[inverse]
    keep = ~np.isin(labels[faces[:,0]], list(removed))
    for variant, selection in [('polycam-clean', keep), ('polycam-removed', ~keep)]:
        target = BASE / 'work' / variant / key
        target.mkdir(parents=True, exist_ok=True)
        used = np.unique(faces[selection])
        remap = {int(old)+1: i+1 for i,old in enumerate(used)}
        v_index = 0
        f_index = 0
        output = []
        for line in lines:
            if line.startswith('v '):
                v_index += 1
                if v_index in remap: output.append(line)
            elif line.startswith('f '):
                if selection[f_index]:
                    tokens = []
                    for token in line.split()[1:]:
                        parts = token.split('/')
                        parts[0] = str(remap[int(parts[0])])
                        tokens.append('/'.join(parts))
                    output.append('f ' + ' '.join(tokens))
                f_index += 1
            else: output.append(line)
        (target / '28_9_2026.obj').write_text('\n'.join(output)+'\n')
        shutil.copy2(source/'28_9_2026.mtl', target/'28_9_2026.mtl')
        if not (target/'textures').exists(): (target/'textures').symlink_to((source/'textures').resolve(), target_is_directory=True)
    report.append({'scan':key,'removedComponents':sorted(removed),'inputFaces':len(faces),'removedFaces':int((~keep).sum()),'outputFaces':int(keep.sum()),'method':'Remove visually identified disconnected transient fragments. No surface interpolation, smoothing or architectural geometry changes.'})
    print(report[-1])
(BASE/'reports/polycam-cleanup.json').write_text(json.dumps(report,indent=2))
