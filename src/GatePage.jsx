import { useEffect, useMemo, useRef, useState } from 'react'
import ModelViewer from './components/ModelViewer.jsx'
import Icon, { GateMark } from './components/Icons.jsx'

const asset = (file) => `${import.meta.env.BASE_URL}${file}`
const sourceViewpoints = [['overview', 'Perspective'], ['front', 'Front'], ['back', 'Reverse'], ['top', 'Above']]
const siteViewpoints = [['overview', 'Gate & stairs'], ['site', 'Whole site'], ['front', 'Front'], ['back', 'Reverse'], ['top', 'Above']]

function PhotoDialog({ photo, close }) {
  const dialog = useRef(null)
  useEffect(() => {
    if (photo) dialog.current.showModal()
    else dialog.current.close()
  }, [photo])
  return <dialog className="survey-dialog" ref={dialog} aria-labelledby="survey-photo-title" onCancel={close} onClick={(event) => { if (event.target === dialog.current) close() }}>
    {photo && <div className="survey-dialog-inner">
      <button className="dialog-close" onClick={close} aria-label="Close photograph" autoFocus><Icon name="close" /></button>
      <img src={asset(photo.image)} alt={photo.title} />
      <div><span className="eyebrow">FIELD PHOTOGRAPH</span><h3 id="survey-photo-title">{photo.title}</h3><p>{photo.date}</p><p className="photo-source">Source: {photo.source}</p></div>
    </div>}
  </dialog>
}

export default function GatePage() {
  const [survey, setSurvey] = useState(null)
  const [loadError, setLoadError] = useState(false)
  const [selection, setSelection] = useState(0)
  const [quality, setQuality] = useState('standard')
  const [mode, setMode] = useState('texture')
  const [view, setView] = useState('overview')
  const [rotating, setRotating] = useState(false)
  const [stats, setStats] = useState(null)
  const [photos, setPhotos] = useState([])
  const [photo, setPhoto] = useState(null)
  const [showHelp, setShowHelp] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    fetch(asset('models/survey.json'), { signal: controller.signal })
      .then((r) => { if (!r.ok) throw new Error('Survey unavailable'); return r.json() })
      .then(setSurvey).catch((error) => { if (error.name !== 'AbortError') setLoadError(true) })
    fetch(asset('survey/photographs.json'), { signal: controller.signal })
      .then((r) => r.json()).then(setPhotos).catch(() => {})
    return () => controller.abort()
  }, [])
  const sourceModel = survey?.models[selection]
  const viewpoints = sourceModel?.focus ? siteViewpoints : sourceViewpoints
  const model = useMemo(() => sourceModel && quality === 'high' && sourceModel.highFile ? { ...sourceModel, id: `${sourceModel.id}-high`, file: sourceModel.highFile, bytes: sourceModel.highBytes } : sourceModel, [sourceModel, quality])
  const choose = (index) => { setSelection(index); setQuality('standard'); setView('overview'); setRotating(false); setStats(null) }

  return <main className="gate-page" id="3d-main">
    <section className="survey-intro" id="3d" aria-labelledby="survey-title">
      <div><p className="eyebrow"><span className="eyebrow-line" /> BÎGEH, ASWAN <span className="eyebrow-divider">/</span> THE DIGITAL SURVEY</p><h1 id="survey-title">The gate, in<br /><em>three dimensions.</em></h1></div>
      <div className="survey-intro-aside"><span className="edition-number">FIELD RECORD — 2026</span><p>Move around the monument, trace its carved surfaces, and explore the stones that surround it.</p><a href="#3d-archive">Discover the survey <Icon name="arrow" size={17} /></a></div>
    </section>

    <section className="survey-workspace" aria-label="Interactive 3D survey">
      <div className="workspace-heading"><span><span className="section-number">01</span> THE SPATIAL RECORD</span><button onClick={() => setShowHelp(!showHelp)} aria-expanded={showHelp} aria-controls="viewer-instructions"><Icon name="info" size={16} /> How to explore</button></div>
      {showHelp && <div id="viewer-instructions" className="viewer-instructions"><p><strong>Take a closer look.</strong> Drag to orbit, scroll or pinch to zoom, and right-drag or use two fingers to pan. Choose a viewpoint to return to a fixed angle.</p><p>Keyboard: focus the model, then use the arrow keys to rotate, + / − to zoom, and R to reset. Surface modes reveal the photograph, stone form, or underlying mesh.</p><button onClick={() => setShowHelp(false)} aria-label="Close instructions"><Icon name="close" size={17} /></button></div>}
      {model ? <>
        <div className="workspace-body">
          <aside className="survey-sidebar">
            <div className="sidebar-section"><p className="control-label">EXPLORE THE SITE</p><div className="survey-models" role="group" aria-label="Survey area">
              {survey.models.map((item, index) => <button key={item.id} className={index === selection ? 'selected' : ''} aria-pressed={index === selection} onClick={() => choose(index)}><span className="model-number">{String(index + 1).padStart(2, '0')}</span><span>{item.shortTitle}<small>{item.subtitle}</small></span><Icon name="arrow" size={16} /></button>)}
            </div></div>
            <div className="sidebar-section surface-section"><p className="control-label">SURFACE</p><div className="surface-options" role="group" aria-label="Surface display">
              {[['texture', 'Photograph'], ['stone', 'Stone'], ['mesh', 'Mesh']].map(([id, title]) => <button key={id} onClick={() => setMode(id)} className={mode === id ? 'selected' : ''} aria-pressed={mode === id}><i className={`surface-swatch swatch-${id}`} />{title}</button>)}
            </div></div>
            <div className="sidebar-detail"><Icon name="layers" size={20} /><p>{model.description}</p><dl><div><dt>Geometry</dt><dd>{stats ? `${new Intl.NumberFormat('en').format(stats.triangles)} faces` : 'Loading…'}</dd></div><div><dt>Record</dt><dd>{model.record}</dd></div></dl></div>
            <a className="model-download" href={asset(model.file)} download><span><Icon name="download" size={18} /> Download this model</span><small>GLB{model.bytes ? ` · ${(model.bytes / 1e6).toFixed(1)} MB` : ''}</small></a>
          </aside>
          <div className="viewer-column">{sourceModel.highFile && <button className="detail-toggle" aria-pressed={quality === 'high'} onClick={() => { setQuality(quality === 'high' ? 'standard' : 'high'); setView('overview'); setStats(null) }}><Icon name="layers" size={14} /> {quality === 'high' ? 'High detail' : 'Load high detail'}</button>}<ModelViewer key={model.id} model={model} mode={mode} view={view} rotating={rotating} onRotateChange={setRotating} onStats={setStats} onViewChange={setView} /><div className="viewpoint-bar"><span className="control-label">VIEWPOINT</span><div role="group" aria-label="Camera viewpoint">{viewpoints.map(([id, title]) => <button key={id} aria-pressed={view === id} className={view === id ? 'selected' : ''} onClick={() => { setView(id); setRotating(false) }}>{title}</button>)}</div><span className="viewpoint-note">{view === 'free' ? 'Free orbit' : 'Orbit to explore'} <Icon name="orbit" size={16} /></span></div></div>
        </div>
        <div className="workspace-caption"><p><span className="status-dot" /> {model.note}</p><span>September 2026 survey</span><a className="mobile-model-download" href={asset(model.file)} download aria-label={`Download ${model.title} as GLB`}><Icon name="download" size={16} /> GLB</a></div>
      </> : <div className="survey-pending" role="status">{loadError ? <>The survey could not be loaded. <button onClick={() => window.location.reload()}>Reload the page</button></> : 'Opening the field archive…'}</div>}
    </section>

    <section className="survey-record" id="3d-archive">
      <div><p className="eyebrow"><span className="section-number">02</span> A RECORD OF WHAT REMAINS</p><h2>Every surface<br />has a story.</h2><p className="record-intro">The gate belongs to a larger landscape. The pavement, the columns, the scattered blocks: each is part of this digital field record.</p></div>
      <div className="record-details"><dl className="record-facts"><div><dt>Photographic input</dt><dd>{survey?.photoCount?.toLocaleString('en') || '1,055'}<small>unique survey photographs</small></dd></div><div><dt>Supporting surveys</dt><dd>03<small>textured Polycam scans</small></dd></div><div><dt>Field campaign</dt><dd>09 / 26<small>September 2026</small></dd></div></dl><div className="record-method"><p className="control-label">ABOUT THIS RECORD</p><p>{survey?.method || 'The original textured scans preserve the monument and the surrounding surfaces captured in the field.'}</p><p className="record-caveat">{survey?.limitation || 'Open edges and missing surfaces reflect gaps in capture. These models document visible remains; they are not a hypothetical restoration.'}</p><a href={asset('models/survey.json')} target="_blank" rel="noreferrer">View the survey record <Icon name="arrow" size={15} /></a></div></div>
    </section>

    {photos.length > 0 && <section className="field-photographs" aria-labelledby="field-title"><div className="field-heading"><div><p className="eyebrow"><span className="section-number">03</span> THE PHOTOGRAPHIC RECORD</p><h2 id="field-title">From the field.</h2></div><p>The photographs behind the geometry.<br />Select an image to look closer.</p></div><div className="photo-grid">{photos.map((item, i) => <button className="survey-photo" aria-label={`View photograph: ${item.title}`} key={item.id} onClick={() => setPhoto(item)}><div><img src={asset(item.thumbnail)} alt="" loading="lazy" /><span className="photo-expand"><Icon name="expand" size={18} /></span></div><span className="photo-caption"><span>{String(i+1).padStart(2, '0')}</span>{item.title}<Icon name="arrow" size={16} /></span></button>)}</div></section>}

    <section className="book-crosslink"><GateMark /><div><p className="eyebrow">ANOTHER WAY TO LOOK</p><h2>Return to the written record.</h2><p>Aylward M. Blackman’s 1915 volume, its inscriptions and photographic plates.</p></div><a href="#title">Open the book <Icon name="arrow" size={20} /></a></section>
    <footer className="survey-footer"><span>THE GATE OF ISIS <span>·</span> BÎGEH, ASWAN</span><span>A place. A record. A closer look.</span><a href="#3d">Back to the gate ↑</a></footer>
    <PhotoDialog photo={photo} close={() => setPhoto(null)} />
  </main>
}
