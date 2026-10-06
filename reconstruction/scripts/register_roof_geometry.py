"""Investigate roof registration; results are candidates, not a validated fusion.

Run with the reconstruction Python environment after extract_reconstruction.py.
See reports/roof-registration.json for independent checks and visual limitations.
The source mesh, main Blender master and public website are not modified.
"""
import numpy as np,json
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pathlib import Path
B=Path(__file__).resolve().parents[1]

def prepare_surfaces():
    """Recreate local fitting caches from captured meshes, preserving their coordinates."""
    from register_scans import obj_data
    v,f,*_=obj_data('upper-stairs')
    for name in ['source','target']:
        if name=='target':
            raw=np.load(B/'work/raw-mesh-0.npz')
            v=raw['vertices'];f=raw['faces']
            mask=(v[:,0]>-.3)&(v[:,0]<1.4)&(v[:,1]>-3)&(v[:,1]<-1.9)&(v[:,2]>2.25)
            f=f[np.all(mask[f],axis=1)]
        tri=v[f]
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-10)
        np.savez(B/'work'/f'roof-{name}.npz',points=tri.mean(1),normals=normals)

if not all((B/'work'/f'roof-{name}.npz').exists() for name in ['source','target']):
    prepare_surfaces()
a=np.load(B/'work/roof-source.npz');b=np.load(B/'work/roof-target.npz')
# Exclude the floating fragment and restrict comparison to surviving vertical faces.
sel=(a['points'][:,2]>.05)&(np.abs(a['normals'][:,2])<.8)
p=a['points'][sel];n=a['normals'][sel]
rng=np.random.default_rng(314);ids=rng.choice(len(p),min(6000,len(p)),False);p=p[ids];n=n[ids]
sel=(b['points'][:,2]<2.65)&(np.abs(b['normals'][:,2])<.85)
q=b['points'][sel];qn=b['normals'][sel];tree=cKDTree(q)
print('matching vertical faces',len(p),len(q),flush=True)
results=[]
for yaw in [80,90,100,-100,-90,-80]:
 for z in [2.36,2.40,2.44]:
  r=Rotation.from_euler('z',yaw,degrees=True).as_matrix();s=.30;t=np.array([.53,-2.40,z])
  for it in range(35):
   x=p@(s*r).T+t;nn=n@r.T;dist,j=tree.query(x,k=12,workers=4)
   dots=np.einsum('ik,ijk->ij',nn,qn[j]);dist=np.where(dots>.75,dist,np.inf);which=dist.argmin(1);d=dist[np.arange(len(x)),which];j=j[np.arange(len(x)),which]
   ok=d<(.085 if it<10 else .045)
   if ok.sum()<60:break
   xx=x[ok];qq=q[j[ok]];norm=qn[j[ok]]
   # Point-to-plane incremental fit; positive normal agreement prevents aligning to the ceiling underside.
   def residual(par):
    rr=Rotation.from_rotvec(par[:3]).as_matrix();v=xx@rr.T*np.exp(par[6])+par[3:6]
    return np.r_[np.einsum('ij,ij->i',v-qq,norm),par[6]*2]
   fit=least_squares(residual,np.zeros(7),loss='soft_l1',f_scale=.008,max_nfev=15)
   rr=Rotation.from_rotvec(fit.x[:3]).as_matrix();ss=np.exp(fit.x[6]);s*=ss;r=rr@r;t=ss*rr@t+fit.x[3:6]
   if not .275<s<.325:break
   if np.linalg.norm(fit.x)<1e-6:break
  x=p@(s*r).T+t;nn=n@r.T;dist,j=tree.query(x,k=12,workers=4);dots=np.einsum('ik,ijk->ij',nn,qn[j]);dist=np.where(dots>.75,dist,np.inf);which=dist.argmin(1);d=dist[np.arange(len(x)),which];j=j[np.arange(len(x)),which];ok=d<.035
  matrix=np.eye(4);matrix[:3,:3]=s*r;matrix[:3,3]=t
  result={'initialYaw':yaw,'initialZ':z,'scale':s,'rotationDegrees':Rotation.from_matrix(r).as_euler('xyz',degrees=True).tolist(),'translation':t.tolist(),'correspondences':int(ok.sum()),'testedSourcePoints':len(p),'medianDistance':float(np.median(d[ok])) if ok.any() else None,'sourceSpread':np.ptp(p[ok],axis=0).tolist() if ok.any() else [],'matrix':matrix.tolist()}
  print({k:v for k,v in result.items() if k!='matrix'},flush=True);results.append(result)
(B/'reports/roof-geometry-trials.json').write_text(json.dumps(results,indent=2))

# Retain a reproducible candidate near the scale established by the other captures.
plausible=[r for r in results if .29<r['scale']<.31]
if not plausible:
    raise RuntimeError('No candidate near the independently estimated scan scale')
candidate=max(plausible,key=lambda r:r['correspondences'])
(B/'work/roof-candidate.json').write_text(json.dumps(candidate,indent=2))
