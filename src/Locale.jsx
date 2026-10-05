import { createContext, useContext, useEffect, useState } from 'react'

const LocaleContext = createContext(null)
export function LocaleProvider({ children }) {
  const [locale, setLocale] = useState(() => {
    const requested = new URLSearchParams(window.location.search).get('lang')
    if (requested === 'ar' || requested === 'en') return requested
    try {
      return localStorage.getItem('gate-language') === 'ar' ? 'ar' : 'en'
    } catch {
      return 'en'
    }
  })
  useEffect(() => {
    document.documentElement.lang = locale
    document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr'
    const url = new URL(window.location.href)
    if (url.searchParams.has('lang')) {
      url.searchParams.set('lang', locale)
      window.history.replaceState(null, '', url)
    }
    try {
      localStorage.setItem('gate-language', locale)
    } catch {
      /* Private browsing may disable storage. */
    }
  }, [locale])
  const t = (en, ar) => (locale === 'ar' ? ar : en)
  return (
    <LocaleContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocaleContext.Provider>
  )
}
// oxlint-disable-next-line react/only-export-components
export function useLocale() {
  return useContext(LocaleContext)
}
