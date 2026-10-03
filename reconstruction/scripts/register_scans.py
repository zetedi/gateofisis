"""Match texture keypoints with their 3D surface coordinates; fit robust similarities."""
from pathlib import Path
import json, cv2, numpy as np
BASE=Path(__file__).resolve().parents[1]
cv2.setNumThreads(4)

def obj_data(key):
    folder=BASE/'work/polycam-clean'/key
    materials={};name=None
    for l in (folder/'28_9_2026.mtl').read_text().splitlines():
        if l.startswith('newmtl '):name=l[7:]
        if l.startswith('map_Kd '):materials[name]=folder/l[7:]
    names=list(materials);v=[];uv=[];faces=[];uvf=[];mid=[];material=0
    for l in (folder/'28_9_2026.obj').read_text().splitlines():
        p=l.split()
        if not p:continue
        if p[0]=='v':v.append(list(map(float,p[1:4])))
        elif p[0]=='vt':uv.append(list(map(float,p[1:3])))
        elif p[0]=='usemtl':material=names.index(p[1])
        elif p[0]=='f':
            tokens=[t.split('/') for t in p[1:]]
            faces.append([int(t[0])-1 for t in tokens]);uvf.append([int(t[1])-1 for t in tokens]);mid.append(material)
    v=np.array(v,dtype=np.float32)
    # OBJ is Y-up; use the same Blender Z-up coordinates as the reconstruction.
    v=v[:,[0,2,1]];v[:,1]*=-1
    return v,np.array(faces),np.array(uv)[np.array(uvf)],np.array(mid),list(materials.values())

def features(key,v,f,uv,mid,images):
    target=BASE/'work'/f'features-{key}.npz'
    if target.exists():return dict(np.load(target))
    pts=[];descriptors=[]
    for material,imgpath in enumerate(images):
        img=cv2.imread(str(imgpath));height,width=img.shape[:2]
        # At most 4096 pixels per atlas for matching; source geometry is unmodified.
        factor=min(1,4096/max(width,height))
        if factor<1:img=cv2.resize(img,None,fx=factor,fy=factor)
        h,w=img.shape[:2]
        atlas=np.zeros((h,w),dtype=np.int32)
        ids=np.flatnonzero(mid==material)
        pixels=uv[ids]*np.array([w,-h])+np.array([0,h])
        for j,poly in zip(ids,np.round(pixels).astype(np.int32)):
            cv2.fillConvexPoly(atlas,poly,int(j)+1)
        sift=cv2.SIFT_create(nfeatures=25000,contrastThreshold=.025)
        kp,desc=sift.detectAndCompute(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY),None)
        positions=np.array([k.pt for k in kp]);ipos=np.floor(positions).astype(int)
        faceids=atlas[np.clip(ipos[:,1],0,h-1),np.clip(ipos[:,0],0,w-1)]-1
        valid=faceids>=0;positions=positions[valid];faceids=faceids[valid];desc=desc[valid]
        tex=positions/np.array([w,-h])+np.array([0,1])
        tri=uv[faceids];a=tri[:,1]-tri[:,0];b=tri[:,2]-tri[:,0];c=tex-tri[:,0]
        det=a[:,0]*b[:,1]-a[:,1]*b[:,0]
        safe=np.abs(det)>1e-12
        u=(c[:,0]*b[:,1]-c[:,1]*b[:,0])/np.where(safe,det,1)
        z=(a[:,0]*c[:,1]-a[:,1]*c[:,0])/np.where(safe,det,1)
        valid=safe&(u>=-.02)&(z>=-.02)&(u+z<=1.02)
        xyz=v[f[faceids]]
        coords=xyz[:,0]+u[:,None]*(xyz[:,1]-xyz[:,0])+z[:,None]*(xyz[:,2]-xyz[:,0])
        pts.append(coords[valid]);descriptors.append(desc[valid])
        print(key,material,len(coords[valid]),flush=True)
    result={'points':np.concatenate(pts),'descriptors':np.concatenate(descriptors)}
    np.savez(target,**result);return result

def similarity(a,b):
    ac=a.mean(0);bc=b.mean(0);x=a-ac;y=b-bc
    u,s,vt=np.linalg.svd(x.T@y)
    d=np.ones(3);d[-1]=np.linalg.det(u@vt)
    rot=(u@np.diag(d)@vt).T
    scale=(s*d).sum()/(x*x).sum()
    t=bc-scale*rot@ac
    return scale,rot,t

def register(source,target):
    matcher=cv2.FlannBasedMatcher(dict(algorithm=1,trees=5),dict(checks=96))
    matches=matcher.knnMatch(source['descriptors'],target['descriptors'],k=2)
    good=[a for a,b in matches if a.distance<.7*b.distance]
    a=np.array([source['points'][m.queryIdx] for m in good]);b=np.array([target['points'][m.trainIdx] for m in good])
    print('Candidate matches',len(a),flush=True)
    if len(a)<4:return {'status':'insufficient matches','matches':len(a)}
    rng=np.random.default_rng(42);best=np.zeros(len(a),bool)
    for _ in range(15000):
        ix=rng.choice(len(a),3,replace=False)
        s,r,t=similarity(a[ix],b[ix])
        if not .1<s<3:continue
        err=np.linalg.norm(a@(s*r).T+t-b,axis=1)
        inliers=err<.045
        if inliers.sum()>best.sum():best=inliers
    for _ in range(5):
        s,r,t=similarity(a[best],b[best]);err=np.linalg.norm(a@(s*r).T+t-b,axis=1);best=err<.045
    matrix=np.eye(4);matrix[:3,:3]=s*r;matrix[:3,3]=t
    return {'status':'estimated' if best.sum()>=8 else 'insufficient inliers','matches':len(a),'inliers':int(best.sum()),'rmse':float(np.sqrt((err[best]**2).mean())),'scale':float(s),'matrix':matrix.tolist(),'sourcePoints':a[best].tolist(),'targetPoints':b[best].tolist()}

if __name__=='__main__':
    data=np.load(BASE/'work/raw-mesh-0.npz');info=json.loads((BASE/'reports/raw-mesh.json').read_text())[0]
    target=features('photogrammetry',data['vertices'],data['faces'],data['uv'],data['materials'],[t['image'] for t in info['textures']])
    results={}
    for key in ['site-b','site-a','upper-stairs']:
        source=features(key,*obj_data(key))
        results[key]=register(source,target)
        print(key,results[key]['status'],results[key].get('inliers'),flush=True)
        (BASE/'reports/registration.json').write_text(json.dumps(results,indent=2))
