"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { CAT_ICONS } from "@/lib/icons";

interface LangMeta {
  code: string;
  name: string;
  native: string;
}

const CATEGORIES = [
  { slug: "mahila",       key: "cat.women",       count: 381  },
  { slug: "student",      key: "cat.student",      count: 748  },
  { slug: "farmer",       key: "cat.farmer",       count: 400  },
  { slug: "employment",   key: "cat.employment",   count: 459  },
  { slug: "disability",   key: "cat.disability",   count: 289  },
  { slug: "pension",      key: "cat.pension",      count: 259  },
  { slug: "health",       key: "cat.health",       count: 184  },
  { slug: "child",        key: "cat.child",        count: 182  },
  { slug: "tribal",       key: "cat.tribal",       count: 157  },
  { slug: "bpl",          key: "cat.bpl",          count: 141  },
  { slug: "entrepreneur", key: "cat.entrepreneur", count: 121  },
  { slug: "minority",     key: "cat.minority",     count: 87   },
  { slug: "housing",      key: "cat.housing",      count: 69   },
  { slug: "maternity",    key: "cat.maternity",    count: 40   },
  { slug: "elderly",      key: "cat.elderly",      count: 24   },
];

interface NavProps {
  lang: string;
  languages: LangMeta[];
  langNative: string;
  translations: Record<string, string>;
}

function t(tr: Record<string, string>, key: string): string {
  return tr[key] ?? key;
}

export default function Nav({ lang, languages, langNative, translations: tr }: NavProps) {
  const pathname = usePathname();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [langOpen, setLangOpen]     = useState(false);
  const [yojanaOpen, setYojanaOpen] = useState(false);
  const langRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (langRef.current && !langRef.current.contains(e.target as Node)) {
        setLangOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Close drawer on route change
  useEffect(() => {
    setDrawerOpen(false);
    setLangOpen(false);
  }, [pathname]);

  // Prevent body scroll when drawer open
  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  // Path base (strip lang prefix) for language switcher
  const pathBase = pathname.replace(/^\/[a-z]{2,3}(\/|$)/, "/") || "/";

  function isActive(href: string) {
    return pathname.startsWith(href) && href.length > 4;
  }

  return (
    <>
      <nav className="nav" role="navigation" aria-label="Main navigation">
        <div className="tricolor-strip" aria-hidden="true" />
        <div className="wrap nav-bar">

          {/* Brand */}
          <Link href={`/${lang}/`} className="nav-brand" aria-label="Aarambha Haq Home">
            <div className="nav-mark" aria-hidden="true">
              <span className="a" /><span className="b" /><span className="c" />
            </div>
            <div className="nav-name">
              Aarambha Haq
              <small>{t(tr, "nav.tagline")}</small>
            </div>
          </Link>

          {/* Desktop mega-nav */}
          <div className="nav-menu" role="menubar">

            {/* Yojana mega-dropdown */}
            <div
              className="nav-item"
              onMouseEnter={() => setYojanaOpen(true)}
              onMouseLeave={() => setYojanaOpen(false)}
            >
              <button
                className={`nav-link ${isActive(`/${lang}/yojana`) ? "active" : ""}`}
                aria-haspopup="true"
                aria-expanded={yojanaOpen}
              >
                {t(tr, "nav.all_schemes")}
                <span aria-hidden="true" style={{ fontSize: 9, marginLeft: 2 }}>▾</span>
              </button>

              {yojanaOpen && (
                <div className="mega-drop" style={{ display: "grid" }} role="menu">
                  <div className="mega-label">{t(tr, "nav.all_schemes")}</div>
                  {CATEGORIES.map((c) => (
                    <Link
                      key={c.slug}
                      href={`/${lang}/yojana/${c.slug}`}
                      className="mega-link"
                      role="menuitem"
                    >
                      <span
                        className="icon"
                        aria-hidden="true"
                        style={{
                          width: 32, height: 32, borderRadius: 8,
                          background: "rgba(11,31,77,.07)",
                          display: "grid", placeItems: "center",
                          color: "var(--navy)", flexShrink: 0,
                        }}
                      >
                        {CAT_ICONS[c.slug]}
                      </span>
                      <span>
                        {t(tr, c.key)}
                        <span className="count" style={{ display: "block" }}>{c.count}</span>
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            <Link href={`/${lang}/check`}
              className={`nav-link ${isActive(`/${lang}/check`) ? "active" : ""}`}>
              {t(tr, "nav.check_eligibility")}
            </Link>
            <Link href={`/${lang}/haq`}
              className={`nav-link ${isActive(`/${lang}/haq`) ? "active" : ""}`}>
              {t(tr, "nav.your_rights")}
            </Link>
            <Link href={`/${lang}/about`}
              className={`nav-link ${isActive(`/${lang}/about`) ? "active" : ""}`}>
              {t(tr, "nav.about")}
            </Link>
          </div>

          {/* Right actions */}
          <div className="nav-actions">

            {/* Language picker */}
            <div className="lang-picker" ref={langRef}>
              <button
                className="lang-btn"
                onClick={() => setLangOpen((p) => !p)}
                aria-haspopup="listbox"
                aria-expanded={langOpen}
                aria-label={`Change language — ${langNative}`}
              >
                <span>{langNative}</span>
                <span aria-hidden="true">▾</span>
              </button>
              {langOpen && (
                <div className="lang-drop open" role="listbox">
                  {languages.map((l) => (
                    <Link
                      key={l.code}
                      href={`/${l.code}${pathBase}`}
                      role="option"
                      aria-selected={l.code === lang}
                      className={`lang-opt ${l.code === lang ? "active" : ""}`}
                    >
                      <span className="native">{l.native}</span>
                      <span className="en-name">{l.name}</span>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            <Link href={`/${lang}/check`} className="btn btn-primary nav-cta">
              {t(tr, "nav.check_eligibility")}
            </Link>

            <button
              className="hamburger"
              onClick={() => setDrawerOpen(true)}
              aria-label="Open menu"
              aria-expanded={drawerOpen}
              aria-controls="navDrawer"
            >
              <svg width="20" height="14" viewBox="0 0 20 14" fill="none" aria-hidden="true">
                <rect width="20" height="2" rx="1" fill="currentColor" />
                <rect y="6" width="14" height="2" rx="1" fill="currentColor" />
                <rect y="12" width="20" height="2" rx="1" fill="currentColor" />
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Drawer */}
      <div
        className={`drawer ${drawerOpen ? "open" : ""}`}
        id="navDrawer"
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
      >
        <div
          className="drawer-overlay"
          onClick={() => setDrawerOpen(false)}
          aria-hidden="true"
        />
        <div className="drawer-panel">
          <button
            className="drawer-close"
            onClick={() => setDrawerOpen(false)}
            aria-label="Close menu"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
              <path d="M1 1l16 16M17 1L1 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>

          <Link href={`/${lang}/`} className="nav-brand" style={{ marginBottom: "var(--s5)" }}>
            <div className="nav-mark" aria-hidden="true">
              <span className="a" /><span className="b" /><span className="c" />
            </div>
            <div className="nav-name">Aarambha Haq</div>
          </Link>

          <Link href={`/${lang}/check`}  className="drawer-link">{t(tr, "nav.check_eligibility")}</Link>
          <Link href={`/${lang}/yojana`} className="drawer-link">{t(tr, "nav.all_schemes")}</Link>
          <Link href={`/${lang}/haq`}    className="drawer-link">{t(tr, "nav.your_rights")}</Link>
          <Link href={`/${lang}/about`}  className="drawer-link">{t(tr, "nav.about")}</Link>

          <p style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: ".07em",
                      color: "rgba(255,255,255,.35)", margin: "var(--s5) 0 var(--s2)" }}>
            {t(tr, "nav.all_schemes")}
          </p>
          <div className="drawer-cat-grid">
            {CATEGORIES.slice(0, 10).map((c) => (
              <Link key={c.slug} href={`/${lang}/yojana/${c.slug}`} className="drawer-cat">
                <span style={{ color: "var(--saffron)", flexShrink: 0 }}>{CAT_ICONS[c.slug]}</span>
                <span style={{ fontSize: 12 }}>{t(tr, c.key)}</span>
              </Link>
            ))}
          </div>

          <p style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: ".07em",
                      color: "rgba(255,255,255,.35)", margin: "var(--s5) 0 var(--s2)" }}>
            Language / भाषा
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "var(--s2)" }}>
            {languages.map((l) => (
              <Link
                key={l.code}
                href={`/${l.code}${pathBase}`}
                style={{
                  fontSize: 12, padding: "5px 8px", borderRadius: 6,
                  textAlign: "center", border: "1px solid",
                  borderColor: l.code === lang ? "rgba(255,153,51,.4)" : "rgba(255,255,255,.12)",
                  background: l.code === lang ? "rgba(255,153,51,.18)" : "transparent",
                  color: l.code === lang ? "var(--saffron)" : "rgba(255,255,255,.6)",
                  fontWeight: l.code === lang ? 800 : 400,
                }}
              >
                {l.native}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
