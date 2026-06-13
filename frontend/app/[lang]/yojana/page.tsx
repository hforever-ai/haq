import type { Metadata } from "next";
import { Suspense } from "react";
import Link from "next/link";
import Image from "next/image";
import { makeT } from "@/lib/i18n";
import { getSchemes } from "@/lib/api";
import SchemeCard from "@/components/scheme/SchemeCard";
import BrowseFilters from "@/components/scheme/BrowseFilters";
import MobileSearch from "@/components/scheme/MobileSearch";

interface Props {
  params: Promise<{ lang: string }>;
  searchParams: Promise<{ category?: string; state?: string; q?: string; level?: string; page?: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang } = await params;
  const t = makeT(lang);
  return {
    title: t("nav.all_schemes"),
    description: `2,754+ ${t("nav.all_schemes")} — ${t("hero.sub")}`,
  };
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

export default async function BrowsePage({ params, searchParams }: Props) {
  const { lang } = await params;
  const sp = await searchParams;
  const t = makeT(lang);

  const page = parseInt(sp.page ?? "1");
  const { schemes, total } = await getSchemes({
    category: sp.category,
    state: sp.state,
    q: sp.q,
    level: sp.level,
    page,
    size: 24,
  });

  const totalPages = Math.ceil(total / 24);
  const activeCategory = sp.category ?? "";

  return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>

      {/* ── Header ── */}
      {activeCategory ? (
        <div style={{ background: "var(--navy)", paddingBottom: "var(--s2)" }}>
          {/* Breadcrumb above hero */}
          <div className="wrap">
            <nav className="cat-hero-breadcrumb" style={{ padding: "var(--s4) 0 var(--s3)" }}>
              <Link href={`/${lang}/`}>{t("nav.tagline")}</Link>
              <span>›</span>
              <Link href={`/${lang}/yojana`}>{t("nav.all_schemes")}</Link>
              <span>›</span>
              <span style={{ color: "#fff", fontWeight: 700 }}>{t(`cat.${activeCategory}`)}</span>
            </nav>
          </div>
          {/* Full-bleed hero */}
          <div className="wrap" style={{ paddingBottom: "var(--s6)" }}>
            <div className="cat-hero">
              <div className="cat-hero-img-container">
                <Image
                  src={`/scheme-images/cat-${activeCategory}.png`}
                  alt=""
                  fill
                  priority
                  sizes="100vw"
                  className="cat-hero-img"
                  aria-hidden="true"
                />
              </div>
              <div className="cat-hero-overlay" />
              <div className="cat-hero-content">
                <h1 className="cat-hero-title">{t(`cat.${activeCategory}`)}</h1>
                <p className="cat-hero-desc">
                  {total.toLocaleString()} योजनाएं
                  {sp.q && ` — "${sp.q}" के लिए परिणाम`}
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div style={{ background: "var(--navy)", padding: "var(--s8) 0 var(--s6)" }}>
          <div className="wrap">
            <nav className="breadcrumb" style={{ marginBottom: "var(--s4)" }}>
              <Link href={`/${lang}/`} style={{ color: "rgba(255,255,255,.5)" }}>{t("nav.tagline")}</Link>
              <span className="sep" style={{ color: "rgba(255,255,255,.2)" }}>›</span>
              <span style={{ color: "rgba(255,255,255,.8)" }}>{t("nav.all_schemes")}</span>
            </nav>
            <h1 style={{ color: "#fff", marginBottom: "var(--s2)" }}>{t("nav.all_schemes")}</h1>
            <p style={{ color: "rgba(255,255,255,.6)", fontSize: 14 }}>
              {total.toLocaleString()} योजनाएं
              {sp.q && ` — "${sp.q}" के लिए परिणाम`}
            </p>
          </div>
        </div>
      )}

      <div className="wrap" style={{ paddingTop: "var(--s6)", paddingBottom: "var(--s10)" }}>

        {/* Mobile search — visible only on mobile (sidebar hidden on mobile) */}
        <div style={{ marginBottom: "var(--s3)" }} className="mobile-search-wrap">
          <Suspense fallback={null}>
            <MobileSearch lang={lang} />
          </Suspense>
        </div>

        {/* Filter pills — mobile horizontal scroll */}
        <div className="filter-bar" role="navigation" aria-label="Category filters">
          <Link href={`/${lang}/yojana`}
            className={`pill ${!activeCategory ? "active" : ""}`}>
            सभी (2,754)
          </Link>
          {CATEGORIES.map((c) => (
            <Link key={c.slug} href={`/${lang}/yojana?category=${c.slug}`}
              className={`pill ${activeCategory === c.slug ? "active" : ""}`}>
              {t(c.key)} ({c.count})
            </Link>
          ))}
        </div>

        <div className="browse-layout">

          {/* Sidebar filters — hidden on mobile, shown on desktop */}
          <div className="browse-sidebar-hidden" style={{ flexDirection: "column" }}>
            <Suspense fallback={<div style={{ height: 200 }} />}>
              <BrowseFilters lang={lang} currentCategory={activeCategory} currentLevel={sp.level ?? ""} />
            </Suspense>
          </div>

          {/* Schemes grid */}
          <div>
            {sp.q && (
              <div style={{ marginBottom: "var(--s4)", fontSize: 14, color: "var(--ink-2)" }}>
                <strong>&ldquo;{sp.q}&rdquo;</strong> के लिए {total} परिणाम
                <Link href={`/${lang}/yojana`} style={{ marginLeft: "var(--s3)", fontSize: 12, color: "var(--saffron-deep)" }}>
                  फ़िल्टर हटाएं ✕
                </Link>
              </div>
            )}

            {schemes.length === 0 ? (
              <div style={{ textAlign: "center", padding: "var(--s16) 0" }}>
                <div style={{ fontSize: 40, marginBottom: "var(--s4)" }}>🔍</div>
                <h3>कोई योजना नहीं मिली</h3>
                <p style={{ color: "var(--ink-3)", marginBottom: "var(--s5)" }}>
                  फ़िल्टर बदलें या सभी योजनाएं देखें
                </p>
                <Link href={`/${lang}/yojana`} className="btn btn-primary">
                  सभी योजनाएं देखें
                </Link>
              </div>
            ) : (
              <>
                <div className="scheme-grid">
                  {schemes.map((s) => (
                    <SchemeCard key={s.slug} scheme={s} lang={lang} t={t} />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="pagination">
                    {page > 1 && (
                      <Link href={`/${lang}/yojana?${new URLSearchParams({ ...sp, page: String(page - 1) })}`}
                        className="page-btn">‹</Link>
                    )}
                    {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                      const p = i + 1;
                      return (
                        <Link key={p}
                          href={`/${lang}/yojana?${new URLSearchParams({ ...sp, page: String(p) })}`}
                          className={`page-btn ${p === page ? "active" : ""}`}>
                          {p}
                        </Link>
                      );
                    })}
                    {page < totalPages && (
                      <Link href={`/${lang}/yojana?${new URLSearchParams({ ...sp, page: String(page + 1) })}`}
                        className="page-btn">›</Link>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
