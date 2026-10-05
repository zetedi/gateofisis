import { useEffect, useRef } from 'react'
import { useLocale } from '../Locale.jsx'
import Icon from './Icons.jsx'

export default function Lightbox({ plates, index, onClose, onStep }) {
  const { t, locale } = useLocale()
  const dialog = useRef(null)
  const plate = plates[index]
  useEffect(() => {
    if (plate) dialog.current.showModal()
    else dialog.current.close()
  }, [plate])
  return (
    <dialog
      ref={dialog}
      className="plate-dialog"
      aria-label={t('Photographic plates', 'اللوحات المصوّرة')}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === dialog.current) onClose()
      }}
      onKeyDown={(e) => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault()
          onStep((e.key === 'ArrowRight' ? 1 : -1) * (locale === 'ar' ? -1 : 1))
        }
      }}
    >
      {plate && (
        <div className="plate-dialog-body">
          <header>
            <span>
              {t('Bîgeh · Plate', 'بيجة · اللوحة')} {plate.num}
            </span>
            <button
              onClick={onClose}
              aria-label={t('Close plate', 'إغلاق اللوحة')}
              autoFocus
            >
              <Icon name="close" />
            </button>
          </header>
          <div className="plate-dialog-image">
            <img
              src={`${import.meta.env.BASE_URL}plates/${plate.id}.jpg`}
              alt={plate.caption}
            />
          </div>
          <p>{plate.caption}</p>
          <footer>
            <button onClick={() => onStep(-1)}>
              {t('← Previous plate', 'اللوحة السابقة →')}
            </button>
            <span>
              {index + 1} / {plates.length}
            </span>
            <button onClick={() => onStep(1)}>
              {t('Next plate →', '← اللوحة التالية')}
            </button>
          </footer>
        </div>
      )}
    </dialog>
  )
}
