"""Publish sealed model metadata and retire obsolete web derivatives."""
import json
from pathlib import Path
B=Path(__file__).resolve().parents[1];P=B.parent/'public/models'
site=json.loads((B/'reports/site-export.json').read_text());high,quick=site
a=P/'complete-site.glb';b=P/'complete-site-sealed.glb'
if a.exists():a.replace(b)
quick['file']='complete-site-sealed.glb';(B/'reports/site-export.json').write_text(json.dumps(site,indent=2))
detail=json.loads((B/'reports/detail-export.json').read_text())
survey=json.loads((P/'survey.json').read_text());model=survey['models'][0]
model.update(file='models/complete-site-sealed.glb',highFile='models/high/complete-site-high.gltf',
             detailFile='models/detail/gate-detail-sealed.gltf',bytes=quick['bytes'],highBytes=high['bytes'],
             detailBytes=detail['totalBytes'],detailTriangles=detail['triangles'],
             downloadFile='models/complete-site-sealed.glb',downloadBytes=quick['bytes'],
             roofFocus=[.53,2.48,2.40],subtitle='Gate and roof, together',
             description='The gate, aligned roof, approach stairs, pavement, columns and surrounding stones in one assembled model. Roof seams and small upper capture holes are sealed.',
             note='1,054 aligned photographs · Roof joined and scan gaps repaired · Choose Original detail for the captured gate geometry and 8K textures.')
roof=survey['models'][3]
roof.update(subtitle='Original roof reference',description='The original separately captured roof, retained for comparison. Its aligned counterpart is included in the complete site.',
            note='Original roof capture. Choose The complete site to see the aligned roof with its seams sealed.')
survey.update(masterTriangles=12808221,masterTextureAtlases=12,
              masterFile='Gate-of-Isis-Sealed.blend',roofAssembly='Aligned to the upper rim using the matching stone joint; captured roof geometry retained.',
              repairs={'roofBoundaryEdgesBridged':1011,'gateBoundaryEdgesBridged':1085,'smallCaptureHolesFilled':44,'upperOpenBoundaryEdges':0,'interpolatedRepairTriangles':19593},
              method='The gate and surrounding stones were reconstructed from 1,054 aligned photographs. The separately captured Polycam roof is aligned and included in every detail level. Roof seams and small upper capture holes are closed with identifiable repair surfaces in the Blender master. Original detail retains captured gate geometry, eleven original 8K atlases and the native roof texture.',
              limitation='The gap-closing surfaces are interpolated repairs, not measured archaeological detail. Their colors come from neighboring captured stone; no inscriptions were generated. The doorway and outer terrain capture edges remain open. Dimensions have not been checked against survey control.')
(P/'survey.json').write_text(json.dumps(survey,indent=2,ensure_ascii=False)+'\n')
old=P/'complete-site-high.glb'
if old.exists():old.unlink()
print('SEALED WEB METADATA',quick['bytes'],high['bytes'],detail['totalBytes'])
