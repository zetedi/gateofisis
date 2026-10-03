import { lazy, Suspense, useEffect, useState } from 'react'
import Navigation from './components/Navigation.jsx'
import Book from './Book.jsx'
import './site.css'

const GatePage = lazy(() => import('./GatePage.jsx'))
const currentPage = () => window.location.hash.startsWith('#3d') ? '3d' : 'book'

export default function App() {
  const [page, setPage] = useState(currentPage)
  useEffect(() => {
    const navigate = () => setPage(currentPage())
    window.addEventListener('hashchange', navigate)
    return () => window.removeEventListener('hashchange', navigate)
  }, [])
  useEffect(() => {
    document.title = page === '3d' ? 'The Gate in 3D · The Gate of Isis' : 'The Book · The Gate of Isis'
    if (page === '3d') window.scrollTo({ top: 0, behavior: 'instant' })
    else requestAnimationFrame(() => document.getElementById(window.location.hash.slice(1))?.scrollIntoView())
  }, [page])
  return <>
    <a className="skip-link" href={page === '3d' ? '#3d-main' : '#title'}>Skip to content</a>
    <Navigation page={page} />
    {page === 'book' ? <Book /> : <Suspense fallback={<main className="page-loading" aria-busy="true">Opening the digital survey…</main>}><GatePage /></Suspense>}
  </>
}
