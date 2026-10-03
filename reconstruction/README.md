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

No surveyed control distances, ground-control points, or independent scale checks were supplied. The photographic reconstruction has relative scale and must not be used as a validated metric survey. The two supporting Polycam similarities have scale factors around 0.30, but this alone does not establish survey-grade dimensions. No hypothetical restoration or generated architectural detail is included.

## Reproduction

Use Python with `numpy scipy pillow rawpy opencv-python-headless`, Blender 5.1, and Swift/RealityKit on a supported Mac. Run from the repository root. Source images are never uploaded.

1. `reports/photo-inventory.json` records SHA-256 deduplication and source paths. `scripts/prepare_photos.py` stages the unique images and develops RAWs.
2. Compile `scripts/reconstruct.swift` with `swiftc -parse-as-library`; run it with the staged photo folder and an output folder. Checkpoints, camera poses, the sparse cloud, and USDZ outputs are retained in `output/photogrammetry`.
3. `scripts/clean_polycam.py` cleans the supplied scans; `scripts/export_polycam.py` runs inside Blender to save source models and the packed archive.
4. `scripts/extract_reconstruction.py` runs inside Blender to preserve RAW geometry, atlases, and an unedited packed master. `scripts/register_scans.py` estimates supporting scan registration.
5. Run `scripts/analyze_components.py` with the reconstruction Python environment to generate `work/raw-components.npy`. `scripts/clean_reconstruction.py` runs inside Blender and uses those connected-component labels and the documented crop to save the clean master.
6. `scripts/export_site.py` finalizes the master with named reference scenes and derives standard/high web resolutions. The master is saved **before** web decimation and texture reduction.
7. `node reconstruction/scripts/validate_models.mjs` runs the Khronos glTF validator on the published models. `npm run lint` and `npm run build` check the website.

Relevant primary documentation: [Apple Object Capture](https://developer.apple.com/documentation/realitykit/photogrammetrysession), [Blender USD](https://docs.blender.org/manual/en/latest/files/import_export/usd.html), [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator).
