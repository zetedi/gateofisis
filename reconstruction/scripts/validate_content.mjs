import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFile, stat } from 'node:fs/promises'
import * as en from '../../src/content.js'
import * as ar from '../../src/content.ar.js'

// The French standalone article “Les” is incorporated into the Arabic title.
// A translation must preserve every chapter, source, scene, caption and paragraph.
function sameShape(original, translation, path = 'content') {
  assert.ok(translation !== undefined, `${path} missing in Arabic`)
  if (Array.isArray(original)) {
    assert.equal(translation.length, original.length, `${path} length differs`)
    original.forEach((v, i) => sameShape(v, translation[i], `${path}[${i}]`))
  } else if (original && typeof original === 'object') {
    Object.entries(original).forEach(([k, v]) =>
      sameShape(v, translation[k], `${path}.${k}`),
    )
  } else if (typeof original === 'string')
    assert.ok(
      typeof translation === 'string' && (original.length === 0 || translation.length > 0 || path === 'content.TITLE_PAGE.les'),
      `${path} empty`,
    )
}
sameShape(en, ar)
const arabicText = JSON.stringify(ar).normalize('NFD').replace(/[\u064B-\u065F]/g,'')
assert.ok(!arabicText.includes('الحسة'),'Incorrect Heissa spelling returned')
assert.equal((arabicText.match(/هيصة/g)||[]).length,3,'Heissa must appear in both introduction mentions and the plate caption')
assert.deepEqual(
  en.NAV.map((x) => x[0]),
  ar.NAV.map((x) => x[0]),
)
for (const plate of [...en.PLATES, { id: 'plate-01-plan' }])
  await stat(`public/plates/${plate.id}.jpg`)
const photos = JSON.parse(
  await readFile('public/survey/photographs.json', 'utf8'),
)
for (const photo of photos) {
  assert.ok(photo.titleAr && photo.dateAr)
  assert.equal(createHash('sha256').update(await readFile(`public/${photo.image}`)).digest('hex'),photo.sha256,'Original photograph changed')
  await stat(`public/${photo.thumbnail}`)
}
const detail = JSON.parse(
  await readFile('public/models/detail/gate-detail.gltf', 'utf8'),
)
assert.equal(detail.images.length, 11)
for (const image of detail.images) {
  const bytes = await readFile(`public/models/detail/${image.uri}`)
  assert.deepEqual(
    [...bytes.subarray(0, 12)],
    [171, 75, 84, 88, 32, 50, 48, 187, 13, 10, 26, 10],
    'KTX2 magic',
  )
  assert.equal(bytes.readUInt32LE(20), 8192, 'Native atlas width')
  assert.equal(bytes.readUInt32LE(24), 8192, 'Native atlas height')
}
assert.equal(
  detail.meshes.reduce(
    (total, m) =>
      total +
      m.primitives.reduce(
        (sum, p) => sum + detail.accessors[p.indices].count / 3,
        0,
      ),
    0,
  ),
  5049392,
)
console.log(
  'English/Arabic structure complete; all plates and photos resolve; eleven 8K KTX2 atlases and 5,049,392 triangles verified.',
)
