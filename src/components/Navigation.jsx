import { useEffect, useRef, useState } from 'react'
import { NAV } from '../content.js'
import Icon, { GateMark } from './Icons.jsx'

export default function Navigation({ page }) {
  const [open, setOpen] = useState(false)
  const menu = useRef(null)
  useEffect(() => {
    const close = (event) => { if (!menu.current?.contains(event.target)) setOpen(false) }
    const escape = (event) => { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('pointerdown', close)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('pointerdown', close)
      document.removeEventListener('keydown', escape)
    }
  }, [])
  return (
    <header className="site-header">
      <a className="site-brand" href="#title" aria-label="The Gate of Isis, home">
        <GateMark />
        <span>The Gate of Isis<small>BÎGEH · ASWAN</small></span>
      </a>
      <nav className="primary-navigation" aria-label="Main navigation">
        <div className="book-navigation" ref={menu}>
          <a href="#title" className={page === 'book' ? 'active' : ''} aria-current={page === 'book' ? 'page' : undefined} onClick={() => setOpen(false)}><span className="nav-index">01</span> The Book</a>
          <button className="book-menu-toggle" aria-label="Book chapters" aria-expanded={open} aria-controls="book-chapters" onClick={() => setOpen(!open)}><Icon name="chevron" size={14} /></button>
          {open && <div className="chapter-dropdown" id="book-chapters"><p>THE 1915 VOLUME</p>{NAV.map(([id, label], i) => <a key={id} href={`#${id}`} onClick={() => setOpen(false)}><span>{String(i + 1).padStart(2, '0')}</span>{label}<Icon name="arrow" size={14} /></a>)}</div>}
        </div>
        <a href="#3d" className={page === '3d' ? 'active' : ''} aria-current={page === '3d' ? 'page' : undefined}><span className="nav-index">02</span> The Gate <span className="nav-3d">3D</span></a>
      </nav>
      <span className="header-note">A record in stone.</span>
    </header>
  )
}
