import { SOURCES } from '../content.js'

export function Ornament({ className = '' }) {
  return (
    <div className={`rule-ornament my-6 ${className}`} aria-hidden="true">
      <svg width="34" height="10" viewBox="0 0 34 10" fill="currentColor">
        <path d="M0 5h10l4-4 3 4 3-4 4 4h10v.8H24l-4 4-3-4-3 4-4-4H0z" />
        <circle cx="17" cy="5" r="1.6" />
      </svg>
    </div>
  )
}

export function Rule({ className = '' }) {
  return <div className={`mx-auto my-5 h-px w-16 bg-ink-500/70 ${className}`} aria-hidden="true" />
}

export function SectionTitle({ children, sub, id }) {
  return (
    <header id={id} className="scroll-mt-24 text-center">
      <h2 className="font-display caps text-2xl font-medium text-ink-900 sm:text-3xl">{children}</h2>
      {sub && <p className="smallcaps mt-2 text-sm text-ink-700">{sub}</p>}
      <Ornament />
    </header>
  )
}

export function RunningHead({ left, right }) {
  return (
    <div className="caps mb-8 flex items-baseline justify-between border-b border-ink-300/50 pb-2 text-[0.65rem] text-ink-500">
      <span>{left}</span>
      <span>{right}</span>
    </div>
  )
}

export function Cite({ source, page }) {
  const s = SOURCES[source]
  if (!s) return null
  return (
    <a
      href={s.url}
      target="_blank"
      rel="noreferrer"
      className="smallcaps inline-block text-xs text-ink-500 underline decoration-ink-300 underline-offset-4 hover:text-vermilion-dark"
      title={s.citation}
    >
      {s.short}
      {page ? `, ${page}` : ''}
    </a>
  )
}

export function Quote({ children, source, page, className = '' }) {
  return (
    <figure className={`my-6 ${className}`}>
      <blockquote className="border-l-2 border-vermilion/70 pl-5 text-[1.05rem] leading-relaxed text-ink-900">
        {children}
      </blockquote>
      <figcaption className="mt-2 pl-5">
        <Cite source={source} page={page} />
      </figcaption>
    </figure>
  )
}

export function Sheet({ children, id, className = '', tone = '' }) {
  return (
    <section
      id={id}
      className={`paper ${tone} scroll-mt-20 mx-auto my-10 w-full max-w-3xl px-6 py-12 sm:px-14 sm:py-16 ${className}`}
    >
      {children}
    </section>
  )
}

export function PlateFigure({ plate, onOpen, className = '' }) {
  return (
    <figure className={`plate-frame p-3 sm:p-4 ${className}`}>
      <div className="caps mb-3 flex justify-between text-[0.6rem] text-ink-500">
        <span>Bîgeh.</span>
        <span>Plate {plate.num}</span>
      </div>
      <button
        type="button"
        onClick={() => onOpen?.(plate)}
        className="block w-full cursor-zoom-in focus:outline-none focus-visible:ring-2 focus-visible:ring-vermilion"
        aria-label={`Open Plate ${plate.num}`}
      >
        <img
          src={`${import.meta.env.BASE_URL}plates/${plate.id}.jpg`}
          alt={`Plate ${plate.num}: ${plate.caption}`}
          loading="lazy"
          className="plate-img block w-full"
        />
      </button>
      <figcaption className="mt-3 text-center text-sm italic leading-snug text-ink-700">
        {plate.caption}
        {plate.own && <span className="not-italic text-ink-500"> *</span>}
      </figcaption>
    </figure>
  )
}
