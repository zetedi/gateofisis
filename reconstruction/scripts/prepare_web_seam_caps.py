import numpy as np,json
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components,dijkstra
B=Path(__file__).resolve().parents[1]
reports=[]
for key in ['high','standard']:
 a=np.load(B/'work'/f'web-{key}-geometry.npz');u,inv=np.unique(np.round(a['vertices'],7),axis=0,return_inverse=True);f=inv[a['faces']]
 region=(u[:,0]>-.25)&(u[:,0]<1.3)&(u[:,1]>-3)&(u[:,1]<-1.85)&(u[:,2]>2.3)&(u[:,2]<2.8)
 ids=np.flatnonzero(region);parent=np.arange(len(u))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,j in cKDTree(u[ids]).query_pairs(.00004,output_type='ndarray'):
  parent[root(ids[j])]=root(ids[i])
 for i in ids:parent[i]=root(i)
 f=parent[f];f=f[(f[:,0]!=f[:,1])&(f[:,1]!=f[:,2])&(f[:,0]!=f[:,2])]
 e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);ee,cc=np.unique(e,axis=0,return_counts=True);boundary=ee[(cc==1)&np.all(region[ee],axis=1)]
 _,labels=connected_components(coo_matrix((np.ones(len(boundary)),(boundary[:,0],boundary[:,1])),shape=(len(u),len(u))),directed=False)
 interior=ee[(cc>1)&np.all(region[ee],axis=1)];length=np.linalg.norm(u[interior[:,0]]-u[interior[:,1]],axis=1)
 graph=coo_matrix((np.tile(length,2),(np.r_[interior[:,0],interior[:,1]],np.r_[interior[:,1],interior[:,0]])),shape=(len(u),len(u))).tocsr()
 newv=list(u);newf=[];details=[]
 for cid in np.unique(labels[boundary[:,0]]):
  edges=boundary[labels[boundary[:,0]]==cid].tolist();verts=np.unique(edges);degree=np.bincount(np.array(edges).ravel(),minlength=len(u));odd=list(verts[degree[verts]%2==1]);initial=len(edges)
  while odd:
   start=odd.pop();distance,predecessor=dijkstra(graph,indices=start,return_predecessors=True)
   finish=min(odd,key=lambda k:distance[k]);assert distance[finish]<.15,(key,cid,distance[finish]);odd.remove(finish)
   current=finish
   while current!=start:
    previous=int(predecessor[current]);assert previous>=0;edges.append([current,previous]);current=previous
  verts=np.unique(edges);center=len(newv);newv.append(u[verts].mean(0))
  for x,y in edges:newf.append([x,y,center])
  details.append({'boundaryEdges':initial,'addedFaces':len(edges),'span':np.ptp(u[verts],axis=0).tolist()})
 newv=np.array(newv);newf=np.array(newf,dtype=int)
 joined=np.vstack([f,newf]);edges=np.sort(np.concatenate([joined[:,[0,1]],joined[:,[1,2]],joined[:,[2,0]]]),axis=1);edges,count=np.unique(edges,axis=0,return_counts=True);openedges=edges[count==1];pos=newv[openedges];remaining=np.all((pos[:,:,0]>-.25)&(pos[:,:,0]<1.3)&(pos[:,:,1]>-3)&(pos[:,:,1]<-1.85)&(pos[:,:,2]>2.3)&(pos[:,:,2]<2.8),axis=1).sum();assert remaining==0,(key,remaining)
 used,inv=np.unique(newf,return_inverse=True);np.savez(B/'work'/f'web-{key}-microcaps.npz',vertices=newv[used],faces=inv.reshape(-1,3))
 report={'quality':key,'capturedBoundaryEdgesClosed':len(boundary),'microcapFaces':len(newf),'remainingRoofOpenEdges':int(remaining),'components':details};reports.append(report);print(key,len(boundary),len(newf),len(details),flush=True)
(B/'reports/web-seam-caps.json').write_text(json.dumps(reports,indent=2))
