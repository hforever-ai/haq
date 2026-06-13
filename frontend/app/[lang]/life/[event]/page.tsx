import type { Metadata } from "next";
import Link from "next/link";
import { makeT } from "@/lib/i18n";
import { getSchemes } from "@/lib/api";
import SchemeCard from "@/components/scheme/SchemeCard";

interface Props {
  params: Promise<{ lang: string; event: string }>;
}

// Life event → category mapping + metadata
const LIFE_EVENT_META: Record<string, {
  label: string;
  desc: string;
  emoji: string;
  categories: string[];
  gender?: string;
  keywords: string;
}> = {
  farmer: {
    label: "किसान",
    desc: "कृषि, सिंचाई, फसल बीमा, KCC, PM-KISAN — किसानों के लिए सभी सरकारी योजनाएं",
    emoji: "🌾",
    categories: ["farmer"],
    keywords: "किसान योजना, PM-KISAN, कृषि बीमा, KCC",
  },
  student: {
    label: "छात्र / छात्रा",
    desc: "छात्रवृत्ति, शिक्षा ऋण, कोचिंग — विद्यार्थियों के लिए सरकारी मदद",
    emoji: "🎓",
    categories: ["student"],
    keywords: "छात्रवृत्ति, शिक्षा ऋण, National Merit Scholarship",
  },
  pregnant: {
    label: "गर्भवती महिला",
    desc: "प्रसूति लाभ, पोषण, अस्पताल — गर्भवती और नई माताओं के लिए योजनाएं",
    emoji: "🤱",
    categories: ["maternity", "mahila", "health"],
    keywords: "प्रसूति लाभ, PMMVY, JSY, आंगनवाड़ी",
  },
  widow: {
    label: "विधवा महिला",
    desc: "विधवा पेंशन, रोजगार, बच्चों की शिक्षा — एकल महिलाओं के लिए सहायता",
    emoji: "🙏",
    categories: ["mahila", "pension"],
    keywords: "विधवा पेंशन, एकल महिला योजना",
  },
  disabled: {
    label: "दिव्यांगजन",
    desc: "दिव्यांग पेंशन, उपकरण सहायता, शिक्षा — विकलांगजन के लिए सरकारी योजनाएं",
    emoji: "♿",
    categories: ["disability"],
    keywords: "दिव्यांग पेंशन, ADIP, सहायक उपकरण",
  },
  elderly: {
    label: "वृद्ध नागरिक",
    desc: "वृद्धावस्था पेंशन, स्वास्थ्य बीमा, NSAP — बुजुर्गों के लिए योजनाएं",
    emoji: "👴",
    categories: ["elderly", "pension"],
    keywords: "वृद्धावस्था पेंशन, NSAP, PMJAY",
  },
  child: {
    label: "बच्चे / बाल कल्याण",
    desc: "बाल पोषण, टीकाकरण, बाल श्रम उन्मूलन — बच्चों के लिए सरकारी कार्यक्रम",
    emoji: "👶",
    categories: ["child"],
    keywords: "आंगनवाड़ी, पोशण अभियान, MDM",
  },
  unemployed: {
    label: "बेरोजगार युवा",
    desc: "कौशल विकास, रोजगार गारंटी, स्वरोजगार ऋण — बेरोजगारों के लिए योजनाएं",
    emoji: "💼",
    categories: ["employment"],
    keywords: "MNREGA, PMKVY, Mudra Loan, रोजगार मेला",
  },
  minority: {
    label: "अल्पसंख्यक",
    desc: "अल्पसंख्यक छात्रवृत्ति, मदरसा, हुनर हाट — अल्पसंख्यक समुदाय के लिए",
    emoji: "🕌",
    categories: ["minority"],
    keywords: "अल्पसंख्यक छात्रवृत्ति, PM Vishwakarma",
  },
  shg: {
    label: "स्वयं सहायता समूह (SHG)",
    desc: "माइक्रो फाइनेंस, DAY-NRLM, PMEGP — महिला SHG के लिए योजनाएं",
    emoji: "👥",
    categories: ["mahila", "employment"],
    keywords: "SHG, NRLM, DAY-NULM, Mudra",
  },
  entrepreneur: {
    label: "उद्यमी / व्यवसायी",
    desc: "Mudra Loan, Startup India, PMEGP — नए व्यवसाय के लिए सरकारी सहायता",
    emoji: "💡",
    categories: ["entrepreneur"],
    keywords: "Mudra, PMEGP, Startup India, स्टैंडअप इंडिया",
  },
  housing: {
    label: "आवास / घर",
    desc: "PMAY, ग्रामीण आवास, शौचालय निर्माण — घर बनाने की सरकारी मदद",
    emoji: "🏠",
    categories: ["housing", "bpl"],
    keywords: "PMAY, ग्रामीण आवास, IAY",
  },
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang, event } = await params;
  const meta = LIFE_EVENT_META[event];
  if (!meta) return { title: "Life Events — Aarambha Haq" };
  return {
    title: `${meta.label} — सरकारी योजनाएं | Aarambha Haq`,
    description: meta.desc,
    keywords: meta.keywords,
    alternates: {
      canonical: `https://haq.aarambhax.in/${lang}/life/${event}`,
    },
  };
}

export default async function LifeEventPage({ params }: Props) {
  const { lang, event } = await params;
  const t = makeT(lang);
  const meta = LIFE_EVENT_META[event];

  if (!meta) {
    return (
      <div className="wrap" style={{ padding: "var(--s16) 0", textAlign: "center" }}>
        <h2>यह पेज उपलब्ध नहीं है</h2>
        <Link href={`/${lang}/yojana`} className="btn btn-primary">सभी योजनाएं देखें</Link>
      </div>
    );
  }

  // Fetch schemes for all relevant categories in parallel
  const categoryResults = await Promise.all(
    meta.categories.map((cat) => getSchemes({ category: cat, size: 12 }))
  );

  // Deduplicate schemes across categories by slug
  const seen = new Set<string>();
  const schemes = categoryResults
    .flatMap((r) => r.schemes)
    .filter((s) => {
      if (seen.has(s.slug)) return false;
      seen.add(s.slug);
      return true;
    })
    .slice(0, 24);

  const totalApprox = categoryResults.reduce((sum, r) => sum + r.total, 0);

  // Related life events (all except current)
  const related = Object.entries(LIFE_EVENT_META)
    .filter(([key]) => key !== event)
    .slice(0, 6);

  return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>

      {/* Hero */}
      <div className="page-hero">
        <div className="wrap">
          <nav className="breadcrumb" style={{ marginBottom: "var(--s3)" }}>
            <Link href={`/${lang}/`} style={{ color: "rgba(255,255,255,.5)" }}>होम</Link>
            <span className="sep" style={{ color: "rgba(255,255,255,.2)" }}>›</span>
            <span style={{ color: "rgba(255,255,255,.8)" }}>{meta.label}</span>
          </nav>

          <div className="hero-eyebrow">{meta.emoji} जीवन परिस्थिति</div>
          <h1>{meta.label} के लिए सरकारी योजनाएं</h1>
          <p className="tagline" style={{ maxWidth: 560 }}>{meta.desc}</p>

          <div style={{ display: "flex", gap: "var(--s2)", flexWrap: "wrap", marginBottom: "var(--s5)" }}>
            <span className="badge" style={{ background: "rgba(255,153,51,.2)", color: "#fff", fontSize: 13 }}>
              {totalApprox}+ योजनाएं
            </span>
            {meta.categories.map((c) => (
              <span key={c} className="badge badge-navy" style={{ fontSize: 12 }}>
                {t(`cat.${c}`)}
              </span>
            ))}
          </div>

          <div className="hero-actions">
            <Link href={`/${lang}/check`} className="btn btn-primary btn-lg">
              अपनी पात्रता जाँचें
            </Link>
          </div>
        </div>
      </div>

      <div className="wrap" style={{ paddingTop: "var(--s8)", paddingBottom: "var(--s10)" }}>

        {/* Key schemes */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--s5)" }}>
          <h2>{meta.label} के लिए प्रमुख योजनाएं</h2>
          <Link
            href={`/${lang}/yojana?category=${meta.categories[0]}`}
            style={{ fontSize: 13, color: "var(--saffron-deep)", fontWeight: 600 }}
          >
            सभी {totalApprox} देखें →
          </Link>
        </div>

        {schemes.length > 0 ? (
          <div className="scheme-grid" style={{ marginBottom: "var(--s10)" }}>
            {schemes.map((s) => (
              <SchemeCard key={s.slug} scheme={s} lang={lang} t={t} />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "var(--s10) 0", color: "var(--ink-3)" }}>
            <div style={{ fontSize: 32, marginBottom: "var(--s3)" }}>🔍</div>
            <p>योजनाएं लोड हो रही हैं...</p>
          </div>
        )}

        {/* Key schemes info card */}
        <div style={{
          background: "var(--navy-tint)",
          border: "1px solid rgba(11,31,77,.1)",
          borderRadius: "var(--r-lg)",
          padding: "var(--s6)",
          marginBottom: "var(--s10)",
        }}>
          <h3 style={{ color: "var(--navy)", marginBottom: "var(--s4)" }}>
            {meta.emoji} {meta.label} — आपके अधिकार
          </h3>
          <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--ink)", marginBottom: "var(--s4)" }}>
            {meta.desc} हर भारतीय नागरिक का अधिकार है कि वो सरकारी योजनाओं का लाभ उठाए।
            Aarambha Haq सभी 2,754+ योजनाओं की जानकारी एक जगह देता है — मुफ्त, बिना किसी एजेंट के।
          </p>
          <Link href={`/${lang}/check`} className="btn btn-primary">
            अभी पात्रता जाँचें
          </Link>
        </div>

        {/* Other life events */}
        <h2 style={{ marginBottom: "var(--s5)" }}>अन्य परिस्थितियाँ</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "var(--s3)" }}>
          {related.map(([key, m]) => (
            <Link
              key={key}
              href={`/${lang}/life/${key}`}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "var(--s3)",
                background: "var(--surface)",
                border: "1px solid var(--line)",
                borderRadius: "var(--r-md)",
                padding: "var(--s3) var(--s4)",
                textDecoration: "none",
                color: "var(--ink)",
                transition: "border-color 0.15s",
              }}
            >
              <span style={{ fontSize: 24 }}>{m.emoji}</span>
              <span style={{ fontSize: 14, fontWeight: 600 }}>{m.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
