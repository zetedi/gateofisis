import { useEffect, useRef, useState } from 'react'
import { NAV as EN_NAV } from '../content.js'
import { NAV as AR_NAV } from '../content.ar.js'
import { useLocale } from '../Locale.jsx'
import Icon, { GateMark } from './Icons.jsx'

export default function Navigation({ page }) {
  const { locale, setLocale, t } = useLocale()
  const NAV = locale === 'ar' ? AR_NAV : EN_NAV
  const [open, setOpen] = useState(false)
  const menu = useRef(null)
  useEffect(() => {
    const close = (event) => {
      if (!menu.current?.contains(event.target)) setOpen(false)
    }
    const escape = (event) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', close)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('pointerdown', close)
      document.removeEventListener('keydown', escape)
    }
  }, [])
  return (
    <header className="site-header">
      <a
        className="site-brand"
        href="#home"
        aria-label={t('The Gate of Isis, home', 'بوابة إيزيس، الصفحة الرئيسية')}
      >
        <GateMark />
        <span>
          {t('The Gate of Isis', 'بوابة إيزيس')}
          <small>{t('BÎGEH · ASWAN', 'بيجة · أسوان')}</small>
        </span>
      </a>
      <nav
        className="primary-navigation"
        aria-label={t('Main navigation', 'التنقل الرئيسي')}
      >
        <div className="book-navigation" ref={menu}>
          <a
            href="#title"
            className={page === 'book' ? 'active' : ''}
            aria-current={page === 'book' ? 'page' : undefined}
            onClick={() => setOpen(false)}
          >
            <span className="nav-index">01</span> {t('The Book', 'الكتاب')}
          </a>
          <button
            className="book-menu-toggle"
            aria-label={t('Book chapters', 'فصول الكتاب')}
            aria-expanded={open}
            aria-controls="book-chapters"
            onClick={() => setOpen(!open)}
          >
            <Icon name="chevron" size={14} />
          </button>
          {open && (
            <div className="chapter-dropdown" id="book-chapters">
              <p>{t('THE 1915 VOLUME', 'مجلد ١٩١٥')}</p>
              {NAV.map(([id, label], i) => (
                <a key={id} href={`#${id}`} onClick={() => setOpen(false)}>
                  <span>{String(i + 1).padStart(2, '0')}</span>
                  {label}
                  <Icon name="arrow" size={14} />
                </a>
              ))}
            </div>
          )}
        </div>
        <a
          href="#3d"
          className={page === '3d' ? 'active' : ''}
          aria-current={page === '3d' ? 'page' : undefined}
        >
          <span className="nav-index">02</span> {t('The Gate', 'البوابة')}{' '}
          <span className="nav-3d">3D</span>
        </a>
      </nav>
      <div
        className="language-switch"
        role="group"
        aria-label="Language / اللغة"
      >
        <button
          lang="en"
          aria-pressed={locale === 'en'}
          onClick={() => setLocale('en')}
        >
          EN
        </button>
        <span aria-hidden="true">/</span>
        <button
          lang="ar"
          aria-pressed={locale === 'ar'}
          onClick={() => setLocale('ar')}
        >
          العربية
        </button>
      </div>
    </header>
  )
}
