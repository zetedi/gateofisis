export default function Icon({ name, size = 20, ...props }) {
  const paths = {
    orbit: <><ellipse cx="12" cy="12" rx="10" ry="4.5" transform="rotate(-35 12 12)" /><circle cx="12" cy="12" r="2" /><path d="m19 3 1 4-4-1" /></>,
    reset: <><path d="M4 10a8 8 0 1 1 1.6 7M4 4v6h6" /></>,
    expand: <><path d="M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6" /></>,
    plus: <path d="M12 5v14M5 12h14" />,
    minus: <path d="M5 12h14" />,
    arrow: <path d="M4 12h16m-6-6 6 6-6 6" />,
    download: <><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5" /></>,
    chevron: <path d="m7 10 5 5 5-5" />,
    cube: <><path d="m12 2 9 5v10l-9 5-9-5V7zm0 10v10M3 7l9 5 9-5M7.5 4.5l9 5V14" /></>,
    book: <><path d="M12 5C9 3 5 3 2 4v15c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1Zm0 0v15" /></>,
    close: <path d="m5 5 14 14M5 19 19 5" />,
    info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v6m0-10v1" /></>,
    layers: <><path d="m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 17l10 5 10-5" /></>,
    photo: <><rect x="3" y="3" width="18" height="18" rx="1" /><circle cx="8" cy="8" r="1.5" /><path d="m3 18 6-6 4 4 3-3 5 5" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><path d="M12 1v2m0 18v2M1 12h2m18 0h2M4 4l1.5 1.5m13 13L20 20M4 20l1.5-1.5m13-13L20 4" /></>,
    pause: <path d="M8 5v14M16 5v14" />,
  }
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.cube}</svg>
}

export function GateMark() {
  return <svg viewBox="0 0 40 44" fill="none" stroke="currentColor" strokeWidth="1" aria-hidden="true"><path d="M4 40h32M7 40V8h26v32M12 40V14h16v26M5 8V4h30v4M16 40V24a4 4 0 0 1 8 0v16M7 19h5m16 0h5M7 30h5m16 0h5" /><path d="M9 4V1m22 3V1M3 43h34" /></svg>
}
