import { useCallback, useState } from 'react'
import {
  AFTERWARD,
  CONTEXT,
  DOOR_INSCRIPTIONS,
  FURTHER_READING,
  GATE_SCENES,
  GRAFFITI,
  INTRODUCTION,
  NAV,
  PLAN,
  PLATES,
  PREFACE,
  PYLON_TOWERS,
  SOURCES,
  TITLE_PAGE,
} from './content.js'
import { Cite, Ornament, PlateFigure, Quote, Rule, RunningHead, SectionTitle, Sheet } from './components/ui.jsx'
import Lightbox from './components/Lightbox.jsx'

const plateById = (id) => PLATES.find((p) => p.id === id)

function Nav() {
  return (
    <nav className="leather sticky top-0 z-40 border-b border-black/40 text-paper-200 shadow-lg">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <a href="#title" className="font-display caps text-sm text-gilt">
          The Gate of Isis
        </a>
        <ul className="hidden gap-4 md:flex">
          {NAV.map(([id, label]) => (
            <li key={id}>
              <a href={`#${id}`} className="caps text-[0.65rem] text-paper-300 transition hover:text-gilt">
                {label}
              </a>
            </li>
          ))}
        </ul>
        <a href="#plates" className="caps text-[0.65rem] text-paper-300 hover:text-gilt md:hidden">
          Plates
        </a>
      </div>
    </nav>
  )
}

function Cover() {
  return (
    <header className="leather relative overflow-hidden text-paper-100">
      <div className="mx-auto max-w-5xl px-6 pb-20 pt-24 text-center sm:pt-32">
        <p className="caps-wide text-xs text-paper-300">{TITLE_PAGE.series}</p>
        <Rule className="bg-gilt/60" />
        <p className="caps text-xs text-paper-300">{TITLE_PAGE.les}</p>
        <h1 className="font-display caps mt-3 text-3xl leading-tight text-vermilion sm:text-5xl">
          {TITLE_PAGE.seriesTitle}
        </h1>
        <Ornament className="text-gilt" />
        <p className="font-display caps text-2xl text-paper-50 sm:text-4xl">The Gate of Isis</p>
        <p className="smallcaps mt-3 text-base text-paper-300">
          The Pylon Gate-way of the Temple of Bîgeh, First Cataract, Aswan
        </p>
        <p className="caps mt-10 text-[0.65rem] text-paper-300">
          Presented from the record of Aylward M. Blackman (1915) and published sources
        </p>
        <a
          href="#title"
          className="caps mt-12 inline-block border border-gilt/60 px-6 py-2 text-xs text-gilt transition hover:bg-gilt/10"
        >
          Open the volume
        </a>
      </div>
      <div className="absolute inset-y-0 left-0 w-10 bg-gradient-to-r from-black/40 to-transparent sm:w-20" aria-hidden="true" />
    </header>
  )
}

function TitlePage() {
  return (
    <Sheet id="title" tone="paper-dark" className="text-center">
      <p className="caps text-xs text-ink-700">{TITLE_PAGE.series}</p>
      <Rule />
      <p className="caps text-xs text-ink-700">{TITLE_PAGE.les}</p>
      <h2 className="font-display caps mt-2 text-2xl text-vermilion sm:text-4xl">{TITLE_PAGE.seriesTitle}</h2>
      <Ornament />
      <p className="font-display caps text-xl text-ink-900 sm:text-3xl">{TITLE_PAGE.title}</p>
      <p className="caps mt-4 text-xs text-ink-700">{TITLE_PAGE.by}</p>
      <p className="mt-6 font-display caps text-sm text-ink-900">{TITLE_PAGE.authorLine}</p>
      {TITLE_PAGE.authorTitles.map((t) => (
        <p key={t} className="smallcaps text-sm text-ink-700">
          {t}
        </p>
      ))}
      <div className="mt-14 space-y-1">
        <p className="caps text-sm text-ink-900">{TITLE_PAGE.place}</p>
        <p className="caps text-xs text-ink-700">{TITLE_PAGE.press}</p>
        <Rule />
        <p className="caps text-sm text-ink-900">{TITLE_PAGE.year}</p>
      </div>
      <p className="mt-10 text-xs italic text-ink-500">
        Transcribed from the title page. Scan:{' '}
        <a className="underline hover:text-vermilion-dark" href={SOURCES.blackman.url} target="_blank" rel="noreferrer">
          Internet Archive
        </a>
        .
      </p>
    </Sheet>
  )
}

function Preface() {
  return (
    <Sheet id="preface">
      <SectionTitle>Preface.</SectionTitle>
      {PREFACE.paragraphs.map((p) => (
        <p key={p} className="dropcap text-[1.05rem] leading-relaxed">
          {p}
        </p>
      ))}
      <p className="smallcaps mt-6 text-right">{PREFACE.signature}</p>
      <p className="mt-2 text-sm">{PREFACE.dateline}</p>
      <p className="mt-6 text-right">
        <Cite source={PREFACE.source} page={PREFACE.page} />
      </p>
    </Sheet>
  )
}

function Introduction({ onOpen }) {
  return (
    <Sheet id="introduction">
      <RunningHead left="The Temple of Bîgeh." right="Part I." />
      <SectionTitle sub="Introduction and Text.">Part I.</SectionTitle>
      <div className="space-y-5 text-[1.05rem] leading-relaxed">
        <p className="dropcap">{INTRODUCTION.paragraphs[0]}</p>
        <p>
          {INTRODUCTION.paragraphs[1]}
          <sup className="fn"> (1)</sup>
        </p>
      </div>

      <div className="my-8 grid gap-6 sm:grid-cols-2">
        <PlateFigure plate={plateById('plate-03-1')} onOpen={onOpen} />
        <PlateFigure plate={plateById('plate-03-2')} onOpen={onOpen} />
      </div>

      <div className="space-y-5 text-[1.05rem] leading-relaxed">
        <p>
          {INTRODUCTION.paragraphs[2]}
          <sup className="fn"> (2) (3)</sup>
        </p>
        <p>{INTRODUCTION.paragraphs[3]}</p>
        <p>{INTRODUCTION.paragraphs[4]}</p>
        <p>{INTRODUCTION.paragraphs[5]}</p>
      </div>

      <div className="mt-8 border-t border-ink-300/50 pt-3">
        {INTRODUCTION.footnotes.map((f, i) => (
          <p key={f} className="footnote">
            <sup className="fn">({i + 1})</sup> {f}
          </p>
        ))}
        <p className="mt-3">
          <Cite source={INTRODUCTION.source} page={INTRODUCTION.page} />
        </p>
      </div>
    </Sheet>
  )
}

function Plan({ onOpen }) {
  const plate = { id: 'plate-01-plan', num: 'I', caption: PLAN.caption }
  return (
    <Sheet id="plan">
      <RunningHead left="Bîgeh." right="Plate I" />
      <SectionTitle sub="Ground-plan of the Temple.">Plate I.</SectionTitle>
      <div className="grid items-start gap-8 sm:grid-cols-5">
        <div className="sm:col-span-3">
          <PlateFigure plate={plate} onOpen={onOpen} />
        </div>
        <dl className="sm:col-span-2">
          {PLAN.legend.map(([k, v]) => (
            <div key={k} className="flex gap-3 border-b border-ink-300/40 py-2 text-sm">
              <dt className="w-5 font-display italic text-vermilion-dark">{k}.</dt>
              <dd>— {v}</dd>
            </div>
          ))}
          <p className="mt-3 text-xs italic text-ink-500">{PLAN.scale}</p>
          <p className="mt-4">
            <Cite source={PLAN.source} page={PLAN.plate} />
          </p>
        </dl>
      </div>
    </Sheet>
  )
}

function SceneBlock({ scene, onOpen, flip }) {
  const plate = plateById(scene.image)
  return (
    <article className="scroll-mt-24 py-8" id={scene.id}>
      <h3 className="font-display caps text-center text-lg text-ink-900">{scene.heading}</h3>
      <p className="smallcaps text-center text-sm text-ink-700">{scene.sub}</p>
      <p className="text-center text-xs text-ink-500">({scene.plate}.)</p>
      <div className={`mt-6 grid gap-8 md:grid-cols-5 ${flip ? 'md:[&>*:first-child]:order-2' : ''}`}>
        <div className="md:col-span-2">
          <PlateFigure plate={plate} onOpen={onOpen} />
        </div>
        <div className="md:col-span-3">
          <p className="text-[1.02rem] leading-relaxed">{scene.scene}</p>
          <p className="smallcaps mt-5 text-sm text-ink-700">Text.</p>
          <ol className="mt-1 space-y-3">
            {scene.texts.map((t, i) => (
              <li key={t.text} className="text-[1.02rem] leading-relaxed">
                <span className="font-display italic text-vermilion-dark">{String.fromCharCode(97 + i)}.</span>{' '}
                <span className="text-ink-700">{t.who} :</span> «&nbsp;{t.text}&nbsp;»
              </li>
            ))}
          </ol>
          <p className="smallcaps mt-5 text-sm text-ink-700">Archaeological details :</p>
          <p className="mt-1 text-[0.95rem] leading-relaxed text-ink-700">{scene.details}</p>
          <p className="mt-4">
            <Cite source={scene.source} page={scene.page} />
          </p>
        </div>
      </div>
    </article>
  )
}

function Gate({ onOpen }) {
  return (
    <Sheet id="gate">
      <RunningHead left="East face of the pylon gate-way." right="The Pylon." />
      <SectionTitle sub="The scenes and inscriptions of the gate-way, in Blackman’s translation.">The Pylon.</SectionTitle>
      <div className="divide-y divide-ink-300/40">
        {GATE_SCENES.map((s, i) => (
          <SceneBlock key={s.id} scene={s} onOpen={onOpen} flip={i % 2 === 1} />
        ))}
      </div>

      <Ornament className="mt-4" />
      <h3 className="font-display caps text-center text-lg">{PYLON_TOWERS.north.heading}</h3>
      <p className="text-center text-xs text-ink-500">({PYLON_TOWERS.north.plate}.)</p>
      <p className="mt-4 text-[1.02rem] leading-relaxed">{PYLON_TOWERS.north.text}</p>
      <Quote source={PYLON_TOWERS.source} page={PYLON_TOWERS.page}>
        «&nbsp;{PYLON_TOWERS.north.inscription}&nbsp;»
      </Quote>
      <p className="text-[1.02rem] leading-relaxed">
        Immediately below the above scene is a much destroyed horizontal line of inscription : «&nbsp;
        {PYLON_TOWERS.north.fragment}&nbsp;»
      </p>
      <h3 className="font-display caps mt-10 text-center text-lg">{PYLON_TOWERS.south.heading}</h3>
      <p className="text-center text-xs text-ink-500">({PYLON_TOWERS.south.plate}.)</p>
      <p className="mt-4 text-[1.02rem] leading-relaxed">{PYLON_TOWERS.south.text}</p>
      <p className="mt-4">
        <Cite source={PYLON_TOWERS.source} page={PYLON_TOWERS.page} />
      </p>
    </Sheet>
  )
}

function Doors({ onOpen }) {
  const d = DOOR_INSCRIPTIONS
  return (
    <Sheet id="doors">
      <RunningHead left="The entrance to the outer hall : west face." right="The Doors." />
      <SectionTitle sub="Inscriptions on the jambs of the entrance to the outer hall.">The Doors of the Horizon.</SectionTitle>
      <p className="text-[1.02rem] leading-relaxed">{d.intro}</p>
      <Quote source={d.source} page="p. 46">«&nbsp;{d.north}&nbsp;»</Quote>
      <div className="my-8 grid gap-6 sm:grid-cols-2">
        <PlateFigure plate={plateById('plate-38')} onOpen={onOpen} />
        <PlateFigure plate={plateById('plate-40')} onOpen={onOpen} />
      </div>
      <p className="text-[1.02rem] leading-relaxed">
        Above Osiris in two vertical lines : «&nbsp;{d.osiris}&nbsp;»
      </p>
      <Quote source={d.source} page="p. 47">«&nbsp;{d.horus}&nbsp;»</Quote>
      <p className="text-[1.02rem] leading-relaxed">
        Below this inscription is a scene representing Horus pouring water out of a vase (Pl. XXXVI, 2). In front of Horus :
        «&nbsp;{d.horusShort}&nbsp;»
      </p>
      <p className="mt-6 text-[1.02rem] leading-relaxed">{d.southIntro}</p>
      <Quote source={d.source} page="p. 47">«&nbsp;{d.south}&nbsp;»</Quote>
    </Sheet>
  )
}

function Graffiti() {
  const g = GRAFFITI
  return (
    <Sheet id="graffiti">
      <RunningHead left="The Demotic graffiti of Bîgeh." right="Greek inscription." />
      <SectionTitle sub="By F. Ll. Griffith.">The Demotic Graffiti of Bîgeh.</SectionTitle>
      <p className="dropcap text-[1.05rem] leading-relaxed">{g.demotic.text}</p>
      <p className="mt-5 text-[1.02rem] leading-relaxed">
        <span className="smallcaps">No. 8.</span> {g.demotic.no8}
      </p>
      <p className="mt-3">
        <Cite source={g.demotic.source} page={g.demotic.page} />
      </p>

      <Ornament className="mt-10" />
      <h3 className="font-display caps text-center text-xl">Greek Inscription.</h3>
      <p className="mt-5 text-[1.02rem] leading-relaxed">{g.greek.intro}</p>
      <p className="mt-2 text-[1.02rem]">{g.greek.dating}</p>
      <table className="mx-auto mt-6 text-[1rem]">
        <tbody>
          {g.greek.lines.map(([gr, en]) => (
            <tr key={gr}>
              <td className="pr-10 font-display tracking-wide">{gr}</td>
              <td className="italic text-ink-700">{en}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-center text-xs italic text-ink-500">
        Lines 5–9 of the transcription (patronymics and place-name) are omitted here; see the source.
      </p>
      <p className="mt-4 text-right">
        <Cite source={g.greek.source} page={g.greek.page} />
      </p>
    </Sheet>
  )
}

function Plates({ onOpen }) {
  return (
    <Sheet id="plates" tone="paper-dark">
      <RunningHead left="Bîgeh." right="Plates." />
      <SectionTitle sub="Heliogravure plates from the 1915 volume. An asterisk denotes the author’s photographs.">List of Plates.</SectionTitle>
      <div className="columns-1 gap-6 sm:columns-2 [&>*]:mb-6 [&>*]:break-inside-avoid">
        {PLATES.map((p) => (
          <PlateFigure key={p.id} plate={p} onOpen={onOpen} />
        ))}
      </div>
      <p className="mt-4 text-center text-xs italic text-ink-500">
        Captions quoted from Blackman’s List of Plates, pp. 71–72. <Cite source="blackman" />
      </p>
    </Sheet>
  )
}

function Context() {
  return (
    <Sheet id="context">
      <RunningHead left="The Abaton." right="Island of Bîgeh." />
      <SectionTitle sub="What published sources say about the island and its sanctuary.">The Abaton.</SectionTitle>
      {CONTEXT.map((block) => (
        <div key={block.source} className="mb-8">
          {block.quotes.map((q) => (
            <p key={q} className="mb-3 text-[1.05rem] leading-relaxed">
              «&nbsp;{q}&nbsp;»
            </p>
          ))}
          <Cite source={block.source} />
        </div>
      ))}

      <Ornament />
      <h3 className="font-display caps text-center text-lg">Afterward.</h3>
      <p className="mt-4 text-sm italic text-ink-700">{AFTERWARD.note}</p>
      {AFTERWARD.quotes.map((q) => (
        <p key={q} className="mt-3 text-[1.05rem] leading-relaxed">
          «&nbsp;{q}&nbsp;»
        </p>
      ))}
      <p className="mt-3">
        <Cite source={AFTERWARD.source} />
      </p>
    </Sheet>
  )
}

function Sources() {
  return (
    <Sheet id="sources">
      <RunningHead left="Index of authorities quoted." right="Sources." />
      <SectionTitle sub="Every passage on this page is quoted from one of the works below.">Index of Authorities Quoted.</SectionTitle>
      <ol className="space-y-4">
        {FURTHER_READING.map((id) => {
          const s = SOURCES[id]
          return (
            <li key={id} className="border-b border-ink-300/40 pb-4 text-[0.98rem] leading-relaxed">
              <span className="smallcaps text-ink-700">{s.short}. </span>
              {s.citation}{' '}
              <a href={s.url} target="_blank" rel="noreferrer" className="break-all text-vermilion-dark underline underline-offset-4">
                {s.url}
              </a>
              {s.note && <p className="mt-1 text-sm italic text-ink-500">{s.note}</p>}
            </li>
          )
        })}
      </ol>
      <p className="mt-8 text-center text-xs text-ink-500">
        Blackman’s volume is in the public domain. Wikipedia text is CC BY-SA 4.0. Other works are cited for reference only.
      </p>
    </Sheet>
  )
}

export default function App() {
  const [index, setIndex] = useState(-1)
  const gallery = [{ id: 'plate-01-plan', num: 'I', caption: PLAN.caption }, ...PLATES]

  const open = useCallback((plate) => {
    const i = gallery.findIndex((p) => p.id === plate.id)
    setIndex(i)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps
  const close = useCallback(() => setIndex(-1), [])
  const step = useCallback((d) => setIndex((i) => (i + d + gallery.length) % gallery.length), [gallery.length])

  return (
    <div className="leather min-h-screen">
      <Nav />
      <Cover />
      <main className="px-3 pb-16 sm:px-6">
        <TitlePage />
        <Preface />
        <Introduction onOpen={open} />
        <Plan onOpen={open} />
        <Gate onOpen={open} />
        <Doors onOpen={open} />
        <Graffiti />
        <Plates onOpen={open} />
        <Context />
        <Sources />
      </main>
      <footer className="caps py-8 text-center text-[0.65rem] text-paper-300">
        The Gate of Isis · Bîgeh, Aswan · Built with React and Tailwind CSS
      </footer>
      <Lightbox plates={gallery} index={index} onClose={close} onStep={step} />
    </div>
  )
}
