import type { Metadata } from "next";
import Link from "next/link";
import { makeT } from "@/lib/i18n";
import { getSchemes } from "@/lib/api";
import SchemeCard from "@/components/scheme/SchemeCard";

interface Props {
  params: Promise<{ lang: string; state: string }>;
}

// Slug → display name
function stateDisplayName(slug: string): string {
  return slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

// Reverse: display name → API state value (title case)
function stateApiValue(slug: string): string {
  return stateDisplayName(slug);
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang, state } = await params;
  const t = makeT(lang);
  const name = stateDisplayName(state);
  return {
    title: `${name} सरकारी योजनाएं — Aarambha Haq`,
    description: `${name} राज्य की सभी सरकारी कल्याण योजनाएं। पात्रता जाँचें, ऑनलाइन आवेदन करें।`,
    alternates: {
      canonical: `https://haq.aarambhax.in/${lang}/state/${state}`,
    },
  };
}

const CATEGORIES = [
  { slug: "mahila",       label: "महिला",       count: 381 },
  { slug: "student",      label: "छात्र",        count: 748 },
  { slug: "farmer",       label: "किसान",        count: 400 },
  { slug: "employment",   label: "रोजगार",       count: 459 },
  { slug: "disability",   label: "दिव्यांग",     count: 289 },
  { slug: "pension",      label: "पेंशन",        count: 259 },
  { slug: "health",       label: "स्वास्थ्य",    count: 184 },
  { slug: "housing",      label: "आवास",         count: 69  },
];

export default async function StateHubPage({ params }: Props) {
  const { lang, state } = await params;
  const t = makeT(lang);
  const stateName = stateDisplayName(state);
  const apiState  = stateApiValue(state);

  // Fetch state-specific schemes + central schemes for this state
  const [stateRes, centralRes] = await Promise.all([
    getSchemes({ state: apiState, level: "State", size: 24 }),
    getSchemes({ state: apiState, level: "Central", size: 12 }),
  ]);

  const total = stateRes.total + centralRes.total;

  return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>

      {/* Hero */}
      <div className="page-hero">
        <div className="wrap">
          <nav className="breadcrumb" style={{ marginBottom: "var(--s3)" }}>
            <Link href={`/${lang}/`} style={{ color: "rgba(255,255,255,.5)" }}>होम</Link>
            <span className="sep" style={{ color: "rgba(255,255,255,.2)" }}>›</span>
            <Link href={`/${lang}/yojana`} style={{ color: "rgba(255,255,255,.5)" }}>{t("nav.all_schemes")}</Link>
            <span className="sep" style={{ color: "rgba(255,255,255,.2)" }}>›</span>
            <span style={{ color: "rgba(255,255,255,.8)" }}>{stateName}</span>
          </nav>

          <div className="hero-eyebrow">राज्य योजनाएं</div>
          <h1>{stateName} — सरकारी योजनाएं</h1>
          <p className="tagline">
            {stateName} राज्य की {total.toLocaleString()}+ कल्याण योजनाएं।
            केंद्र और राज्य सरकार दोनों की योजनाएं एक जगह।
          </p>

          <div className="hero-actions">
            <Link href={`/${lang}/check`} className="btn btn-primary btn-lg">
              अपनी पात्रता जाँचें
            </Link>
            <Link href={`/${lang}/yojana?state=${encodeURIComponent(apiState)}`}
              className="btn btn-lg"
              style={{ color: "rgba(255,255,255,.75)", border: "1.5px solid rgba(255,255,255,.2)", background: "transparent" }}>
              सभी {stateName} योजनाएं
            </Link>
          </div>
        </div>
      </div>

      <div className="wrap" style={{ paddingTop: "var(--s8)", paddingBottom: "var(--s10)" }}>

        {/* Stats bar */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "var(--s3)",
          marginBottom: "var(--s8)",
        }}>
          {[
            { label: "कुल योजनाएं", value: total.toLocaleString(), color: "var(--saffron-deep)" },
            { label: "राज्य योजनाएं", value: stateRes.total.toLocaleString(), color: "var(--navy)" },
            { label: "केंद्रीय योजनाएं", value: centralRes.total.toLocaleString(), color: "var(--green-deep)" },
          ].map((s) => (
            <div key={s.label} style={{
              background: "var(--surface)", border: "1px solid var(--line)",
              borderRadius: "var(--r-lg)", padding: "var(--s4) var(--s5)", textAlign: "center",
            }}>
              <div style={{ fontSize: 28, fontWeight: 900, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 12, color: "var(--ink-3)", marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Category quick links */}
        <h2 style={{ marginBottom: "var(--s4)" }}>श्रेणी के अनुसार खोजें</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--s2)", marginBottom: "var(--s8)" }}>
          {CATEGORIES.map((c) => (
            <Link
              key={c.slug}
              href={`/${lang}/yojana?category=${c.slug}&state=${encodeURIComponent(apiState)}`}
              className="pill"
            >
              {c.label}
            </Link>
          ))}
        </div>

        {/* State schemes */}
        {stateRes.schemes.length > 0 && (
          <section style={{ marginBottom: "var(--s10)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--s5)" }}>
              <h2>{stateName} राज्य योजनाएं</h2>
              {stateRes.total > 24 && (
                <Link href={`/${lang}/yojana?state=${encodeURIComponent(apiState)}&level=State`}
                  style={{ fontSize: 13, color: "var(--saffron-deep)", fontWeight: 600 }}>
                  सभी {stateRes.total} देखें →
                </Link>
              )}
            </div>
            <div className="scheme-grid">
              {stateRes.schemes.map((s) => (
                <SchemeCard key={s.slug} scheme={s} lang={lang} t={t} />
              ))}
            </div>
          </section>
        )}

        {/* Central schemes */}
        {centralRes.schemes.length > 0 && (
          <section style={{ marginBottom: "var(--s10)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--s5)" }}>
              <h2>केंद्रीय योजनाएं ({stateName} में लागू)</h2>
              {centralRes.total > 12 && (
                <Link href={`/${lang}/yojana?level=Central`}
                  style={{ fontSize: 13, color: "var(--saffron-deep)", fontWeight: 600 }}>
                  सभी केंद्रीय योजनाएं →
                </Link>
              )}
            </div>
            <div className="scheme-grid">
              {centralRes.schemes.map((s) => (
                <SchemeCard key={s.slug} scheme={s} lang={lang} t={t} />
              ))}
            </div>
          </section>
        )}

        {/* No schemes */}
        {total === 0 && (
          <div style={{ textAlign: "center", padding: "var(--s16) 0" }}>
            <div style={{ fontSize: 40, marginBottom: "var(--s4)" }}>🔍</div>
            <h3>{stateName} के लिए कोई राज्य-विशेष योजना नहीं मिली</h3>
            <p style={{ color: "var(--ink-3)", marginBottom: "var(--s5)" }}>
              लेकिन केंद्र की सभी योजनाएं यहाँ लागू हैं
            </p>
            <Link href={`/${lang}/yojana`} className="btn btn-primary">
              सभी योजनाएं देखें
            </Link>
          </div>
        )}

        {/* Eligibility CTA */}
        <div className="cta-card">
          <div>
            <h3>{stateName} में आपके लिए कौन सी योजनाएं हैं?</h3>
            <p>2 मिनट में जानें — आय, आयु, जाति के आधार पर मिलान</p>
          </div>
          <Link href={`/${lang}/check`} className="btn btn-primary">
            {t("hero.cta")}
          </Link>
        </div>
      </div>
    </div>
  );
}
