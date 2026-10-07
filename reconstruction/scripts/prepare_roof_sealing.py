"""Trace captured boundaries, bridge the roof seam and close small upper holes.

Run extract_sealing_regions.py inside Blender first. This script runs in the
reconstruction Python environment. It writes a separate repair mesh, retains
captured surface geometry, and records open/non-manifold edge counts.
"""

import numpy as np,json
from pathlib import Path
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
B=Path(__file__).resolve().parents[1]
results={}
for key in ['roof','main']:
 a=np.load(B/'work'/f'seal-{key}.npz');v=a['vertices'];f=a['faces'];u,ix,inv=np.unique(np.round(v,6),axis=0,return_index=True,return_inverse=True);v=v[ix];f=inv[f]
 e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);ue,counts=np.unique(e,axis=0,return_counts=True);edge=ue[counts==1]
 n,labels=connected_components(coo_matrix((np.ones(len(edge)),(edge[:,0],edge[:,1])),shape=(len(v),len(v))),directed=False)
 comps=[]
 for cid in np.unique(labels[edge[:,0]]):
  ee=edge[labels[edge[:,0]]==cid];vv=np.unique(ee);p=v[vv];length=float(np.linalg.norm(v[ee[:,0]]-v[ee[:,1]],axis=1).sum());degree=np.bincount(ee.ravel(),minlength=len(v))[vv]
  comps.append({'id':int(cid),'vertices':len(vv),'length':length,'min':p.min(0).tolist(),'max':p.max(0).tolist(),'mean':p.mean(0).tolist(),'branched':int((degree!=2).sum())})
 comps.sort(key=lambda x:-x['length']);results[key]=comps
 np.savez(B/'work'/f'seal-{key}-boundary.npz',vertices=v,faces=f,boundaryEdges=edge,labels=labels,originalVertexIndices=ix)
 print(key,'nonmanifold',int((counts>2).sum()),'loops',len(comps));print(json.dumps(comps[:15],indent=2),flush=True)
(B/'work/seal-boundary-analysis.json').write_text(json.dumps(results,indent=2))


from pathlib import Path
import json,numpy as np
B=Path(__file__).resolve().parents[1]
for key in ['main','roof']:
 a=np.load(B/'work'/f'seal-{key}-boundary.npz');v=a['vertices'];f=a['faces'];edges=a['boundaryEdges'];iset=set(map(tuple,edges.tolist()));directed=[]
 for fpart in [f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]:
  for i,j in fpart:
   if tuple(sorted((int(i),int(j)))) in iset:directed.append((int(i),int(j)))
 remaining=set(directed);out={}
 for i,j in directed:out.setdefault(i,[]).append(j)
 loops=[]
 while remaining:
  first=min(remaining);i,j=first;loop=[i];remaining.remove(first)
  while j!=loop[0]:
   loop.append(j);nexts=[k for k in out.get(j,[]) if (j,k) in remaining]
   if not nexts:break
   if len(nexts)==1:k=nexts[0]
   else:
    # Trace the sharpest right turn through the projected rim, separating pinched holes.
    incoming=v[j,:2]-v[i,:2]
    def turn(k):
     outgoing=v[k,:2]-v[j,:2]
     return np.arctan2(incoming[0]*outgoing[1]-incoming[1]*outgoing[0],incoming@outgoing)
    k=min(nexts,key=turn)
   remaining.remove((j,k));i,j=j,k
  p=v[loop];area=float(.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))
  loops.append({'vertices':loop,'closed':j==loop[0],'area':area,'count':len(loop),'min':p.min(0).tolist(),'max':p.max(0).tolist()})
 loops.sort(key=lambda l:-abs(l['area']));(B/'work'/f'seal-{key}-loops.json').write_text(json.dumps(loops))
 print(key,[(len(l['vertices']),round(l['area'],6),l['closed'],round(l['min'][2],4)) for l in loops],flush=True)


import numpy as np,json,sys
from pathlib import Path
from scipy.spatial import cKDTree
from PIL import Image
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from register_scans import obj_data
ma=np.load(B/'work/seal-main-boundary.npz');ra=np.load(B/'work/seal-roof-boundary.npz')
ml=json.load(open(B/'work/seal-main-loops.json'));rl=json.load(open(B/'work/seal-roof-loops.json'))
A=ma['vertices'][ml[0]['vertices']][::-1];R=ra['vertices'][rl[0]['vertices']]
# Start at the nearest pair and preserve cyclic boundary order.
d,idx=cKDTree(R).query(A);i=d.argmin();j=idx[i];A=np.roll(A,-i,axis=0);R=np.roll(R,-j,axis=0);na,nr=len(A),len(R)
aa=np.vstack([A,A[0]]);rr=np.vstack([R,R[0]])
# Minimum-cost zipper: every original boundary edge receives exactly one incident patch face.
cost=np.full((na+1,nr+1),np.inf);step=np.zeros((na+1,nr+1),np.uint8);cost[0,0]=0
for i in range(na+1):
 for j in range(nr+1):
  if i==0 and j==0:continue
  length=np.linalg.norm(aa[i]-rr[j]);penalty=length*length+1e-6
  left=cost[i-1,j] if i else np.inf;down=cost[i,j-1] if j else np.inf
  if left<down:cost[i,j]=left+penalty;step[i,j]=1
  else:cost[i,j]=down+penalty;step[i,j]=2
v=list(np.vstack([A,R]));faces=[];i,j=na,nr
while i or j:
 if step[i,j]==1:faces.append([(i-1)%na,i%na,na+j%nr]);i-=1
 else:faces.append([i%na,na+j%nr,na+(j-1)%nr]);j-=1
# Close only upper-region small capture loops, never the artificial crop boundaries.
small=[]
for loop in ml[1:]:
 if loop['min'][2]<2.3:continue
 p=ma['vertices'][loop['vertices']][::-1];base=len(v);v.extend(p);center=len(v);v.append(p.mean(0))
 for k in range(len(p)):faces.append([base+k,base+(k+1)%len(p),center])
 small.append(len(p))
v=np.array(v);faces=np.array(faces,dtype=int)
# Add interior samples for a textured appearance without subdividing captured boundary edges.
verts=list(v);pending=[(f,0) for f in faces];final=[]
while pending:
 f,depth=pending.pop();p=np.array([verts[k] for k in f]);area=np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))*.5
 if area>1e-5 and depth<5:
  c=len(verts);verts.append(p.mean(0))
  pending.extend([(np.array([f[k],f[(k+1)%3],c]),depth+1) for k in range(3)])
 else:final.append(f)
v=np.array(verts);faces=np.array(final)
# Sample adjacent captured texture colors, blending across the narrow repaired strip.
source=[];color=[]
for key in ['main','roof']:
 a=np.load(B/'work'/f'seal-{key}.npz');tri=a['vertices'][a['faces']];centers=tri.mean(1);uv=a['uv'].mean(1);mid=a['materials'];pixels=np.zeros((len(tri),3))
 paths=[t['image'] for t in json.load(open(B/'reports/raw-mesh.json'))[0]['textures']] if key=='main' else obj_data('upper-stairs')[-1]
 for m in np.unique(mid):
  im=np.asarray(Image.open(paths[m]).convert('RGB'));h,w=im.shape[:2];sel=mid==m;xx=np.clip((uv[sel,0]*w).astype(int),0,w-1);yy=np.clip(((1-uv[sel,1])*h).astype(int),0,h-1);pixels[sel]=im[yy,xx]/255
 # Ignore remaining sky/dark green background fringe when choosing fill colors.
 stone=(pixels[:,0]>pixels[:,2]*1.03)&(pixels[:,0]>pixels[:,1]*.98)&(pixels[:,0]>.16)
 source.append(centers[stone]);color.append(pixels[stone])
source=np.concatenate(source);color=np.concatenate(color);dist,ids=cKDTree(source).query(v,k=4);weights=1/np.maximum(dist,1e-4)**2;rgb=(color[ids]*weights[:,:,None]).sum(1)/weights.sum(1)[:,None]
rgb=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
np.savez(B/'work/seal-patch.npz',vertices=v,faces=faces,colors=rgb)
# Check all upper boundary edges are now closed after welding coincident positions.
vv=np.vstack([ma['vertices'],ra['vertices'],v]);ff=np.vstack([ma['faces'],ra['faces']+len(ma['vertices']),faces+len(ma['vertices'])+len(ra['vertices'])]);u,inv=np.unique(np.round(vv,6),axis=0,return_inverse=True);ff=inv[ff];edges=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);ee,cc=np.unique(edges,axis=0,return_counts=True);boundary=ee[cc==1];upper=boundary[np.all(u[boundary,2]>2.3,axis=1)]
report={'roofBoundaryEdgesBridged':nr,'gateRimBoundaryEdgesBridged':na,'smallUpperCaptureLoopsFilled':len(small),'patchTriangles':len(faces),'remainingUpperBoundaryEdges':len(upper),'nonmanifoldEdgesInUpperRegion':int(((cc>2)&np.all(u[ee,2]>2.3,axis=1)).sum()),'maxBridgeDistance':float(np.max(np.linalg.norm(v[faces[:,0]]-v[faces[:,1]],axis=1))),'method':'Boundary-to-boundary triangle strips and local hole caps. Captured vertices and UVs are unchanged. Repair colors sampled from neighboring stone photographs; no inscriptions generated.'}
(B/'reports/roof-sealing.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert len(upper)==0
