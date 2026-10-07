"""Check the roof boundary in decoded web geometry, allowing Draco quantization."""
import json,numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
B=Path(__file__).resolve().parents[1]
reports=[]
for key in ['high','standard']:
 a=np.load(B/'work'/f'web-{key}-geometry.npz');v=a['vertices'];f=a['faces'];u,inv=np.unique(np.round(v,7),axis=0,return_inverse=True);f=inv[f]
 region=(u[:,0]>-.25)&(u[:,0]<1.3)&(u[:,1]>-3)&(u[:,1]<-1.85)&(u[:,2]>2.3)&(u[:,2]<2.8)
 ids=np.flatnonzero(region);pairs=cKDTree(u[ids]).query_pairs(.00004,output_type='ndarray');parent=np.arange(len(u))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,j in pairs:
  ri,rj=root(ids[i]),root(ids[j]);parent[rj]=ri
 for i in ids:parent[i]=root(i)
 f=parent[f];f=f[(f[:,0]!=f[:,1])&(f[:,1]!=f[:,2])&(f[:,0]!=f[:,2])]
 e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);ee,cc=np.unique(e,axis=0,return_counts=True);edge=ee[cc==1];open_edges=edge[np.all(region[edge],axis=1)]
 report={'quality':key,'decodedTriangles':len(a['faces']),'upperOpenBoundaryEdges':len(open_edges),'comparisonTolerance':.00004,'region':{'x':[-.25,1.3],'y':[-3,-1.85],'z':[2.3,2.8]},'note':'Coordinate proximity resolves per-material Draco quantization at the shared seam. Terrain/background capture edges are outside this roof-only test.'}
 print(json.dumps(report),flush=True);reports.append(report)
 if len(open_edges):
  print('OPEN BOUNDS',u[open_edges].min((0,1)),u[open_edges].max((0,1)),flush=True)
(B/'reports/web-roof-validation.json').write_text(json.dumps(reports,indent=2))
assert all(r['upperOpenBoundaryEdges']==0 for r in reports)
site=json.loads((B/'reports/site-export.json').read_text())
for entry,r in zip(site,reports):
 entry['openUpperBoundaryEdges']=r['upperOpenBoundaryEdges'];entry['closureCheck']='Decoded web geometry; roof-only region; 0.00004 reconstruction-unit quantization tolerance.'
(B/'reports/site-export.json').write_text(json.dumps(site,indent=2))
