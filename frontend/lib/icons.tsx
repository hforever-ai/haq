// Category SVG icons — shared by home page + Nav
// Stroke-based, 24x24 viewBox, strokeWidth 1.8, round caps

// Lottie file mapping per category slug (files live in /public/lottie/)
export const CAT_LOTTIE: Record<string, string> = {
  mahila:       "cat-mahila.json",
  student:      "cat-student.json",
  farmer:       "cat-farmer.json",
  employment:   "cat-employment.json",
  disability:   "cat-disability.json",
  pension:      "cat-pension.json",
  child:        "cat-child.json",
  tribal:       "cat-tribal.json",
  bpl:          "cat-bpl.json",
  entrepreneur: "cat-employment.json",
  minority:     "cat-minority.json",
  housing:      "cat-housing.json",
  maternity:    "cat-maternity.json",
  elderly:      "cat-pension.json",
  health:       "cat-disability.json",
};

function I({ children }: { children: React.ReactNode }) {
  return (
    <svg
      width="20" height="20" viewBox="0 0 24 24"
      fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export const CAT_ICONS: Record<string, React.ReactNode> = {
  mahila: <I><circle cx="12" cy="9" r="5" /><path d="M12 14v5M9.5 17h5" /></I>,
  student: <I><path d="M2 8.5L12 4l10 4.5L12 13z" /><path d="M6 11v4.5c0 1.7 2.7 2.8 6 2.8s6-1.1 6-2.8V11" /><line x1="22" y1="8.5" x2="22" y2="14" /></I>,
  farmer: <I><path d="M12 22V12" /><path d="M7 14c2-3.5 7-4 10-2" /><path d="M9 18c1-2.5 6-3 8-1" /><path d="M12 12c-1-3-5-4-8-2" /></I>,
  employment: <I><rect x="2" y="9" width="20" height="13" rx="2" /><path d="M8 9V7a2 2 0 012-2h4a2 2 0 012 2v2" /><line x1="12" y1="14" x2="12" y2="18" /><line x1="10" y1="16" x2="14" y2="16" /></I>,
  disability: <I><circle cx="12" cy="5" r="2.5" /><path d="M10 9h4l1.5 5.5H8.5z" /><path d="M9 22a5 5 0 005-5" /><path d="M17 22a5 5 0 00-3-4.5" /></I>,
  pension: <I><rect x="3" y="10" width="18" height="12" rx="2" /><path d="M7 10V8a5 5 0 0110 0v2" /><line x1="12" y1="14" x2="12" y2="18" /><line x1="10" y1="16" x2="14" y2="16" /></I>,
  health: <I><path d="M20.8 4.6a5.5 5.5 0 00-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 00-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 000-7.8z" /></I>,
  child: <I><circle cx="12" cy="6" r="3.5" /><path d="M9 10h6l.8 5H8.2z" /><path d="M10 15v6M14 15v6M8 21h8" /></I>,
  tribal: <I><path d="M12 22V12" /><path d="M12 12c0-4 4-8 8-6-1 4.5-4 7-8 6z" /><path d="M12 12c0-4-4-8-8-6 1 4.5 4 7 8 6z" /><path d="M10 18c1-1.5 4-1.5 4 0" /></I>,
  bpl: <I><path d="M3 9.5L12 3l9 6.5v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" /><rect x="9" y="13" width="6" height="9" /></I>,
  entrepreneur: <I><path d="M15 14c.2-1 .7-1.8 1.5-2.6C17.5 10.4 18 9 18 7.5A6 6 0 006 7.5c0 1.4.5 2.7 1.5 3.8.7.8 1.2 1.5 1.4 2.7" /><path d="M9 22h6M12 18v4M10 18h4" /></I>,
  minority: <I><circle cx="9" cy="7" r="3" /><circle cx="15" cy="7" r="3" /><path d="M3 22v-2a4 4 0 014-4h4" /><path d="M11 22v-2a4 4 0 014-4h2a4 4 0 014 4v2" /></I>,
  housing: <I><path d="M3 9.5L12 3l9 6.5v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" /><path d="M9 22V13h6v9" /><line x1="5" y1="13" x2="19" y2="13" /></I>,
  maternity: <I><circle cx="12" cy="5" r="2.5" /><path d="M9 9h6l-.5 5.5H9.5z" /><ellipse cx="12" cy="17" rx="3.5" ry="2.5" /><path d="M10 22v-2.5M14 22v-2.5" /></I>,
  elderly: <I><circle cx="12" cy="5" r="2.5" /><path d="M9 9h6v5l2 5" /><path d="M9 14l-2 5" /><path d="M17 19l1.5 3" /></I>,
};

// How-it-works step icons
export const STEP_ICONS = {
  form: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="5" y="2" width="14" height="20" rx="2" />
      <line x1="9" y1="8" x2="15" y2="8" />
      <line x1="9" y1="12" x2="15" y2="12" />
      <line x1="9" y1="16" x2="12" y2="16" />
    </svg>
  ),
  match: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3l1.8 4.9 5.2.4-3.9 3.3 1.3 5L12 14l-4.4 2.6 1.3-5L5 8.3l5.2-.4z" />
      <path d="M19 19l2.5 2.5" />
      <circle cx="17" cy="17" r="4" />
    </svg>
  ),
  apply: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  ),
};
