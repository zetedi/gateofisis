# The Gate of Isis · Bîgeh

A React + Tailwind CSS presentation of the pylon gate-way of the Temple of Bîgeh
(island of Bîgeh, First Cataract, Aswan), designed after the typography of

> Aylward M. Blackman, *The Temple of Bîgeh* (Les Temples immergés de la Nubie),
> Le Caire: Imprimerie de l'Institut français d'archéologie orientale, 1915.

## Sourcing rule

Every sentence of historical prose in the **Book** is quoted verbatim from a published source and is
followed by a citation link. No text was written for the site itself except headings,
navigation labels, and the short editorial notes marked in italics. The sources are:

- Blackman 1915 (public domain; scan at https://archive.org/details/templeofbgeh00blac),
  including the contributions of F. Ll. Griffith (Demotic graffiti) and A. S. Hunt (Greek inscription).
- Wikipedia, "Bigeh" and "Philae" (CC BY-SA 4.0).
- Isma'il Kushkush, "When Isis Was Queen", *Archaeology*, Nov/Dec 2021.

All quotations live in `src/content.js`, each with a `source` key resolving to `SOURCES`.

## Plates

`public/plates/` holds the heliogravure plates and the ground-plan, cropped from the scan of
the 1915 volume (`The temple of Bîgeh.pdf`). Captions are quoted from Blackman's List of Plates.

## Run

```sh
npm install
npm run dev      # http://localhost:5173/gateofisis/
npm run build    # production bundle in dist/
```

## Stack

Vite 8, React 19, Tailwind CSS 4 (`@tailwindcss/vite`). Fonts: Bodoni Moda (display) and
Old Standard TT (text) from Google Fonts.

## 3D survey

The main navigation has **The Book** (with the original chapter submenu) and **The Gate · 3D**.
Open `/gateofisis/#3d` for the complete photographic reconstruction: gate, approach,
columns, pavement and surrounding stones in one model. Three cleaned supporting
Polycam captures remain available as references, including the correctly labeled top of the gate.

The Three.js viewer loads only on the 3D page. It supports standard/high detail,
photographic/stone/mesh surfaces, camera presets, orbit/pan/zoom, keyboard controls,
fullscreen, model downloads and enlarged field photographs. The book's quotations
and plates remain unchanged; the 3D page uses editorial survey descriptions.
The opening camera centers the gate and approach stairs; **Whole site** restores the
complete surroundings. Larger, darker interface text and stronger display typography
keep the survey readable on desktop and mobile.

The packed Blender master is `reconstruction/output/Gate-of-Isis.blend`.
See [reconstruction/README.md](reconstruction/README.md) for methods, fidelity,
registration limitations, artifact paths and reproducibility. Validate web exports with
`node reconstruction/scripts/validate_models.mjs`.

## Deployment

Pushes to `main` build and deploy the site to GitHub Pages via
`.github/workflows/deploy.yml`: https://zetedi.github.io/gateofisis/
