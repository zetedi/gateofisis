import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import Icon from './Icons.jsx'

const assetUrl = (file) => `${import.meta.env.BASE_URL}${file}`

function disposeModel(root) {
  const geometries = new Set(), materials = new Set(), textures = new Set()
  root.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry)
    const all = [...(Array.isArray(object.material) ? object.material : [object.material]), ...(object.userData.viewerMaterials || [])]
    all.filter(Boolean).forEach((material) => {
      materials.add(material)
      Object.values(material).forEach((value) => { if (value?.isTexture) textures.add(value) })
    })
  })
  geometries.forEach((g) => g.dispose())
  materials.forEach((m) => m.dispose())
  textures.forEach((t) => { t.dispose(); t.source?.data?.close?.() })
}

async function fetchModel(url, signal, onProgress) {
  const response = await fetch(url, { signal })
  if (!response.ok) throw new Error(`Model download failed (${response.status})`)
  const total = Number(response.headers.get('content-length'))
  if (!response.body) return response.arrayBuffer()
  const reader = response.body.getReader()
  const chunks = []
  let received = 0
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    chunks.push(value)
    received += value.length
    onProgress(total ? Math.min(95, Math.round(received / total * 95)) : null)
  }
  const bytes = new Uint8Array(received)
  let position = 0
  chunks.forEach((chunk) => { bytes.set(chunk, position); position += chunk.length })
  return bytes.buffer
}

export default function ModelViewer({ model, mode, view, rotating, onRotateChange, onStats, onViewChange }) {
  const host = useRef(null)
  const frame = useRef(null)
  const api = useRef(null)
  const callbacks = useRef({ onStats, onRotateChange, onViewChange })
  const preferences = useRef({ mode, view, rotating })
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  const [fullscreen, setFullscreen] = useState(false)
  useLayoutEffect(() => {
    callbacks.current = { onStats, onRotateChange, onViewChange }
    preferences.current = { mode, view, rotating }
  }, [onStats, onRotateChange, onViewChange, mode, view, rotating])

  useEffect(() => {
    const container = host.current
    const abort = new AbortController()
    let destroyed = false, modelRoot, renderer, animation, dirty = true, visible = true, transition
    let extent = 10, fitDistance = 20, lastTime = 0
    const center = new THREE.Vector3()
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 1000)
    camera.position.set(12, 8, 16)
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' })
    } catch {
      // GPU support is only knowable when creating the renderer, after mounting.
      // oxlint-disable-next-line react/set-state-in-effect
      setError('Interactive 3D is unavailable in this browser. You can still explore the survey photographs below or download the model.')
      setLoading(false)
      return () => abort.abort()
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.setClearColor(0x000000, 0)
    renderer.domElement.tabIndex = 0
    renderer.domElement.setAttribute('aria-label', `${model.title}. Drag to orbit, scroll to zoom. Arrow keys rotate, plus and minus zoom, R resets the view.`)
    renderer.domElement.setAttribute('role', 'img')
    container.appendChild(renderer.domElement)
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.09
    controls.screenSpacePanning = true
    controls.autoRotateSpeed = 0.6
    controls.maxPolarAngle = Math.PI * 0.55
    controls.minPolarAngle = 0.02
    controls.addEventListener('change', () => { dirty = true })
    controls.addEventListener('start', () => {
      transition = null
      callbacks.current.onRotateChange(false)
      callbacks.current.onViewChange('free')
    })
    scene.add(new THREE.HemisphereLight(0xfff8eb, 0x757e72, 2.2))
    const light = new THREE.DirectionalLight(0xfff7e8, 3)
    light.position.set(10, 16, 10)
    scene.add(light)
    const fill = new THREE.DirectionalLight(0xc9d8e8, 1.2)
    fill.position.set(-12, 5, -7)
    scene.add(fill)

    function setMode(next) {
      modelRoot?.traverse((object) => {
        if (object.isMesh) object.material = object.userData.viewerMaterials[{ texture: 0, stone: 1, mesh: 2 }[next] ?? 0]
      })
      dirty = true
      if (modelRoot && document.hidden) renderer.render(scene, camera)
    }
    function viewpoint(name, instant = false) {
      if (name === 'free') return
      const focused = model.focus && !['site', 'top'].includes(name)
      const target = focused ? new THREE.Vector3(...model.focus.target) : center.clone()
      const distance = focused ? model.focus.radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) / Math.min(camera.aspect, 1) : fitDistance
      const directions = { overview: model.focus?.direction || model.direction || [1, 0.65, 1.2], site: model.direction || [1, 0.65, 1.2], front: model.front || [0, 0.12, 1], back: (model.front || [0, 0.12, 1]).map((v, i) => i === 1 ? v : -v), top: [0.001, 1, 0.001] }
      const direction = new THREE.Vector3(...(directions[name] || directions.overview)).normalize()
      const targetPosition = target.clone().addScaledVector(direction, distance * (name === 'top' ? 1.05 : 1))
      if (instant || document.hidden || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        camera.position.copy(targetPosition)
        controls.target.copy(target)
        controls.update()
        dirty = true
        // Paint the opening frame even when Safari pauses the background animation loop.
        if (modelRoot) renderer.render(scene, camera)
      } else transition = { time: performance.now(), position: camera.position.clone(), target: controls.target.clone(), destination: targetPosition, destinationTarget: target }
    }
    function zoom(factor) {
      transition = null
      const offset = camera.position.clone().sub(controls.target)
      offset.setLength(THREE.MathUtils.clamp(offset.length() * factor, controls.minDistance, controls.maxDistance))
      camera.position.copy(controls.target).add(offset)
      controls.update()
      dirty = true
      if (document.hidden) renderer.render(scene, camera)
    }
    const resize = new ResizeObserver(() => {
      const { width, height } = container.getBoundingClientRect()
      camera.aspect = width / Math.max(height, 1)
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
      const fov = THREE.MathUtils.degToRad(camera.fov)
      fitDistance = extent / (2 * Math.sin(fov / 2)) / Math.min(camera.aspect, 1) * (model.fit ?? 0.76)
      if (modelRoot && preferences.current.view !== 'free') viewpoint(preferences.current.view, true)
      dirty = true
    })
    resize.observe(container)
    const intersection = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; dirty = true })
    intersection.observe(container)
    const visibilityChanged = () => { dirty = true }
    document.addEventListener('visibilitychange', visibilityChanged)
    function animate(time) {
      animation = requestAnimationFrame(animate)
      const delta = Math.min((time - lastTime) / 1000, 0.05)
      lastTime = time
      if (!visible || document.hidden) return
      controls.autoRotate = preferences.current.rotating
      if (transition) {
        const t = Math.min((time - transition.time) / 750, 1)
        const eased = 1 - (1 - t) ** 3
        camera.position.lerpVectors(transition.position, transition.destination, eased)
        controls.target.lerpVectors(transition.target, transition.destinationTarget, eased)
        dirty = true
        if (t === 1) transition = null
      }
      controls.update(delta)
      if (dirty || controls.autoRotate) { renderer.render(scene, camera); dirty = false }
    }
    animation = requestAnimationFrame(animate)
    function keydown(event) {
      if (['+', '=', '-', '_', 'r', 'R', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) event.preventDefault()
      else return
      callbacks.current.onRotateChange(false)
      if (['+', '='].includes(event.key)) zoom(0.82)
      else if (['-', '_'].includes(event.key)) zoom(1.22)
      else if (event.key.toLowerCase() === 'r') { viewpoint('overview'); callbacks.current.onViewChange('overview') }
      else {
        transition = null
        const offset = camera.position.clone().sub(controls.target)
        const spherical = new THREE.Spherical().setFromVector3(offset)
        if (event.key === 'ArrowLeft') spherical.theta -= 0.12
        if (event.key === 'ArrowRight') spherical.theta += 0.12
        if (event.key === 'ArrowUp') spherical.phi -= 0.12
        if (event.key === 'ArrowDown') spherical.phi += 0.12
        spherical.phi = THREE.MathUtils.clamp(spherical.phi, controls.minPolarAngle, controls.maxPolarAngle)
        camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical))
        controls.update(); dirty = true
        callbacks.current.onViewChange('free')
      }
    }
    renderer.domElement.addEventListener('keydown', keydown)
    api.current = { setMode, viewpoint, zoom }

    fetchModel(assetUrl(model.file), abort.signal, (value) => { if (!destroyed) setProgress(value) })
      .then((bytes) => new GLTFLoader().parseAsync(bytes, assetUrl('models/')))
      .then((gltf) => {
        if (destroyed) { disposeModel(gltf.scene); return }
        modelRoot = gltf.scene
        let triangles = 0
        modelRoot.traverse((object) => {
          if (!object.isMesh) return
          const original = Array.isArray(object.material) ? object.material[0] : object.material
          const map = original.map
          if (map) map.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy())
          const texture = new THREE.MeshBasicMaterial({ map, color: map ? 0xffffff : 0xbca987, side: THREE.DoubleSide })
          const stone = new THREE.MeshStandardMaterial({ color: 0xbcb4a5, roughness: 0.94, metalness: 0, side: THREE.DoubleSide })
          const mesh = new THREE.MeshBasicMaterial({ color: 0x536c5f, wireframe: true, side: THREE.DoubleSide })
          object.userData.viewerMaterials = [texture, stone, mesh, original]
          triangles += (object.geometry.index?.count || object.geometry.attributes.position.count) / 3
        })
        scene.add(modelRoot)
        const bounds = new THREE.Box3().setFromObject(modelRoot)
        const sphere = bounds.getBoundingSphere(new THREE.Sphere())
        bounds.getCenter(center)
        extent = sphere.radius * 2
        camera.near = extent / 10000
        camera.far = extent * 100
        camera.updateProjectionMatrix()
        controls.minDistance = extent * 0.025
        controls.maxDistance = extent * 5
        fitDistance = extent / (2 * Math.sin(THREE.MathUtils.degToRad(camera.fov / 2))) / Math.min(camera.aspect, 1) * (model.fit ?? 0.76)
        setMode(preferences.current.mode)
        viewpoint(preferences.current.view, true)
        callbacks.current.onStats({ triangles: Math.round(triangles) })
        setProgress(100); setLoading(false)
        dirty = true
      })
      .catch((failure) => {
        if (!destroyed && failure.name !== 'AbortError') {
          setError('The model could not be opened. Check your connection and try again, or explore the photographs below.')
          setLoading(false)
        }
      })
    return () => {
      destroyed = true
      abort.abort()
      cancelAnimationFrame(animation)
      resize.disconnect(); intersection.disconnect()
      document.removeEventListener('visibilitychange', visibilityChanged)
      controls.dispose()
      renderer.domElement.removeEventListener('keydown', keydown)
      if (modelRoot) disposeModel(modelRoot)
      renderer.dispose()
      renderer.domElement.remove()
      api.current = null
    }
  }, [model, retry])

  useEffect(() => { api.current?.setMode(mode) }, [mode])
  useEffect(() => { api.current?.viewpoint(view) }, [view])
  useEffect(() => {
    const changed = () => setFullscreen(document.fullscreenElement === frame.current)
    document.addEventListener('fullscreenchange', changed)
    return () => document.removeEventListener('fullscreenchange', changed)
  }, [])
  const toggleFullscreen = async () => {
    if (document.fullscreenElement) await document.exitFullscreen?.()
    else if (frame.current.requestFullscreen) await frame.current.requestFullscreen()
    else setFullscreen(!fullscreen)
  }

  return <div className={`model-viewport ${fullscreen ? 'is-fullscreen' : ''}`} ref={frame}>
    <div className="viewport-label"><span className="status-dot" /> INTERACTIVE SURVEY <span className="viewport-label-separator">/</span> {model.shortTitle}</div>
    <div ref={host} className="webgl-host" />
    {(loading || error) && <div className="viewer-loading" aria-live="polite">
      {model.poster && <img className="viewer-poster" src={assetUrl(model.poster)} alt="" />}
      <div className="loading-card">
        {error ? <><Icon name="info" /><p>{error}</p><button onClick={() => { setLoading(true); setProgress(0); setError(''); setRetry((n) => n + 1) }}>Try again <Icon name="reset" size={16} /></button></> : <><span className="loading-orbit"><Icon name="cube" size={28} /></span><p>Bringing the stones into view</p><span className="loading-detail">{progress === null ? 'Loading the survey' : `${progress}% · ${progress >= 95 ? 'Preparing the model' : 'Loading the survey'}`}</span><div className="loading-track"><i style={{ width: `${progress ?? 10}%` }} /></div></>}
      </div>
    </div>}
    <div className="viewer-tools" aria-label="3D view controls">
      <button title="Zoom in" aria-label="Zoom in" disabled={loading || !!error} onClick={() => api.current?.zoom(0.8)}><Icon name="plus" /></button>
      <button title="Zoom out" aria-label="Zoom out" disabled={loading || !!error} onClick={() => api.current?.zoom(1.25)}><Icon name="minus" /></button>
      <span />
      <button title="Reset view" aria-label="Reset view" disabled={loading || !!error} onClick={() => { api.current?.viewpoint('overview'); onViewChange('overview'); onRotateChange(false) }}><Icon name="reset" /></button>
      <button title={rotating ? 'Pause rotation' : 'Rotate automatically'} aria-label={rotating ? 'Pause rotation' : 'Rotate automatically'} aria-pressed={rotating} disabled={loading || !!error} onClick={() => onRotateChange(!rotating)}><Icon name={rotating ? 'pause' : 'orbit'} /></button>
      <span />
      <button title={fullscreen ? 'Exit fullscreen' : 'Enter fullscreen'} aria-label={fullscreen ? 'Exit fullscreen' : 'Enter fullscreen'} onClick={() => toggleFullscreen().catch(() => setFullscreen(!fullscreen))}><Icon name={fullscreen ? 'close' : 'expand'} /></button>
    </div>
    <div className="viewport-bottom"><span><i className="drag-symbol" /> Drag to orbit <b>·</b> Scroll to zoom <b>·</b> Right-drag to pan</span><span className="view-coordinate">X <i /> Y <i /> Z</span></div>
  </div>
}
