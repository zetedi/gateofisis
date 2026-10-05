import { lazy, Suspense, useEffect, useState } from 'react'
import Navigation from './components/Navigation.jsx'
import Book, { BookHero } from './Book.jsx'
import './site.css'
import { useLocale } from './Locale.jsx'

const GatePage = lazy(() => import('./GatePage.jsx'))
const currentPage = () =>
  window.location.hash.startsWith('#3d')
    ? '3d'
    : ['', '#home', '#home-main'].includes(window.location.hash)
      ? 'home'
      : 'book'

export default function App() {
  const { locale, t } = useLocale()
  const [page, setPage] = useState(currentPage)
  useEffect(() => {
    const navigate = () => setPage(currentPage())
    window.addEventListener('hashchange', navigate)
    return () => window.removeEventListener('hashchange', navigate)
  }, [])
  useEffect(() => {
    document.title =
      page === 'home'
        ? locale === 'ar'
          ? 'بوابة إيزيس · بيجة، أسوان'
          : 'The Gate of Isis · Bîgeh, Aswan'
        : locale === 'ar'
          ? page === '3d'
            ? 'البوابة ثلاثية الأبعاد · بوابة إيزيس'
            : 'الكتاب · بوابة إيزيس'
          : page === '3d'
            ? 'The Gate in 3D · The Gate of Isis'
            : 'The Book · The Gate of Isis'
    if (page === '3d' || page === 'home')
      window.scrollTo({ top: 0, behavior: 'instant' })
    else
      requestAnimationFrame(() =>
        document
          .getElementById(window.location.hash.slice(1))
          ?.scrollIntoView({ behavior: 'instant' }),
      )
  }, [page, locale])
  return (
    <>
      <a
        className="skip-link"
        href={
          page === '3d'
            ? '#3d-main'
            : page === 'home'
              ? '#home-main'
              : '#book-main'
        }
      >
        {t('Skip to content', 'انتقل إلى المحتوى')}
      </a>
      <Navigation page={page} />
      {page === 'home' ? (
        <BookHero />
      ) : page === 'book' ? (
        <Book />
      ) : (
        <Suspense
          fallback={
            <main className="page-loading" aria-busy="true">
              {t('Opening the digital survey…', 'جارٍ فتح المسح الرقمي…')}
            </main>
          }
        >
          <GatePage />
        </Suspense>
      )}
      <footer className="author-credit">
        <span>{t('Authors', 'المؤلفان')}</span>
        <bdi>Pietro Parroccini</bdi>
        <span aria-hidden="true">&</span>
        <bdi>Zoltán Etédi</bdi>
      </footer>
    </>
  )
}
