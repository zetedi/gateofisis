# Gate of Isis — photographic reconstruction

## Deliverables

- `output/Gate-of-Isis.blend`: cleaned, full-detail photographic reconstruction of the gate **and surrounding site together**. Supporting Polycam captures are additional named reference scenes. Textures are packed.
- `output/Gate-of-Isis-Raw.blend`: unedited reconstruction retained for traceability.
- `output/Gate-of-Isis-Polycam-Archive.blend`: cleaned source scans with original texture resolution.
- `../public/models/complete-site.glb`: standard web derivative.
- `../public/models/complete-site-high.glb`: high-detail web derivative.

Large intermediates, original source ZIPs, Blender masters, source-photo inventories and diagnostic images are local artifacts, excluded from Git. The website's GLBs are included in `public/models` and do not require a reconstruction tool at runtime. Processing scripts and the cleanup, registration and validation reports are versioned alongside the website.

## Input and reconstruction

The supplied `01_Foto` collection contains 1,987 files: 1,849 JPEGs and 138 Canon CR2 RAWs. SHA-256 deduplication identified 1,070 unique photographs. Fifteen photographs in `Others` folders were excluded; 1,055 were submitted. RAWs were developed with LibRaw/rawpy using camera white balance, no automatic exposure brightening, and JPEG quality 98 with no chroma subsampling. The original files were not modified.

RealityKit Object Capture ran locally on this Mac with unordered samples, high feature sensitivity, object masking disabled, and the bounding-box restriction disabled. It registered **1,054 cameras**, skipping sample 1024, and produced **472,736 sparse points**. The raw dense reconstruction has **13,058,793 triangles**, 6,531,283 vertices, and **eleven 8192 × 8192 diffuse texture atlases**. Both RAW and reduced outputs completed successfully. Intermediate USD localization warnings did not prevent the final archives from containing their textures.

The main model is one photographic reconstruction; the gate, approach stairs, pavement, columned remains, and scattered stones share its coordinate frame. It is not a manual arrangement of the independent scans.

## Cleanup

Detached sky/capture fragments were removed. Incomplete background vegetation was trimmed with documented scene-space bounds (`clean_reconstruction.py`). The cleaned main mesh retains **12,699,647 triangles** and 6,351,193 vertices. Stone surfaces were not procedurally rebuilt, smoothed, or filled. Incomplete coverage and open edges remain visible. UV layer names and original atlas resolution were preserved in the Blender master.

In the Polycam gate scan, the blue-shirted figure and four suspended capture fragments were removed. Two incomplete human-shaped fragments were removed from the column-area scan. Cleanup operates on visually inspected connected components and does not move the remaining vertices or change their UVs. Face counts and component IDs are recorded in `reports/polycam-cleanup.json`. The original ZIPs remain untouched.

## Registration and limitations

SIFT texture features were mapped back to their 3D triangle surfaces through UV barycentric coordinates. Robust similarity fitting registered the gate source scan with 9 supporting matches (RMS residual 0.00235 reconstruction units), and the column-area scan with 19 matches (0.00546 units). These are internal fitting residuals, **not independently measured survey accuracy**.

`28_9_2026 2.zip` is the **top of the gate**, not the approach stairs. It did not produce enough consistent correspondences to validate registration. It remains a clearly labeled independent reference scene and website source model; it is not falsely fused into the main reconstruction. The photographic model therefore retains the capture gaps in the top surfaces.

### Roof registration follow-up · 6 October 2026

`output/Gate-of-Isis-Roof-Study.blend` contains the complete photographic site and
an editable roof scan placed above the gate. **This is a provisional inspection
study, not a validated stitch.** The archival master and published models are
unchanged. Four comparison renders are saved as `reports/roof-candidate-*.png`.

Eighteen geometric registration trials tested both roof orientations, several
starting heights and small changes in heading. Fitting used vertical faces and
same-facing normals to avoid matching the roof top to the ceiling underside.
The preferred orientation repeatedly approached a scale of 0.2991, consistent
with the other Polycam captures. Of 6,000 sampled vertical-face points, 1,444
fell within 0.035 reconstruction units; their median distance was 0.00481 units.
These selected fitting residuals do not establish accuracy for the whole roof.

The independent comparison against the already registered Polycam gate scan
supported only 7.9% of the roof's vertical faces at the same threshold. Guided
texture matching yielded only four distinct target features, insufficient for
validated landmarks. In the combined renders, captured ceiling geometry
intersects the roof's central recess; rim gaps and capture artifacts remain.
The vertical placement and seams therefore remain unresolved. No synthetic
stone, smoothing, welding or hole filling was used to conceal these problems.
The disconnected fragment below the roof was omitted from the study only.

`scripts/register_roof_geometry.py` reproduces the geometric trials from the
captured meshes. `scripts/export_roof_study.py`, run in Blender afterward, saves
the separate packed study and inspection renders. The decision and checks are
recorded in `reports/roof-registration.json`; all trial transforms are retained
in `reports/roof-geometry-trials.json`.

### Roof aligned to the rim · 6 October 2026

The later `output/Gate-of-Isis-Roof-Aligned.blend` applies the user's observation
that the stone joint already matches horizontally. A rigid correction raises
the roof by 0.03929 relative units at its centre and adjusts its tilt by
2.304° about X and −4.283° about Y. It retains the captured roof shape and
texture coordinates. Both ends, both oblique sides and the overhead view were
rendered and inspected. The earlier study remains available for comparison.

The median absolute height difference at 1,000 sampled rim comparisons drops
from approximately 0.057 to 0.010 reconstruction units. In a separate local
check, the roof is above all 36,980 sampled overlapping central-ceiling points;
the previous placement penetrated part of that sample. This is a visual
alignment with local checks, not an independently controlled metric survey.

The blue sky-colored capture strips along the join were inspected in diagnostic
renders and isolated as 8,854 original triangles in a hidden collection. Their
coordinates and UVs remain available, making the cleanup reversible. No new
stone surfaces, inscriptions, smoothing or hole filling were introduced.
Small residual scan-edge artifacts remain.

Run `prepare_roof_rim_alignment.py` in the reconstruction Python environment,
then `export_aligned_roof.py` in Blender. `validate_aligned_roof.py` compares
the retained stone coordinates, UVs and material assignments against the
earlier study and checks the roof transform and packed textures. Reports are
`roof-rim-alignment.json` and `roof-alignment-validation.json`. The aligned
Blender file is a local deliverable; the published website models are unchanged.

### Sealed presentation and website models · 7 October 2026

`output/Gate-of-Isis-Sealed.blend` includes the aligned roof and a separate,
editable repair mesh. The repair connects 1,011 roof boundary edges to 1,085
gate-rim edges and caps 44 small upper capture holes. The upper-region boundary
check reports zero remaining open edges. There are 14 multiple-face edge
junctions at pinched capture boundaries in the assembled full-detail mesh;
this is a presentation repair, not a certified manifold mesh for fabrication.
The doorway, real recesses and outer terrain capture boundary remain open.

The 19,593 repair triangles use colors sampled from adjacent captured stone.
They are explicitly interpolated surfaces, not new archaeological evidence.
No inscriptions were generated. The captured gate and roof coordinates, UVs
and transforms are unchanged, and all source textures are packed. The visible
master has 12,808,221 triangles. Earlier masters remain available separately.

All three website quality levels now use this assembly. The original-detail
view contains 4,740,539 native gate triangles, 299,999 context triangles, the
97,835-triangle roof and the repair mesh. Its eleven original 8K atlases are
reused unchanged, with the native 4096 × 2880 roof texture added. Lower-detail
web derivatives are welded before reduction and checked again for open upper
edges. Their tiny simplification gaps are capped in the exported presentation
mesh. A dedicated Roof view lets visitors inspect the result.

Reproduce with `extract_sealing_regions.py` in Blender,
`prepare_roof_sealing.py` in the reconstruction Python environment, and
`save_sealed_master.py` in Blender. `export_sealed_site.py` creates all web
derivatives. Run `inspect_web_roof.py` in Blender, `prepare_web_seam_caps.py`
in the reconstruction environment, then `apply_web_seam_caps.py` in Blender
to close tiny simplification gaps. Re-run `inspect_web_roof.py` and then
`validate_web_roof.py` to check the actual decoded exports.
`package_sealed_detail.py` reuses the native compressed atlases;
`finalize_sealed_web.py` updates public metadata after those checks pass. `validate_sealed_master.py`
checks the source meshes and packed textures. The numerical records are
`roof-sealing.json`, `sealed-master-validation.json` and `site-export.json`.

No surveyed control distances, ground-control points, or independent scale checks were supplied. The photographic reconstruction has relative scale and must not be used as a validated metric survey. The two supporting Polycam similarities have scale factors around 0.30, but this alone does not establish survey-grade dimensions. No hypothetical restoration or generated architectural detail is included.

## Reproduction

Use Python with `numpy scipy pillow rawpy opencv-python-headless`, Blender 5.1, and Swift/RealityKit on a supported Mac. Run from the repository root. Reconstruction runs locally. Eight selected original field photographs are published on the site for inspection; the supplied frontal photograph was also used with the image-generation tool for the separate illustrative hero sketch.

1. `reports/photo-inventory.json` records SHA-256 deduplication and source paths. `scripts/prepare_photos.py` stages the unique images and develops RAWs.
2. Compile `scripts/reconstruct.swift` with `swiftc -parse-as-library`; run it with the staged photo folder and an output folder. Checkpoints, camera poses, the sparse cloud, and USDZ outputs are retained in `output/photogrammetry`.
3. `scripts/clean_polycam.py` cleans the supplied scans; `scripts/export_polycam.py` runs inside Blender to save source models and the packed archive.
4. `scripts/extract_reconstruction.py` runs inside Blender to preserve RAW geometry, atlases, and an unedited packed master. `scripts/register_scans.py` estimates supporting scan registration.
5. Run `scripts/analyze_components.py` with the reconstruction Python environment to generate `work/raw-components.npy`. `scripts/clean_reconstruction.py` runs inside Blender and uses those connected-component labels and the documented crop to save the clean master.
6. `scripts/export_site.py` finalizes the master with named reference scenes and derives standard/high web resolutions. The master is saved **before** web decimation and texture reduction.
7. `node reconstruction/scripts/validate_models.mjs` runs the Khronos glTF validator on the published models. `npm run lint` and `npm run build` check the website.

Relevant primary documentation: [Apple Object Capture](https://developer.apple.com/documentation/realitykit/photogrammetrysession), [Blender USD](https://docs.blender.org/manual/en/latest/files/import_export/usd.html), [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator).

## Original detail in the browser · October 2026

`export_detail.py` reads the existing full-resolution Blender master, retains the
gate-region geometry and UVs (4,749,393 triangles), and reduces only the surrounding
context to 299,999 triangles. Both remain in their original common coordinate frame.
The exported glTF has 5,049,392 triangles. Draco uses 20-bit position and 18-bit UV
quantization; this is a compressed web derivative, not a new reconstruction.

`compress_detail.py` encodes all eleven original 8192 × 8192 atlases as KTX2 ETC1S
at quality 255, with sRGB mipmaps, using Basis Universal 2.50. This preserves atlas
resolution but is lossy texture compression. No carving, glyph or stone was generated
or sharpened artificially. The separate glTF, geometry buffer and textures total
169,461,632 bytes in `public/models/detail/`. The packed Blender master still keeps
the complete site at 12.7 million triangles and the original textures.

The optional Original detail view avoids forcing a 169 MB download on every visitor.
The Inscriptions camera faces the decorated reverse side; four dedicated full-resolution
field photos offer original-pixel inspection of the jambs, ceiling and inner wall.

Khronos validation reports no errors. The installed validator does not implement
KHR_texture_basisu or KHR_draco_mesh_compression and emits eleven MIME warnings for
image/ktx2. These are retained in the report, not suppressed. Additional checks verify
all KTX2 signatures, native atlas dimensions, texture references and triangle counts.
The complete model was decoded and visually inspected in Safari.

Primary references: [Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html),
[KTX2Loader](https://threejs.org/docs/pages/KTX2Loader.html),
[Basis Universal](https://github.com/BinomialLLC/basis_universal).
