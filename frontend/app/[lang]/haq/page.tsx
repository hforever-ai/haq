import type { Metadata } from "next";
import Link from "next/link";
import { makeT } from "@/lib/i18n";
import RightsClient from "@/components/rights/RightsClient";

interface Props {
  params: Promise<{ lang: string }>;
  searchParams: Promise<{ category?: string; q?: string }>;
}

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8097";

interface RightsArticle {
  id: number;
  slug: string;
  title_hi: string;
  title_en: string;
  category: string;
  summary_hi: string;
  keywords: string[];
}

async function getRights(category?: string, q?: string): Promise<RightsArticle[]> {
  try {
    const qs = new URLSearchParams();
    if (category) qs.set("category", category);
    if (q) qs.set("q", q);
    const res = await fetch(`${API}/api/rights?${qs}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.articles ?? [];
  } catch {
    return [];
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang } = await params;
  const t = makeT(lang);
  return {
    title: `${t("nav.your_rights")} — Aarambha Haq`,
    description: "भारत के संवैधानिक और कानूनी अधिकार — महिला हक, घरेलू हिंसा, पेंशन, कानूनी सहायता",
  };
}

const CATEGORIES = [
  { slug: "mahila-haq",     label: "महिला हक",        icon: "👩" },
  { slug: "gharelu-hinsa",  label: "घरेलू हिंसा",      icon: "🛡️" },
  { slug: "prasuti",        label: "प्रसूति अधिकार",   icon: "🤱" },
  { slug: "talak",          label: "तलाक / परिवार",    icon: "⚖️" },
  { slug: "sampatti",       label: "संपत्ति अधिकार",   icon: "🏠" },
  { slug: "pension",        label: "पेंशन",             icon: "👴" },
  { slug: "legal-aid",      label: "कानूनी सहायता",    icon: "⚖️" },
  { slug: "shiksha-rozgar", label: "शिक्षा / रोज़गार",  icon: "📚" },
];

const CAT_MAP = Object.fromEntries(CATEGORIES.map(c => [c.slug, c]));

export default async function RightsPage({ params, searchParams }: Props) {
  const { lang } = await params;
  const sp = await searchParams;
  const t = makeT(lang);

  const activeCategory = sp.category ?? "";
  const activeQ = sp.q ?? "";
  const articles = await getRights(activeCategory || undefined, activeQ || undefined);

  const grouped: Record<string, RightsArticle[]> = {};
  for (const a of articles) {
    (grouped[a.category] ??= []).push(a);
  }

  return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>

      {/* Header */}
      <div style={{ background: "var(--navy)", padding: "var(--s8) 0 var(--s6)" }}>
        <div className="wrap">
          <nav className="breadcrumb" style={{ marginBottom: "var(--s4)" }}>
            <Link href={`/${lang}/`} style={{ color: "rgba(255,255,255,.5)" }}>होम</Link>
            <span className="sep" style={{ color: "rgba(255,255,255,.2)" }}>›</span>
            <span style={{ color: "rgba(255,255,255,.8)" }}>आपके अधिकार</span>
          </nav>
          <h1 style={{ color: "#fff", marginBottom: "var(--s2)" }}>आपके अधिकार</h1>
          <p style={{ color: "rgba(255,255,255,.6)", fontSize: 14 }}>
            भारत के संविधान और कानूनों के तहत आपके मौलिक और कानूनी अधिकार
          </p>
        </div>
      </div>

      <div className="wrap" style={{ paddingTop: "var(--s6)", paddingBottom: "var(--s10)" }}>

        {/* Category pills */}
        <div className="filter-bar" style={{ marginBottom: "var(--s5)" }}>
          <Link href={`/${lang}/haq`}
            className={`pill ${!activeCategory ? "active" : ""}`}>
            सभी अधिकार
          </Link>
          {CATEGORIES.map(c => (
            <Link key={c.slug} href={`/${lang}/haq?category=${c.slug}`}
              className={`pill ${activeCategory === c.slug ? "active" : ""}`}>
              {c.icon} {c.label}
            </Link>
          ))}
        </div>

        {/* Search box (client component) */}
        <RightsClient lang={lang} initialQ={activeQ} activeCategory={activeCategory} />

        {/* Results */}
        {activeCategory || activeQ ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--s3)" }}>
            {articles.length === 0 ? (
              <div style={{ textAlign: "center", padding: "var(--s16) 0" }}>
                <div style={{ fontSize: 40, marginBottom: "var(--s4)" }}>🔍</div>
                <h3>कोई अधिकार नहीं मिला</h3>
                <Link href={`/${lang}/haq`} className="btn btn-primary" style={{ marginTop: "var(--s4)" }}>
                  सभी अधिकार देखें
                </Link>
              </div>
            ) : (
              articles.map(a => <RightsCard key={a.slug} article={a} />)
            )}
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--s8)" }}>
            {CATEGORIES.filter(c => grouped[c.slug]?.length).map(cat => (
              <div key={cat.slug}>
                <div style={{
                  display: "flex", alignItems: "center", gap: "var(--s3)",
                  marginBottom: "var(--s4)",
                }}>
                  <span style={{ fontSize: 22 }}>{cat.icon}</span>
                  <h2 style={{ fontSize: 20, fontWeight: 800, color: "var(--navy)" }}>
                    {cat.label}
                  </h2>
                  <Link href={`/${lang}/haq?category=${cat.slug}`}
                    style={{ fontSize: 12, color: "var(--saffron-deep)", marginLeft: "auto" }}>
                    सभी देखें →
                  </Link>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--s3)" }}>
                  {grouped[cat.slug].map(a => (
                    <RightsCard key={a.slug} article={a} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Helplines */}
        <div className="tips-box" style={{ marginTop: "var(--s10)" }}>
          <h4>📞 आपातकालीन हेल्पलाइन</h4>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
            gap: "var(--s3)", marginTop: "var(--s3)",
          }}>
            {[
              { label: "पुलिस", num: "112" },
              { label: "महिला हेल्पलाइन", num: "181" },
              { label: "कानूनी सहायता (NALSA)", num: "15100" },
              { label: "चाइल्ड हेल्पलाइन", num: "1098" },
              { label: "एम्बुलेंस", num: "108" },
              { label: "साइबर क्राइम", num: "1930" },
            ].map(h => (
              <a key={h.label} href={`tel:${h.num}`} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "10px var(--s3)", borderRadius: "var(--r-sm)",
                background: "rgba(255,153,51,.06)", border: "1px solid rgba(255,153,51,.2)",
                textDecoration: "none",
              }}>
                <span style={{ fontSize: 13, color: "var(--ink)", fontWeight: 600 }}>{h.label}</span>
                <span style={{ fontSize: 15, fontWeight: 900, color: "var(--saffron-deep)" }}>{h.num}</span>
              </a>
            ))}
          </div>
        </div>

        {/* CTA to wizard */}
        <div style={{
          marginTop: "var(--s8)", padding: "var(--s6)", borderRadius: "var(--r-lg)",
          background: "var(--navy)", textAlign: "center",
        }}>
          <h3 style={{ color: "#fff", marginBottom: "var(--s2)" }}>अपनी पात्र योजनाएं जानें</h3>
          <p style={{ color: "rgba(255,255,255,.6)", fontSize: 14, marginBottom: "var(--s5)" }}>
            5 सवालों में जानें आप कौन-कौन सी सरकारी योजनाओं के लिए पात्र हैं
          </p>
          <Link href={`/${lang}/check`} className="btn btn-primary">पात्रता जांचें →</Link>
        </div>
      </div>
    </div>
  );
}

async function getArticleDetail(slug: string): Promise<string | null> {
  try {
    const res = await fetch(`${API}/api/rights/${slug}`, { next: { revalidate: 86400 } });
    if (!res.ok) return null;
    return (await res.json()).detail_hi ?? null;
  } catch {
    return null;
  }
}

async function RightsCard({ article }: { article: RightsArticle }) {
  const detail = await getArticleDetail(article.slug);
  const cat = CAT_MAP[article.category];

  return (
    <div style={{
      background: "#fff", borderRadius: "var(--r-lg)",
      border: "1.5px solid var(--line)",
      boxShadow: "0 2px 8px rgba(11,31,77,.05)",
      overflow: "hidden",
    }}>
      <div style={{ padding: "var(--s5)" }}>
        {cat && (
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 4,
            marginBottom: "var(--s2)",
            fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".06em",
            color: "var(--saffron-deep)", background: "rgba(255,153,51,.1)",
            padding: "3px 8px", borderRadius: 6,
          }}>
            {cat.icon} {cat.label}
          </div>
        )}
        <h3 style={{ fontSize: 17, fontWeight: 800, color: "var(--navy)", marginBottom: "var(--s2)", lineHeight: 1.3 }}>
          {article.title_hi}
        </h3>
        <p style={{ fontSize: 14, color: "var(--ink-2)", lineHeight: 1.65, margin: 0 }}>
          {article.summary_hi}
        </p>
      </div>

      {detail && (
        <details style={{ borderTop: "1px solid var(--line)" }}>
          <summary style={{
            padding: "var(--s3) var(--s5)", cursor: "pointer",
            fontSize: 13, fontWeight: 700, color: "var(--saffron-deep)",
            listStyle: "none", display: "flex", alignItems: "center", justifyContent: "space-between",
            userSelect: "none",
          }}>
            <span>पूरी जानकारी देखें</span>
            <span style={{ fontSize: 16 }}>▾</span>
          </summary>
          <RightsDetailBody html={detail} />
        </details>
      )}
    </div>
  );
}

function RightsDetailBody({ html }: { html: string }) {
  /* detail_hi is seeded from scripts/seed_rights.py — internal content, not user input */
  return (
    <div
      className="rights-detail"
      style={{ padding: "var(--s4) var(--s5)", borderTop: "1px solid var(--line)" }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
