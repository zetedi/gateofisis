import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Served from https://zetedi.github.io/gateofisis/ on GitHub Pages.
export default defineConfig({
  base: process.env.VITE_BASE ?? '/gateofisis/',
  plugins: [react(), tailwindcss()],
})
