import { useEffect } from 'react'

export default function Lightbox({ plates, index, onClose, onStep }) {
  const plate = index >= 0 ? plates[index] : null

  useEffect(() => {
    if (!plate) return
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowRight') onStep(1)
      if (e.key === 'ArrowLeft') onStep(-1)
    }
    window.addEventListener('keydown', onKey)
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = prev
    }
  }, [plate, onClose, onStep])

  if (!plate) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Plate ${plate.num}`}
      className="fixed inset-0 z-50 flex flex-col bg-leather-900/95 p-4 text-paper-100"
      onClick={onClose}
    >
      <div className="caps flex items-center justify-between text-xs text-paper-300">
        <span>Bîgeh. Plate {plate.num}</span>
        <button
          type="button"
          onClick={onClose}
          className="caps rounded px-3 py-1 hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-gilt"
        >
          Close ✕
        </button>
      </div>
      <div className="flex min-h-0 flex-1 items-center justify-center" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          onClick={() => onStep(-1)}
          className="hidden h-12 w-12 shrink-0 rounded-full font-display text-2xl hover:bg-white/10 sm:block"
          aria-label="Previous plate"
        >
          ‹
        </button>
        <img
          src={`/plates/${plate.id}.jpg`}
          alt={`Plate ${plate.num}: ${plate.caption}`}
          className="max-h-full max-w-full object-contain shadow-2xl"
        />
        <button
          type="button"
          onClick={() => onStep(1)}
          className="hidden h-12 w-12 shrink-0 rounded-full font-display text-2xl hover:bg-white/10 sm:block"
          aria-label="Next plate"
        >
          ›
        </button>
      </div>
      <p className="mt-3 text-center text-sm italic text-paper-200" onClick={(e) => e.stopPropagation()}>
        {plate.caption}
      </p>
      <div className="mt-2 flex justify-center gap-6 sm:hidden" onClick={(e) => e.stopPropagation()}>
        <button type="button" onClick={() => onStep(-1)} className="caps text-xs">‹ Prev</button>
        <button type="button" onClick={() => onStep(1)} className="caps text-xs">Next ›</button>
      </div>
    </div>
  )
}
