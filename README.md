# The Gate of Isis · Bîgeh

A single-page React + Tailwind CSS presentation of the pylon gate-way of the Temple of Bîgeh
(island of Bîgeh, First Cataract, Aswan), designed after the typography of

> Aylward M. Blackman, *The Temple of Bîgeh* (Les Temples immergés de la Nubie),
> Le Caire: Imprimerie de l'Institut français d'archéologie orientale, 1915.

## Sourcing rule

Every sentence of prose on the page is quoted verbatim from a published source and is
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

## Deployment

Pushes to `main` build and deploy the site to GitHub Pages via
`.github/workflows/deploy.yml`: https://zetedi.github.io/gateofisis/
