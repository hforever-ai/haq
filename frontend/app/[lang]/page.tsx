import type { Metadata } from "next";
import Link from "next/link";
import { makeT, VALID_LANGS, getLanguages } from "@/lib/i18n";
import { getSchemes } from "@/lib/api";
import { CAT_ICONS, CAT_LOTTIE, STEP_ICONS } from "@/lib/icons";
import LottiePlayer from "@/components/ui/LottiePlayer";
import HeroCarousel from "@/components/ui/HeroCarousel";

export const dynamic = "force-dynamic";
import SchemeCard from "@/components/scheme/SchemeCard";
import HeroSearch from "@/components/ui/HeroSearch";

interface Props {
  params: Promise<{ lang: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang } = await params;
  const t = makeT(lang);
  return {
    title: t("hero.headline"),
    description: `${t("hero.sub")} 2,754+ सरकारी योजनाएं — 22 भारतीय भाषाओं में।`,
    openGraph: {
      title: `${t("hero.headline")} — Aarambha Haq`,
      description: t("hero.sub"),
    },
  };
}

const CATEGORIES = [
  { slug: "mahila",       key: "cat.women",       count: 381,  color: "#FF9933" },
  { slug: "student",      key: "cat.student",      count: 748,  color: "#0B1F4D" },
  { slug: "farmer",       key: "cat.farmer",       count: 400,  color: "#138808" },
  { slug: "employment",   key: "cat.employment",   count: 459,  color: "#0B1F4D" },
  { slug: "disability",   key: "cat.disability",   count: 289,  color: "#6B48D0" },
  { slug: "pension",      key: "cat.pension",      count: 259,  color: "#C87941" },
  { slug: "health",       key: "cat.health",       count: 184,  color: "#E74C3C" },
  { slug: "child",        key: "cat.child",        count: 182,  color: "#FF9933" },
  { slug: "tribal",       key: "cat.tribal",       count: 157,  color: "#138808" },
  { slug: "bpl",          key: "cat.bpl",          count: 141,  color: "#5B6678" },
  { slug: "entrepreneur", key: "cat.entrepreneur", count: 121,  color: "#0B1F4D" },
  { slug: "minority",     key: "cat.minority",     count: 87,   color: "#2980B9" },
  { slug: "housing",      key: "cat.housing",      count: 69,   color: "#C87941" },
  { slug: "maternity",    key: "cat.maternity",    count: 40,   color: "#E056A0" },
  { slug: "elderly",      key: "cat.elderly",      count: 24,   color: "#5B6678" },
];

export default async function HomePage({ params }: Props) {
  const { lang } = await params;
  if (!VALID_LANGS.has(lang)) return null;

  const t = makeT(lang);
  const { schemes: popular } = await getSchemes({ size: 6 });

  const carouselSlides = [
    { slug: "mahila",     badge: t("cat.women"),      title: t("hero.headline"), desc: t("hero.sub"), ctaLabel: t("hero.cta"), ctaHref: `/${lang}/yojana?category=mahila` },
    { slug: "farmer",     badge: t("cat.farmer"),     title: t("hero.headline"), desc: t("hero.sub"), ctaLabel: t("hero.cta"), ctaHref: `/${lang}/yojana?category=farmer` },
    { slug: "student",    badge: t("cat.student"),    title: t("hero.headline"), desc: t("hero.sub"), ctaLabel: t("hero.cta"), ctaHref: `/${lang}/yojana?category=student` },
    { slug: "employment", badge: t("cat.employment"), title: t("hero.headline"), desc: t("hero.sub"), ctaLabel: t("hero.cta"), ctaHref: `/${lang}/yojana?category=employment` },
    { slug: "health",     badge: t("cat.health"),     title: t("hero.headline"), desc: t("hero.sub"), ctaLabel: t("hero.cta"), ctaHref: `/${lang}/yojana?category=health` },
  ];

  return (
    <>
      {/* ── Hero Carousel ── */}
      <HeroCarousel slides={carouselSlides} />

      {/* ── Category Grid ── */}
      <section className="section" aria-labelledby="cat-heading">
        <div className="wrap">
          <div className="sh">
            <div>
              <div className="section-label">{t("hero.badge")}</div>
              <h2 id="cat-heading">{t("nav.all_schemes")}</h2>
            </div>
            <Link href={`/${lang}/yojana`}>सभी 2,754 योजनाएं →</Link>
          </div>
          <div className="cat-grid">
            {CATEGORIES.map((c) => (
              <Link key={c.slug} href={`/${lang}/yojana/${c.slug}`} className="cat-tile"
                aria-label={`${t(c.key)} — ${c.count} योजनाएं`}
                style={{ "--cat-bg-image": `url('/scheme-images/cat-${c.slug}.png')` } as React.CSSProperties}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: `${c.color}18`, border: `1.5px solid ${c.color}35`,
                  display: "grid", placeItems: "center",
                  color: c.color, overflow: "hidden",
                }}>
                  {CAT_LOTTIE[c.slug]
                    ? <LottiePlayer src={CAT_LOTTIE[c.slug]} size={44} />
                    : CAT_ICONS[c.slug]}
                </div>
                <h4>{t(c.key)}</h4>
                <span className="cnt">{c.count}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section style={{ background: "var(--navy-tint)", padding: "var(--s12) 0" }}>
        <div className="wrap">
          <div className="section-label text-center">{t("how.title")}</div>
          <h2 className="text-center" style={{ marginBottom: "var(--s8)" }}>{t("how.title")}</h2>
          <div className="how-grid">
            {([
              { num: 1, icon: STEP_ICONS.form,  step: t("how.step1"), desc: "अपनी जानकारी भरें — लिंग, आयु, राज्य, आय" },
              { num: 2, icon: STEP_ICONS.match, step: t("how.step2"), desc: "AI आपके लिए उपयुक्त योजनाएं तुरंत खोजता है" },
              { num: 3, icon: STEP_ICONS.apply, step: t("how.step3"), desc: "सीधे सरकारी पोर्टल पर जाएं और आवेदन करें" },
            ] as const).map(({ num, icon, step, desc }) => (
              <div key={num} className="how-step">
                <div style={{
                  width: 56, height: 56, borderRadius: "50%",
                  background: "rgba(255,153,51,.12)",
                  border: "2px solid rgba(255,153,51,.25)",
                  display: "grid", placeItems: "center",
                  margin: "0 auto var(--s3)",
                  color: "var(--saffron-deep)",
                }}>
                  {icon}
                </div>
                <div className="how-num" style={{ position: "relative", top: -4, marginBottom: "var(--s2)" }}>{num}</div>
                <h4>{step}</h4>
                <p>{desc}</p>
              </div>
            ))}
          </div>
          <div className="text-center" style={{ marginTop: "var(--s8)" }}>
            <Link href={`/${lang}/check`} className="btn btn-primary btn-lg">{t("hero.cta")}</Link>
          </div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section style={{ background: "var(--navy)", padding: "var(--s8) 0" }}>
        <div className="wrap">
          <div className="stat-grid">
            {[
              { n: "2,754", label: t("trust.schemes_count") },
              { n: "22",    label: "अनुसूचित भाषाएं" },
              { n: "15",    label: "लाभार्थी श्रेणियां" },
            ].map(({ n, label }) => (
              <div key={n} className="stat-box"
                style={{ background: "rgba(255,255,255,.06)", borderColor: "rgba(255,255,255,.08)" }}>
                <div className="n">{n}</div>
                <div className="lbl" style={{ color: "rgba(255,255,255,.55)" }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Popular Schemes ── */}
      <section className="section" aria-labelledby="schemes-heading">
        <div className="wrap">
          <div className="sh">
            <div>
              <div className="section-label">{t("trust.govt_data")}</div>
              <h2 id="schemes-heading">{t("nav.all_schemes")}</h2>
            </div>
            <Link href={`/${lang}/yojana`}>सभी देखें →</Link>
          </div>
          <div className="scheme-grid">
            {popular.map((s) => (
              <SchemeCard key={s.slug} scheme={s} lang={lang} t={t} />
            ))}
          </div>
          <div className="text-center" style={{ marginTop: "var(--s8)" }}>
            <Link href={`/${lang}/yojana`} className="btn btn-outline btn-lg">
              2,754 योजनाएं देखें
            </Link>
          </div>
        </div>
      </section>

      {/* ── CTA strip ── */}
      <section style={{ background: "var(--saffron)", padding: "var(--s8) 0" }}>
        <div className="wrap" style={{
          display: "flex", alignItems: "center",
          justifyContent: "space-between", flexWrap: "wrap", gap: "var(--s5)",
        }}>
          <div>
            <h2 style={{ color: "var(--navy)", marginBottom: "var(--s2)" }}>{t("hero.cta")}</h2>
            <p style={{ color: "rgba(11,31,77,.7)", fontSize: 15, margin: 0 }}>{t("hero.sub")}</p>
          </div>
          <Link href={`/${lang}/check`} className="btn btn-navy btn-lg">{t("hero.cta")}</Link>
        </div>
      </section>
    </>
  );
}
