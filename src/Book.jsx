import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react'
import * as english from './content.js'
import * as arabic from './content.ar.js'
import { useLocale } from './Locale.jsx'
import Lightbox from './components/Lightbox.jsx'
import Icon from './components/Icons.jsx'
import './book.css'

const chapterFromHash = () =>
  english.NAV.some(([id]) => `#${id}` === window.location.hash)
    ? window.location.hash.slice(1)
    : 'title'

function Chapter({ id, content: c, onOpen }) {
  const { t } = useLocale()
  const cite = (source, page) => (
    <a
      className="reader-cite"
      href={c.SOURCES[source].url}
      target="_blank"
      rel="noreferrer"
    >
      {c.SOURCES[source].short}
      {page && ` · ${page}`}
    </a>
  )
  const heading = (title, sub) => (
    <header className="reader-chapter-heading">
      <h2>{title}</h2>
      {sub && <p>{sub}</p>}
    </header>
  )
  const paragraphs = (items) => items.map((text, i) => <p key={i}>{text}</p>)
  const quote = (text, source, page) => (
    <>
      <blockquote>« {text} »</blockquote>
      {cite(source, page)}
    </>
  )
  const figure = (plate, compact = false) => (
    <figure
      className={`reader-figure ${compact ? 'compact' : ''}`}
      key={plate.id}
    >
      <button
        onClick={() => onOpen(plate)}
        aria-label={`${t('Enlarge plate', 'تكبير اللوحة')} ${plate.num}`}
      >
        <img
          src={`${import.meta.env.BASE_URL}plates/${plate.id}.jpg`}
          alt={plate.caption}
        />
      </button>
      <figcaption>
        <span>
          {t('PLATE', 'اللوحة')} {plate.num}
        </span>
        {plate.caption}
      </figcaption>
    </figure>
  )
  const plate = (id, compact) =>
    figure(
      c.PLATES.find((p) => p.id === id),
      compact,
    )
  switch (id) {
    case 'title':
      return (
        <div className="reader-title-page">
          <p className="reader-kicker">{c.TITLE_PAGE.series}</p>
          <div className="reader-rule" />
          <p>{c.TITLE_PAGE.les}</p>
          <h2>{c.TITLE_PAGE.seriesTitle}</h2>
          <div className="reader-rule" />
          <h3>{c.TITLE_PAGE.title}</h3>
          <p>{c.TITLE_PAGE.by}</p>
          <p>{c.TITLE_PAGE.authorLine}</p>
          {c.TITLE_PAGE.authorTitles.map((line, i) => (
            <p className="reader-small" key={i}>
              {line}
            </p>
          ))}
          <div className="reader-imprint">
            <p>{c.TITLE_PAGE.place}</p>
            <p>{c.TITLE_PAGE.press}</p>
            <p>1915</p>
          </div>
          <p className="reader-small">
            {t('From the original title page.', 'عن صفحة العنوان الأصلية.')}{' '}
            {cite('blackman')}
          </p>
        </div>
      )
    case 'preface':
      return (
        <>
          {heading(t('Preface', 'تمهيد'))}
          {paragraphs(c.PREFACE.paragraphs)}
          <p className="reader-signature">{c.PREFACE.signature}</p>
          <p>{c.PREFACE.dateline}</p>
          {cite(c.PREFACE.source, c.PREFACE.page)}
        </>
      )
    case 'introduction':
      return (
        <>
          {heading(
            t('The Temple of Bîgeh', 'معبد بيجة'),
            t('Part I · Introduction and text', 'الجزء الأول · المقدمة والنص'),
          )}
          {c.INTRODUCTION.paragraphs.map((p, i) => (
            <p key={i}>
              {p}
              {i === 1 && <sup> (1)</sup>}
              {i === 2 && <sup> (2) (3)</sup>}
            </p>
          ))}
          <div className="reader-footnotes">
            {c.INTRODUCTION.footnotes.map((f, i) => (
              <p key={i}>
                <sup>{i + 1}</sup> {f}
              </p>
            ))}
          </div>
          {cite(c.INTRODUCTION.source, c.INTRODUCTION.page)}
          {plate('plate-03-1', true)}
          {plate('plate-03-2', true)}
        </>
      )
    case 'plan':
      return (
        <>
          {heading(
            t('Plan of the temple', 'مخطط المعبد'),
            t('Plate I · Bîgeh', 'اللوحة الأولى · بيجة'),
          )}
          {figure(
            { id: 'plate-01-plan', num: 'I', caption: c.PLAN.caption },
            true,
          )}
          <dl className="reader-legend">
            {c.PLAN.legend.map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{v}</dd>
              </div>
            ))}
          </dl>
          <p className="reader-small">{c.PLAN.scale}</p>
          {cite(c.PLAN.source, c.PLAN.plate)}
        </>
      )
    case 'gate':
      return (
        <>
          {heading(
            t('The pylon gate', 'بوابة الصرح'),
            t(
              'Scenes and inscriptions in Blackman’s translation',
              'المناظر والنقوش وفق ترجمة بلاكمان',
            ),
          )}
          {c.GATE_SCENES.map((s) => (
            <section key={s.id}>
              <h3>{s.heading}</h3>
              <p className="reader-subtitle">
                {s.sub} · {s.plate}
              </p>
              {plate(s.image, true)}
              <p>{s.scene}</p>
              <h4>{t('Text', 'النص')}</h4>
              {s.texts.map((x, i) => (
                <p key={i}>
                  <em>{x.who}:</em> « {x.text} »
                </p>
              ))}
              <h4>{t('Archaeological details', 'تفاصيل أثرية')}</h4>
              <p>{s.details}</p>
              {cite(s.source, s.page)}
            </section>
          ))}
          <h3>{c.PYLON_TOWERS.north.heading}</h3>
          <p className="reader-subtitle">{c.PYLON_TOWERS.north.plate}</p>
          <p>{c.PYLON_TOWERS.north.text}</p>
          {quote(
            c.PYLON_TOWERS.north.inscription,
            c.PYLON_TOWERS.source,
            c.PYLON_TOWERS.page,
          )}
          <p>
            {t(
              'Immediately below is a much-destroyed horizontal inscription:',
              'أسفل هذا المنظر مباشرة سطر أفقي من نقش شديد التلف:',
            )}{' '}
            « {c.PYLON_TOWERS.north.fragment} »
          </p>
          <h3>{c.PYLON_TOWERS.south.heading}</h3>
          <p>{c.PYLON_TOWERS.south.plate}</p>
          <p>{c.PYLON_TOWERS.south.text}</p>
          {cite(c.PYLON_TOWERS.source, c.PYLON_TOWERS.page)}
        </>
      )
    case 'doors':
      return (
        <>
          {heading(
            t('The doors of the horizon', 'أبواب الأفق'),
            t(
              'The entrance to the outer hall · West face',
              'مدخل القاعة الخارجية · الوجه الغربي',
            ),
          )}
          <p>{c.DOOR_INSCRIPTIONS.intro}</p>
          {quote(
            c.DOOR_INSCRIPTIONS.north,
            c.DOOR_INSCRIPTIONS.source,
            'p. 46',
          )}
          {plate('plate-38', true)}
          {plate('plate-40', true)}
          <p>
            {t(
              'Above Osiris in two vertical lines:',
              'فوق أوزيريس في سطرين رأسيين:',
            )}{' '}
            « {c.DOOR_INSCRIPTIONS.osiris} »
          </p>
          {quote(
            c.DOOR_INSCRIPTIONS.horus,
            c.DOOR_INSCRIPTIONS.source,
            'p. 47',
          )}
          <p>
            {t(
              'Below this inscription, Horus pours water from a vase (Pl. XXXVI, 2). In front of Horus:',
              'أسفل هذا النقش منظر لحورس يصب الماء من إناء (اللوحة XXXVI، 2). وأمام حورس:',
            )}{' '}
            « {c.DOOR_INSCRIPTIONS.horusShort} »
          </p>
          <p>{c.DOOR_INSCRIPTIONS.southIntro}</p>
          {quote(
            c.DOOR_INSCRIPTIONS.south,
            c.DOOR_INSCRIPTIONS.source,
            'p. 47',
          )}
        </>
      )
    case 'graffiti':
      return (
        <>
          {heading(
            t('The graffiti of Bîgeh', 'نقوش زوّار بيجة'),
            t('Demotic · F. Ll. Griffith', 'الديموطيقية · ف. ل. غريفيث'),
          )}
          <p>{c.GRAFFITI.demotic.text}</p>
          <p>
            <strong>{t('No. 8.', 'رقم ٨.')} </strong>
            {c.GRAFFITI.demotic.no8}
          </p>
          {cite(c.GRAFFITI.demotic.source, c.GRAFFITI.demotic.page)}
          <h3>{t('Greek inscription', 'النقش اليوناني')}</h3>
          <p>{c.GRAFFITI.greek.intro}</p>
          <p>{c.GRAFFITI.greek.dating}</p>
          <table className="reader-greek">
            <tbody>
              {c.GRAFFITI.greek.lines.map(([gr, tr]) => (
                <tr key={gr}>
                  <td lang="el" dir="ltr">
                    {gr}
                  </td>
                  <td>{tr}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="reader-small">
            {t(
              'Lines 5–9 (patronymics and place-name) are omitted here; see the source.',
              'حُذفت هنا الأسطر ٥–٩ (أسماء الآباء واسم المكان)؛ راجع المصدر.',
            )}
          </p>
          {cite(c.GRAFFITI.greek.source, c.GRAFFITI.greek.page)}
        </>
      )
    case 'plates':
      return (
        <>
          {heading(
            t('The plates', 'اللوحات'),
            t(
              'Photographic plates from the 1915 volume. An asterisk marks Blackman’s own photographs.',
              'لوحات مصوّرة من مجلد ١٩١٥. تشير النجمة إلى الصور التي التقطها بلاكمان.',
            ),
          )}
          {c.PLATES.map((p) => figure(p))}
          <p className="reader-small">
            {t(
              'Captions from the List of Plates, pp. 71–72.',
              'التعليقات من قائمة اللوحات، ص ٧١–٧٢.',
            )}{' '}
            {cite('blackman')}
          </p>
        </>
      )
    case 'context':
      return (
        <>
          {heading(
            t('The Abaton', 'الأباتون'),
            t(
              'The island and its sanctuary in published sources',
              'الجزيرة وحرمها في المصادر المنشورة',
            ),
          )}
          {c.CONTEXT.map((b, i) => (
            <section key={i}>
              {b.quotes.map((q, j) => (
                <blockquote key={j}>« {q} »</blockquote>
              ))}
              {cite(b.source)}
            </section>
          ))}
          <h3>{t('Afterward', 'ما بعد ذلك')}</h3>
          <p>{c.AFTERWARD.note}</p>
          {c.AFTERWARD.quotes.map((q, i) => (
            <blockquote key={i}>« {q} »</blockquote>
          ))}
          {cite(c.AFTERWARD.source)}
        </>
      )
    case 'sources':
      return (
        <>
          {heading(t('Sources & editorial notes', 'المصادر وملاحظات التحرير'))}
          {c.FURTHER_READING.map((id) => (
            <section key={id}>
              <h4>{c.SOURCES[id].short}</h4>
              <p lang="en" dir="ltr">
                {c.SOURCES[id].citation}
              </p>
              {cite(id)}
              {c.SOURCES[id].note && (
                <p className="reader-small">{c.SOURCES[id].note}</p>
              )}
            </section>
          ))}
          <h3>{t('About this edition', 'عن هذه النسخة')}</h3>
          <p>
            {t(
              'The Arabic edition is an editorial translation of the English selections. Gaps, uncertainties and historical wording are retained; the original sources remain the reference.',
              'النسخة العربية ترجمة تحريرية للمقتطفات الإنجليزية، تحافظ على مواضع النقص والشك والتعبيرات التاريخية؛ وتبقى المصادر الأصلية مرجعًا.',
            )}
          </p>
          <p>
            {t(
              'The opening illustration is an AI-generated drawing in a handmade sketch style, based on the field photograph. It is an illustration, separate from the photographic survey.',
              'الرسم الافتتاحي صورة مولّدة بالذكاء الاصطناعي بأسلوب الرسم اليدوي، مستندة إلى الصورة الميدانية. وهو رسم توضيحي مستقل عن التوثيق الفوتوغرافي.',
            )}
          </p>
          <p className="reader-small">
            {t(
              'Blackman’s volume is in the public domain. Wikipedia text is CC BY-SA 4.0.',
              'مجلد بلاكمان ضمن الملكية العامة. نصوص ويكيبيديا متاحة برخصة CC BY-SA 4.0.',
            )}
          </p>
        </>
      )
    default:
      return null
  }
}

function PaginatedReader({ chapter, content, onOpen, onChapter }) {
  const { locale, t } = useLocale()
  const viewport = useRef(null)
  const flow = useRef(null)
  const [page, setPage] = useState(0)
  const [metrics, setMetrics] = useState({ count: 1, stride: 0 })
  const chapterIndex = content.NAV.findIndex(([id]) => id === chapter)
  useLayoutEffect(() => {
    let cancelled = false
    const measure = () => {
      if (cancelled || !viewport.current || !flow.current) return
      const width = viewport.current.clientWidth
      flow.current.style.height = `${viewport.current.clientHeight}px`
      flow.current.style.columnWidth = `${width}px`
      const gap = parseFloat(getComputedStyle(flow.current).columnGap)
      const count = Math.max(
        1,
        Math.ceil((flow.current.scrollWidth + gap - 2) / (width + gap)),
      )
      setMetrics({ count, stride: width + gap })
      setPage((p) => Math.min(p, count - 1))
    }
    const observer = new ResizeObserver(measure)
    observer.observe(viewport.current)
    flow.current.addEventListener('load', measure, true)
    const element = flow.current
    document.fonts.ready.then(measure)
    measure()
    return () => {
      cancelled = true
      observer.disconnect()
      element.removeEventListener('load', measure, true)
    }
  }, [locale, chapter])
  const turn = (delta) => {
    const next = page + delta
    if (next >= 0 && next < metrics.count) {
      setPage(next)
      viewport.current
        .closest('.reader-section')
        .scrollIntoView({ block: 'start', behavior: 'instant' })
    } else if (content.NAV[chapterIndex + delta])
      onChapter(content.NAV[chapterIndex + delta][0])
  }
  return (
    <div
      className="book-reader"
      onKeyDown={(e) => {
        if (e.target.closest('button,a,input')) return
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault()
          turn((e.key === 'ArrowRight' ? 1 : -1) * (locale === 'ar' ? -1 : 1))
        }
      }}
    >
      <div className="reader-toolbar">
        <span>{t('THE 1915 VOLUME', 'مجلد ١٩١٥')}</span>
        <span>{t('English edition', 'النسخة العربية')}</span>
      </div>
      <article
        className="reader-paper"
        aria-label={content.NAV[chapterIndex][1]}
        tabIndex={0}
      >
        <div className="reader-running-head">
          <span>{t('THE TEMPLE OF BÎGEH', 'معبد بيجة')}</span>
          <span>{content.NAV[chapterIndex][1]}</span>
        </div>
        <div className="reader-viewport" ref={viewport}>
          <div
            className="reader-flow"
            ref={flow}
            style={{
              transform: `translateX(${(locale === 'ar' ? 1 : -1) * page * metrics.stride}px)`,
            }}
          >
            <Chapter id={chapter} content={content} onOpen={onOpen} />
          </div>
        </div>
        <div className="reader-folio" aria-live="polite">
          {page + 1} / {metrics.count}
        </div>
      </article>
      <div className="reader-pagination">
        <button
          onClick={() => turn(-1)}
          disabled={page === 0 && chapterIndex === 0}
        >
          <span aria-hidden="true">{locale === 'ar' ? '→' : '←'}</span>{' '}
          {t('Previous', 'السابق')}
        </button>
        <span>
          {t('Page', 'صفحة')} {page + 1} {t('of', 'من')} {metrics.count}
        </span>
        <button
          onClick={() => turn(1)}
          disabled={
            page === metrics.count - 1 &&
            chapterIndex === content.NAV.length - 1
          }
        >
          {t('Next', 'التالي')}{' '}
          <span aria-hidden="true">{locale === 'ar' ? '←' : '→'}</span>
        </button>
      </div>
    </div>
  )
}

export function BookHero() {
  const { t } = useLocale()
  return (
    <main className="book-page landing-page" id="home-main">
      <header className="book-hero" id="home">
        <p className="eyebrow">
          {t('BÎGEH, ASWAN · A RECORD IN STONE', 'بيجة، أسوان · سجلّ في الحجر')}
        </p>
        <h1>{t('The Gate of Isis', 'بوابة إيزيس')}</h1>
        <p className="book-hero-intro">
          {t(
            'A monument, its inscriptions, and the landscape that holds them.',
            'أثرٌ ونقوشه والمشهد الذي يحتضنه.',
          )}
        </p>
        <img
          className="gate-sketch"
          src={`${import.meta.env.BASE_URL}art/gate-sketch.png`}
          width="1086"
          height="1448"
          alt={t(
            'A sketch of the gate of Isis, its arch and the stone stairs rising from the water.',
            'رسم لبوابة إيزيس وعقدها ودرجاتها الحجرية الصاعدة من الماء.',
          )}
          fetchPriority="high"
        />
        <blockquote className="hero-quotation">
          {t(
            '"...the divine doors of the gates of the horizon, the hall of heaven upon earth, the great doors of the places of Osiris..."',
            '«...الأبواب الإلهية لبوابات الأفق، قاعة السماء على الأرض، الأبواب العظيمة لمواضع أوزيريس...»',
          )}
        </blockquote>
        <a className="hero-citation" href="#doors">
          {t(
            'BLACKMAN · THE TEMPLE OF BÎGEH · 1915, P. 47',
            'بلاكمان · معبد بيجة · ١٩١٥، ص ٤٧',
          )}
        </a>
        <div className="hero-actions">
          <a href="#title">
            {t('Read the book', 'اقرأ الكتاب')} <Icon name="arrow" size={18} />
          </a>
          <a href="#3d">
            {t('Explore the gate in 3D', 'استكشف البوابة ثلاثية الأبعاد')}{' '}
            <Icon name="arrow" size={18} />
          </a>
        </div>
      </header>
    </main>
  )
}

export default function Book() {
  const { locale, t } = useLocale()
  const content = locale === 'ar' ? arabic : english
  const [chapter, setChapter] = useState(chapterFromHash)
  const [index, setIndex] = useState(-1)
  const gallery = [
    { id: 'plate-01-plan', num: 'I', caption: content.PLAN.caption },
    ...content.PLATES,
  ]
  useEffect(() => {
    const navigate = () => setChapter(chapterFromHash())
    window.addEventListener('hashchange', navigate)
    return () => window.removeEventListener('hashchange', navigate)
  }, [])
  useEffect(() => {
    if (window.location.hash && window.location.hash !== '#home')
      requestAnimationFrame(() =>
        document
          .getElementById(chapter)
          ?.scrollIntoView({ block: 'start', behavior: 'instant' }),
      )
  }, [chapter])
  const close = useCallback(() => setIndex(-1), [])
  const step = useCallback(
    (d) =>
      setIndex(
        (i) =>
          (i + d + english.PLATES.length + 1) % (english.PLATES.length + 1),
      ),
    [],
  )
  return (
    <main className="book-page" id="book-main">
      <div className="book-layout">
        <aside className="book-contents">
          <p className="control-label">{t('CONTENTS', 'المحتويات')}</p>
          <nav aria-label={t('Book contents', 'محتويات الكتاب')}>
            {content.NAV.map(([id, label], i) => (
              <a
                href={`#${id}`}
                key={id}
                aria-current={chapter === id ? 'page' : undefined}
              >
                <span>{String(i + 1).padStart(2, '0')}</span>
                {label}
              </a>
            ))}
          </nav>
          <p className="contents-note">
            {t(
              'Aylward M. Blackman\nCairo, 1915',
              'أيلورد م. بلاكمان\nالقاهرة، ١٩١٥',
            )}
          </p>
        </aside>
        <section id={chapter} className="reader-section">
          <PaginatedReader
            key={`${locale}-${chapter}`}
            chapter={chapter}
            content={content}
            onOpen={(p) => setIndex(gallery.findIndex((x) => x.id === p.id))}
            onChapter={(id) => {
              window.location.hash = id
            }}
          />
        </section>
      </div>
      <footer className="survey-footer">
        <span>
          {t('THE GATE OF ISIS · BÎGEH, ASWAN', 'بوابة إيزيس · بيجة، أسوان')}
        </span>
        <a href="#3d">
          {t('Continue to the digital survey →', 'تابع إلى المسح الرقمي ←')}
        </a>
      </footer>
      <Lightbox plates={gallery} index={index} onClose={close} onStep={step} />
    </main>
  )
}
