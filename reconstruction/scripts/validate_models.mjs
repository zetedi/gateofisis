import { readFile, writeFile, stat } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import validator from 'gltf-validator'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const survey = JSON.parse(await readFile(path.join(root, 'public/models/survey.json'), 'utf8'))
const reports = []
for (const model of survey.models) {
  for (const file of [model.file, model.highFile, model.detailFile].filter(Boolean)) {
    const bytes = await readFile(path.join(root, 'public', file))
    const report = await validator.validateBytes(new Uint8Array(bytes), { uri: file, maxIssues: 30, externalResourceFunction: async uri => new Uint8Array(await readFile(path.join(root, 'public', path.dirname(file), uri))) })
    const gltf = file.endsWith('.gltf') ? JSON.parse(bytes.toString()) : JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString())
    const triangles = gltf.meshes.reduce((sum, mesh) => sum + mesh.primitives.reduce((total, primitive) => total + gltf.accessors[primitive.indices].count / 3, 0), 0)
    const summary = { file, bytes: (await stat(path.join(root, 'public', file))).size, triangles, errors: report.issues.numErrors, warnings: report.issues.numWarnings, messages: report.issues.messages }
    reports.push(summary)
    console.log(`${file}: ${triangles.toLocaleString('en')} triangles; ${summary.errors} errors; ${summary.warnings} warnings`)
    if (summary.errors) process.exitCode = 1
  }
}
await writeFile(path.join(root, 'reconstruction/reports/model-validation.json'), JSON.stringify(reports, null, 2))
