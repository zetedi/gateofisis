import { useEffect, useMemo, useRef, useState } from 'react'
import ModelViewer from './components/ModelViewer.jsx'
import Icon, { GateMark } from './components/Icons.jsx'
import { useLocale } from './Locale.jsx'

const asset = (file) => `${import.meta.env.BASE_URL}${file}`
const modelArabic = [
  {
    title: 'البوابة والموقع المحيط',
    shortTitle: 'الموقع الكامل',
    subtitle: 'البوابة وسقفها في نموذج واحد',
    description:
      'البوابة وسقفها المُحاذى ودرجات المدخل والرصف والأعمدة والأحجار المتناثرة معًا. أُغلقت الفجوات الصغيرة حول اتصال السقف.',
    record: 'المسح التصويري',
    note: '١٬٠٥٤ صورة متحاذية · السقف والمحيط في نموذج واحد · فواصل السقف والفجوات الصغيرة مُغلقة · اختر التفاصيل الأصلية لعرض خامات البوابة بدقة 8K.',
  },
  {
    title: 'البوابة والمنصة المطلة على الماء',
    shortTitle: 'المسح المرجعي للبوابة',
    subtitle: 'مرجع Polycam منقّح',
    description: 'البوابة وأسطحها الحجرية والمنصة المصوّرة المطلة على الماء.',
    record: 'Polycam · ٢٨ سبتمبر',
    note: 'أسطح الحجر وخاماته كما سُجّلت. أُزيلت أشكال الأشخاص العابرة؛ وتعكس الحواف المفتوحة حدود التصوير.',
  },
  {
    title: 'الأعمدة والرصف والأحجار المتناثرة',
    shortTitle: 'المسح المرجعي للمحيط',
    subtitle: 'مرجع Polycam منقّح',
    description: 'بقايا الأعمدة وأسطح الأرض والشظايا الحجرية المتناثرة.',
    record: 'Polycam · ٢٨ سبتمبر',
    note: 'أسطح الحجر وخاماته كما سُجّلت. أُزيلت أشكال الأشخاص العابرة؛ وتعكس الحواف المفتوحة حدود التصوير.',
  },
  {
    title: 'أعلى البوابة',
    shortTitle: 'أعلى البوابة',
    subtitle: 'مرجع مستقل للجزء العلوي',
    description:
      'المسح الأصلي المنفصل لأعلى البوابة. أُدرجت نسخة مُحاذاة منه في نموذج الموقع الكامل.',
    record: 'Polycam · ٢٨ سبتمبر',
    note: 'المسح الأصلي محفوظ للمقارنة. اختر الموقع الكامل لرؤية السقف المُحاذى مع الفواصل المُغلقة.',
  },
]

function PhotoDialog({ photo, close }) {
  const { t, locale } = useLocale()
  const dialog = useRef(null)
  const [zoom, setZoom] = useState(false)
  useEffect(() => {
    if (photo) dialog.current.showModal()
    else dialog.current.close()
  }, [photo])
  return (
    <dialog
      className="survey-dialog"
      ref={dialog}
      aria-labelledby="survey-photo-title"
      onCancel={close}
      onClick={(e) => {
        if (e.target === dialog.current) close()
      }}
    >
      {photo && (
        <div className="survey-dialog-inner">
          <button
            className="dialog-close"
            onClick={close}
            aria-label={t('Close photograph', 'إغلاق الصورة')}
            autoFocus
          >
            <Icon name="close" />
          </button>
          <div
            className={`photo-inspector ${zoom ? 'is-zoomed' : ''}`}
            tabIndex={0}
            aria-label={t(
              'Photograph. Scroll to inspect when enlarged.',
              'الصورة. مرّر لاستكشافها عند التكبير.',
            )}
          >
            <img
              src={asset(photo.image)}
              alt={locale === 'ar' ? photo.titleAr : photo.title}
            />
          </div>
          <div className="photo-information">
            <span className="eyebrow">
              {t('FIELD PHOTOGRAPH', 'صورة ميدانية')}
            </span>
            <h3 id="survey-photo-title">
              {locale === 'ar' ? photo.titleAr : photo.title}
            </h3>
            <p>{locale === 'ar' ? photo.dateAr : photo.date}</p>
            <button
              className="photo-zoom"
              aria-pressed={zoom}
              onClick={() => setZoom(!zoom)}
            >
              <Icon name={zoom ? 'minus' : 'plus'} size={17} />
              {zoom
                ? t('Fit photograph', 'عرض الصورة كاملة')
                : t('Original pixels · 100%', 'البكسلات الأصلية · ١٠٠٪')}
            </button>
            <p>
              {zoom
                ? t(
                    'Scroll horizontally and vertically to inspect the carving.',
                    'مرّر أفقيًا ورأسيًا لاستكشاف النقش.',
                  )
                : t(
                    'Open the original pixels to inspect the hieroglyphs.',
                    'اعرض البكسلات الأصلية لفحص النقوش الهيروغليفية.',
                  )}
            </p>
            <a
              className="photo-original"
              href={asset(photo.image)}
              target="_blank"
              rel="noreferrer"
            >
              {t(
                'Open full-resolution photograph ↗',
                'فتح الصورة بدقتها الكاملة ↗',
              )}
            </a>
            <p className="photo-source">
              {t('Source:', 'المصدر:')} <bdi>{photo.source}</bdi>
            </p>
          </div>
        </div>
      )}
    </dialog>
  )
}

export default function GatePage() {
  const { locale, t } = useLocale()
  const [survey, setSurvey] = useState(null)
  const [loadError, setLoadError] = useState(false)
  const [selection, setSelection] = useState(0)
  const [quality, setQuality] = useState('standard')
  const [mode, setMode] = useState('texture')
  const [view, setView] = useState(() => window.location.hash === '#3d-roof' ? 'roof' : 'overview')
  const [rotating, setRotating] = useState(false)
  const [stats, setStats] = useState(null)
  const [photos, setPhotos] = useState([])
  const [photo, setPhoto] = useState(null)
  const [showHelp, setShowHelp] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    fetch(asset('models/survey.json'), { signal: controller.signal, cache: 'no-cache' })
      .then((r) => {
        if (!r.ok) throw new Error('Survey unavailable')
        return r.json()
      })
      .then(setSurvey)
      .catch((e) => {
        if (e.name !== 'AbortError') setLoadError(true)
      })
    fetch(asset('survey/photographs.json'), { signal: controller.signal })
      .then((r) => r.json())
      .then(setPhotos)
      .catch(() => {})
    return () => controller.abort()
  }, [])
  useEffect(() => {
    if (photos.length && ['#3d-inscriptions', '#3d-archive', '#3d-roof'].includes(window.location.hash)) {
      document.getElementById(window.location.hash.slice(1))?.scrollIntoView({ behavior: 'instant', block: 'start' })
    }
  }, [photos])
  const sourceModel = survey?.models[selection]
  const model = useMemo(() => {
    if (!sourceModel) return null
    const result = {
      ...sourceModel,
      ...(locale === 'ar' ? modelArabic[selection] : {}),
    }
    if (quality === 'detail' && sourceModel.detailFile)
      return {
        ...result,
        id: `${result.id}-detail`,
        file: result.detailFile,
        bytes: result.detailBytes,
      }
    if (quality === 'high' && sourceModel.highFile)
      return {
        ...result,
        id: `${result.id}-high`,
        file: result.highFile,
        bytes: result.highBytes,
      }
    return result
  }, [sourceModel, quality, locale, selection])
  const choose = (index) => {
    setSelection(index)
    setQuality('standard')
    setView('overview')
    setRotating(false)
    setStats(null)
  }
  const viewpoints = sourceModel?.focus
    ? [
        ['overview', t('Gate & stairs', 'البوابة والدرج')],
        ['detail', t('Gate close-up', 'البوابة عن قرب')],
        ['inscriptions', t('Inscriptions', 'النقوش')],
        ['roof', t('Roof', 'السقف')],
        ['site', t('Whole site', 'الموقع كاملًا')],
        ['front', t('Front', 'الأمام')],
        ['back', t('Reverse', 'الخلف')],
        ['top', t('Above', 'الأعلى')],
      ]
    : [
        ['overview', t('Perspective', 'منظور')],
        ['front', t('Front', 'الأمام')],
        ['back', t('Reverse', 'الخلف')],
        ['top', t('Above', 'الأعلى')],
      ]
  const download = sourceModel?.downloadFile || model?.file
  const downloadBytes = sourceModel?.downloadBytes || model?.bytes
  const detailSize = new Intl.NumberFormat(locale).format(
    Math.round((sourceModel?.detailBytes || 0) / 1e6),
  )
  const photoSection = (items, inscriptions) =>
    items.length > 0 && (
      <section
        className="field-photographs"
        id={inscriptions ? '3d-inscriptions' : undefined}
        aria-labelledby={inscriptions ? 'inscription-title' : 'field-title'}
      >
        <div className="field-heading">
          <div>
            <p className="eyebrow">
              <span className="section-number">
                {inscriptions ? '02' : '04'}
              </span>
              {inscriptions
                ? t('THE INSCRIBED STONE', 'الحجر المنقوش')
                : t('THE PHOTOGRAPHIC RECORD', 'السجل الفوتوغرافي')}
            </p>
            <h2 id={inscriptions ? 'inscription-title' : 'field-title'}>
              {inscriptions
                ? t('Read the surface.', 'اقرأ سطح الحجر.')
                : t('From the field.', 'من الميدان.')}
            </h2>
          </div>
          <p>
            {inscriptions
              ? t(
                  'Original photographs, at full resolution. Select a carving to inspect its hieroglyphs.',
                  'صور أصلية بدقتها الكاملة. اختر نقشًا لفحص علاماته الهيروغليفية.',
                )
              : t(
                  'The photographs behind the geometry. Select an image to look closer.',
                  'الصور التي يستند إليها النموذج. اختر صورة لرؤية أدق.',
                )}
          </p>
        </div>
        <div className="photo-grid">
          {items.map((item, i) => (
            <button
              className="survey-photo"
              aria-label={`${t('View photograph:', 'عرض الصورة:')} ${locale === 'ar' ? item.titleAr : item.title}`}
              key={item.id}
              onClick={() => setPhoto(item)}
            >
              <div>
                <img src={asset(item.thumbnail)} alt="" loading="lazy" />
                <span className="photo-expand">
                  <Icon name="expand" size={18} />
                </span>
              </div>
              <span className="photo-caption">
                <span>{String(i + 1).padStart(2, '0')}</span>
                {locale === 'ar' ? item.titleAr : item.title}
                <Icon name="arrow" size={16} />
              </span>
            </button>
          ))}
        </div>
      </section>
    )
  return (
    <main className="gate-page" id="3d-main">
      <section className="survey-intro" id="3d" aria-labelledby="survey-title">
        <div>
          <p className="eyebrow">
            <span className="eyebrow-line" />
            {t('BÎGEH, ASWAN', 'بيجة، أسوان')}
            <span className="eyebrow-divider">/</span>
            {t('THE DIGITAL SURVEY', 'المسح الرقمي')}
          </p>
          <h1 id="survey-title">
            {t('The gate, in', 'البوابة، في')}
            <br />
            <em>{t('three dimensions.', 'ثلاثة أبعاد.')}</em>
          </h1>
        </div>
        <div className="survey-intro-aside">
          <span className="edition-number">
            {t('FIELD RECORD — 2026', 'السجل الميداني — ٢٠٢٦')}
          </span>
          <p>
            {t(
              'Move around the monument, trace its carved surfaces, and explore the stones that surround it.',
              'تحرّك حول الأثر، وتتبّع أسطحه المنقوشة، واستكشف الأحجار المحيطة به.',
            )}
          </p>
          <a href="#3d-inscriptions">
            {t('Inspect the hieroglyphs', 'تأمّل النقوش الهيروغليفية')}
            <Icon name="arrow" size={17} />
          </a>
        </div>
      </section>
      <section
        className="survey-workspace"
        id="3d-roof"
        aria-label={t('Interactive 3D survey', 'المسح التفاعلي ثلاثي الأبعاد')}
      >
        <div className="workspace-heading">
          <span>
            <span className="section-number">01</span>
            {t('THE SPATIAL RECORD', 'السجل المكاني')}
          </span>
          <button
            onClick={() => setShowHelp(!showHelp)}
            aria-expanded={showHelp}
            aria-controls="viewer-instructions"
          >
            <Icon name="info" size={16} />
            {t('How to explore', 'كيفية الاستكشاف')}
          </button>
        </div>
        {showHelp && (
          <div id="viewer-instructions" className="viewer-instructions">
            <p>
              {t(
                'Drag to orbit, scroll or pinch to zoom, and right-drag or use two fingers to pan. Choose a viewpoint to return to a fixed angle.',
                'اسحب للدوران، ومرّر أو باعد بين إصبعيك للتكبير، واسحب بالزر الأيمن أو بإصبعين للتحريك. اختر نقطة رؤية للعودة إلى زاوية ثابتة.',
              )}
            </p>
            <p>
              {t(
                'Keyboard: focus the model, then use arrows to rotate, + / − to zoom, and R to reset. Choose Original detail to examine the gate at its captured resolution.',
                'باستخدام لوحة المفاتيح: ركّز على النموذج، ثم استخدم الأسهم للدوران و + / − للتكبير و R لإعادة العرض. اختر التفاصيل الأصلية لفحص البوابة بدقة التصوير.',
              )}
            </p>
            <button
              onClick={() => setShowHelp(false)}
              aria-label={t('Close instructions', 'إغلاق التعليمات')}
            >
              <Icon name="close" size={17} />
            </button>
          </div>
        )}
        {model ? (
          <>
            <div className="workspace-body">
              <aside className="survey-sidebar">
                <div className="sidebar-section">
                  <p className="control-label">
                    {t('EXPLORE THE SITE', 'استكشف الموقع')}
                  </p>
                  <div
                    className="survey-models"
                    role="group"
                    aria-label={t('Survey area', 'منطقة المسح')}
                  >
                    {survey.models.map((item, i) => (
                      <button
                        key={item.id}
                        className={i === selection ? 'selected' : ''}
                        aria-pressed={i === selection}
                        onClick={() => choose(i)}
                      >
                        <span className="model-number">
                          {String(i + 1).padStart(2, '0')}
                        </span>
                        <span>
                          {locale === 'ar'
                            ? modelArabic[i].shortTitle
                            : item.shortTitle}
                          <small>
                            {locale === 'ar'
                              ? modelArabic[i].subtitle
                              : item.subtitle}
                          </small>
                        </span>
                        <Icon name="arrow" size={16} />
                      </button>
                    ))}
                  </div>
                </div>
                <div className="sidebar-section surface-section">
                  <p className="control-label">{t('SURFACE', 'السطح')}</p>
                  <div
                    className="surface-options"
                    role="group"
                    aria-label={t('Surface display', 'عرض السطح')}
                  >
                    {[
                      ['texture', t('Photograph', 'الصورة')],
                      ['stone', t('Stone', 'الحجر')],
                      ['mesh', t('Mesh', 'الشبكة')],
                    ].map(([id, title]) => (
                      <button
                        key={id}
                        onClick={() => setMode(id)}
                        className={mode === id ? 'selected' : ''}
                        aria-pressed={mode === id}
                      >
                        <i className={`surface-swatch swatch-${id}`} />
                        {title}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="sidebar-detail">
                  <Icon name="layers" size={20} />
                  <p>{model.description}</p>
                  <dl>
                    <div>
                      <dt>{t('Geometry', 'الهندسة')}</dt>
                      <dd>
                        {stats
                          ? `${new Intl.NumberFormat(locale).format(stats.triangles)} ${t('faces', 'وجه')}`
                          : t('Loading…', 'جارٍ التحميل…')}
                      </dd>
                    </div>
                    <div>
                      <dt>{t('Record', 'السجل')}</dt>
                      <dd>{model.record}</dd>
                    </div>
                  </dl>
                </div>
                <a className="model-download" href={asset(download)} download>
                  <span>
                    <Icon name="download" size={18} />
                    {sourceModel.downloadFile
                      ? t('Download model · 2K', 'تنزيل النموذج · 2K')
                      : t('Download source scan', 'تنزيل المسح الأصلي')}
                  </span>
                  <small>
                    GLB ·{' '}
                    {(
                      downloadBytes / 1e6
                    ).toFixed(1)}{' '}
                    MB
                  </small>
                </a>
              </aside>
              <div className="viewer-column">
                {sourceModel.highFile && (
                  <div className="detail-quality">
                    <label htmlFor="survey-quality">
                      {t('DETAIL', 'التفاصيل')}
                    </label>
                    <select
                      id="survey-quality"
                      value={quality}
                      onChange={(e) => {
                        setQuality(e.target.value)
                        setStats(null)
                      }}
                    >
                      <option value="standard">
                        {t('Quick view · 2K', 'عرض سريع · 2K')}
                      </option>
                      <option value="high">
                        {t('High detail · 4K', 'تفاصيل عالية · 4K')}
                      </option>
                      {sourceModel.detailFile && (
                        <option value="detail">
                          {t(
                            `Original detail · 8K · ${detailSize} MB`,
                            `التفاصيل الأصلية · 8K · ${detailSize} م.ب.`,
                          )}
                        </option>
                      )}
                    </select>
                  </div>
                )}
                <ModelViewer
                  key={`${model.id}-${locale}`}
                  model={model}
                  mode={mode}
                  view={view}
                  rotating={rotating}
                  onRotateChange={setRotating}
                  onStats={setStats}
                  onViewChange={setView}
                />
                <div className="viewpoint-bar">
                  <div
                    role="group"
                    aria-label={t('Camera viewpoint', 'نقطة الرؤية')}
                  >
                    {viewpoints.map(([id, title]) => (
                      <button
                        key={id}
                        aria-pressed={view === id}
                        className={view === id ? 'selected' : ''}
                        onClick={() => {
                          setView(id)
                          setRotating(false)
                        }}
                      >
                        {title}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="workspace-caption">
              <p>
                <span className="status-dot" />
                {model.note}
              </p>
              <a
                className="mobile-model-download"
                href={asset(download)}
                download
                aria-label={t(
                  'Download model as GLB',
                  'تنزيل النموذج بصيغة GLB',
                )}
              >
                <Icon name="download" size={16} />
                GLB
              </a>
            </div>
          </>
        ) : (
          <div className="survey-pending" role="status">
            {loadError ? (
              <>
                {t('The survey could not be loaded.', 'تعذّر تحميل المسح.')}{' '}
                <button onClick={() => window.location.reload()}>
                  {t('Reload the page', 'إعادة تحميل الصفحة')}
                </button>
              </>
            ) : (
              t('Opening the field archive…', 'جارٍ فتح الأرشيف الميداني…')
            )}
          </div>
        )}
      </section>
      {sourceModel?.detailFile && (
        <div className="detail-invitation">
          <div>
            <h2>
              {t('Closer to the carved stone.', 'أقرب إلى الحجر المنقوش.')}
            </h2>
            <p>
              {t(
                'The captured gate geometry, eleven 8K textures, and the aligned roof. Open the original detail, then zoom into a carved surface.',
                'هندسة البوابة المصوّرة، وإحدى عشرة خريطة خامات بدقة 8K، والسقف المُحاذى. افتح التفاصيل الأصلية، ثم اقترب من السطح المنقوش.',
              )}
            </p>
          </div>
          <button
            aria-pressed={quality === 'detail'}
            onClick={() => {
              setQuality('detail')
              setView('inscriptions')
              setStats(null)
              document
                .querySelector('.survey-workspace')
                ?.scrollIntoView({ block: 'start' })
            }}
          >
            <Icon name="layers" size={18} />
            {quality === 'detail'
              ? t('Original detail selected', 'التفاصيل الأصلية محدّدة')
              : t(
                  `Open original detail · ${detailSize} MB`,
                  `فتح التفاصيل الأصلية · ${detailSize} م.ب.`,
                )}
          </button>
        </div>
      )}
      {photoSection(
        photos.filter((p) => p.inscription),
        true,
      )}
      <section className="survey-record" id="3d-archive">
        <div>
          <p className="eyebrow">
            <span className="section-number">03</span>
            {t('A RECORD OF WHAT REMAINS', 'سجلّ لما بقي')}
          </p>
          <h2>{t('Every surface has a story.', 'لكل سطح حكاية.')}</h2>
          <p className="record-intro">
            {t(
              'The gate belongs to a larger landscape. The pavement, the columns, the scattered blocks: each is part of this digital field record.',
              'البوابة جزء من مشهد أوسع. الرصف والأعمدة والكتل المتناثرة: كلّها أجزاء من هذا السجل الميداني الرقمي.',
            )}
          </p>
        </div>
        <div className="record-details">
          <dl className="record-facts">
            <div>
              <dt>{t('Photographic input', 'الصور المستخدمة')}</dt>
              <dd>
                {(survey?.photoCount || 1055).toLocaleString(locale)}
                <small>
                  {t('unique survey photographs', 'صورة ميدانية فريدة')}
                </small>
              </dd>
            </div>
            <div>
              <dt>{t('Supporting surveys', 'المسوحات المساندة')}</dt>
              <dd>
                03
                <small>
                  {t('textured Polycam scans', 'مسوحات Polycam بخامات مصوّرة')}
                </small>
              </dd>
            </div>
            <div>
              <dt>{t('Field campaign', 'الحملة الميدانية')}</dt>
              <dd>
                09 / 26<small>{t('September 2026', 'سبتمبر ٢٠٢٦')}</small>
              </dd>
            </div>
          </dl>
          <div className="record-method">
            <p className="control-label">
              {t('ABOUT THIS RECORD', 'عن هذا السجل')}
            </p>
            <p>
              {t(
                survey?.method ||
                  'The original scans preserve captured stone surfaces.',
                'أُعيد بناء البوابة والأحجار المحيطة من ١٬٠٥٤ صورة متحاذية، وأُضيف مسح Polycam لأعلى البوابة بعد محاذاته. أُغلقت فواصل السقف والفجوات الصغيرة بأسطح ترميم منفصلة وقابلة للتحرير في ملف Blender. تحتفظ البوابة بهندستها المصوّرة وخاماتها الأصلية بدقة 8K.',
              )}
            </p>
            <p className="record-caveat">
              {t(
                survey?.limitation || 'Gaps reflect capture coverage.',
                'الأسطح التي تُغلق فجوات المسح مستكملة بالاستيفاء وليست تفاصيل أثرية مصوّرة؛ أُخذت ألوانها من الحجر المجاور، ولم تُولَّد نقوش جديدة. تبقى فتحة البوابة وحواف نطاق التصوير مفتوحة. لم تُراجَع الأبعاد مقابل نقاط ضبط مساحية.',
              )}
            </p>
            <a
              href={asset('models/survey.json')}
              target="_blank"
              rel="noreferrer"
            >
              {t('View the survey record', 'عرض سجل المسح')}
              <Icon name="arrow" size={15} />
            </a>
          </div>
        </div>
      </section>
      {photoSection(
        photos.filter((p) => !p.inscription),
        false,
      )}
      <section className="book-crosslink">
        <GateMark />
        <div>
          <p className="eyebrow">{t('ANOTHER WAY TO LOOK', 'نظرة أخرى')}</p>
          <h2>
            {t('Return to the written record.', 'عُد إلى السجل المكتوب.')}
          </h2>
          <p>
            {t(
              'Aylward M. Blackman’s 1915 volume, its inscriptions and photographic plates.',
              'مجلد أيلورد م. بلاكمان الصادر سنة ١٩١٥، بنقوشه ولوحاته المصوّرة.',
            )}
          </p>
        </div>
        <a href="#title">
          {t('Open the book', 'افتح الكتاب')}
          <Icon name="arrow" size={20} />
        </a>
      </section>
      <footer className="survey-footer">
        <span>
          {t('THE GATE OF ISIS · BÎGEH, ASWAN', 'بوابة إيزيس · بيجة، أسوان')}
        </span>
        <span>
          {t('A place. A record. A closer look.', 'مكان. سجلّ. نظرة أقرب.')}
        </span>
        <a href="#3d">{t('Back to the gate ↑', 'عُد إلى البوابة ↑')}</a>
      </footer>
      <PhotoDialog
        key={photo?.id || 'closed'}
        photo={photo}
        close={() => setPhoto(null)}
      />
    </main>
  )
}
